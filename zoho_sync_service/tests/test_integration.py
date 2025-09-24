import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import json

# Add the parent directory to the path to import our modules
sys.path.append('/app')

from service import ZohoSyncService
from models import EmployeeRecord, CandidateDetails


class TestZohoSyncIntegration:
    @pytest.fixture
    async def sync_service(self):
        """Create a sync service instance for testing"""
        with patch.dict(os.environ, {
            'ZOHO_ACCESS_TOKEN': 'test_token',
            'GOOGLE_API_KEY': 'test_google_key',
            'MONGO_URL': 'mongodb://test:test@localhost:27017/test_db',
            'DB_NAME': 'test_db',
            'SYNC_INTERVAL': '5'
        }):
            service = ZohoSyncService()
            
            # Mock the database connection
            service.client = AsyncMock()
            service.db = AsyncMock()
            service.employees_collection = AsyncMock()
            service.candidates_collection = AsyncMock()
            service.sync_status_collection = AsyncMock()
            
            # Mock the LLM
            service.llm = AsyncMock()
            
            yield service

    @pytest.mark.asyncio
    async def test_full_sync_flow_success(self, sync_service):
        """Test successful end-to-end sync flow"""
        # Mock Zoho API response
        mock_employees_data = [
            {
                "Employeeid": "EMP001",
                "Firstname": "John",
                "Lastname": "Doe",
                "Designation": "Software Engineer",
                "Department": "Engineering",
                "Emailid": "john.doe@example.com",
                "Mobile": "+1234567890"
            },
            {
                "Employeeid": "EMP002",
                "Firstname": "Jane",
                "Lastname": "Smith",
                "Designation": "Product Manager",
                "Department": "Product",
                "Emailid": "jane.smith@example.com",
                "Mobile": "+1234567891"
            }
        ]
        
        # Mock LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.content = json.dumps({
            "profile": "Experienced software professional",
            "skills": "Python, FastAPI, MongoDB",
            "experience": "5+ years in software development",
            "summary": "Skilled engineer with expertise in backend development"
        })
        
        with patch('requests.get') as mock_get:
            # Mock Zoho API call
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "response": {"result": mock_employees_data}
            }
            mock_get.return_value = mock_response
            
            # Mock LLM call
            sync_service.llm.invoke = AsyncMock(return_value=mock_llm_response)
            
            # Mock database operations
            sync_service.employees_collection.replace_one = AsyncMock(
                return_value=MagicMock(upserted_id="new_id")
            )
            sync_service.candidates_collection.find_one = AsyncMock(return_value=None)
            sync_service.candidates_collection.insert_one = AsyncMock(
                return_value=MagicMock(inserted_id="candidate_id")
            )
            sync_service.sync_status_collection.replace_one = AsyncMock()
            
            # Run sync
            result = await sync_service.run_sync()
            
            # Verify results
            assert result["employees_fetched"] == 2
            assert result["employees_processed"] == 2
            assert result["candidates_created"] == 2
            assert len(result["errors"]) == 0
            
            # Verify database operations were called
            assert sync_service.employees_collection.replace_one.call_count == 2
            assert sync_service.candidates_collection.insert_one.call_count == 2
            assert sync_service.sync_status_collection.replace_one.call_count == 1

    @pytest.mark.asyncio
    async def test_sync_with_existing_candidates(self, sync_service):
        """Test sync when candidates already exist (should skip)"""
        mock_employees_data = [
            {
                "Employeeid": "EMP001",
                "Firstname": "John",
                "Lastname": "Doe",
                "Designation": "Software Engineer",
                "Department": "Engineering",
                "Emailid": "john.doe@example.com"
            }
        ]
        
        with patch('requests.get') as mock_get:
            # Mock Zoho API call
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "response": {"result": mock_employees_data}
            }
            mock_get.return_value = mock_response
            
            # Mock database operations - existing candidate
            sync_service.employees_collection.replace_one = AsyncMock(
                return_value=MagicMock(upserted_id=None)  # Updated existing
            )
            sync_service.candidates_collection.find_one = AsyncMock(
                return_value={"employee_id": "EMP001"}  # Existing candidate
            )
            sync_service.sync_status_collection.replace_one = AsyncMock()
            
            # Run sync
            result = await sync_service.run_sync()
            
            # Verify results
            assert result["employees_fetched"] == 1
            assert result["employees_processed"] == 1
            assert result["candidates_created"] == 0  # Should be 0 since candidate exists
            
            # Verify candidate was not inserted
            sync_service.candidates_collection.insert_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_with_zoho_api_error(self, sync_service):
        """Test sync when Zoho API fails"""
        with patch('requests.get') as mock_get:
            # Mock Zoho API failure
            mock_get.side_effect = Exception("Zoho API connection failed")
            
            # Mock database operations
            sync_service.sync_status_collection.replace_one = AsyncMock()
            
            # Run sync
            result = await sync_service.run_sync()
            
            # Verify error handling
            assert result["employees_fetched"] == 0
            assert result["employees_processed"] == 0
            assert result["candidates_created"] == 0
            assert len(result["errors"]) > 0
            assert "Zoho API connection failed" in str(result["errors"])

    @pytest.mark.asyncio
    async def test_sync_with_llm_error(self, sync_service):
        """Test sync when LLM generation fails"""
        mock_employees_data = [
            {
                "Employeeid": "EMP001",
                "Firstname": "John",
                "Lastname": "Doe",
                "Designation": "Software Engineer",
                "Department": "Engineering"
            }
        ]
        
        with patch('requests.get') as mock_get:
            # Mock Zoho API call
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "response": {"result": mock_employees_data}
            }
            mock_get.return_value = mock_response
            
            # Mock LLM failure
            sync_service.llm.invoke = AsyncMock(side_effect=Exception("LLM generation failed"))
            
            # Mock database operations
            sync_service.employees_collection.replace_one = AsyncMock(
                return_value=MagicMock(upserted_id="new_id")
            )
            sync_service.candidates_collection.find_one = AsyncMock(return_value=None)
            sync_service.candidates_collection.insert_one = AsyncMock(
                return_value=MagicMock(inserted_id="candidate_id")
            )
            sync_service.sync_status_collection.replace_one = AsyncMock()
            
            # Run sync
            result = await sync_service.run_sync()
            
            # Verify fallback candidate creation
            assert result["employees_processed"] == 1
            assert result["candidates_created"] == 1  # Should still create with fallback
            
            # Verify candidate was inserted (with fallback data)
            sync_service.candidates_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_employee_limit_respected(self, sync_service):
        """Test that only 50 employees are processed per sync"""
        # Create 60 mock employees (more than the 50 limit)
        mock_employees_data = []
        for i in range(60):
            mock_employees_data.append({
                "Employeeid": f"EMP{i:03d}",
                "Firstname": f"Employee{i}",
                "Lastname": "Test",
                "Designation": "Test Role",
                "Department": "Test Dept"
            })
        
        with patch('requests.get') as mock_get:
            # Mock Zoho API call - should be called with limit=50
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "response": {"result": mock_employees_data[:50]}  # API respects limit
            }
            mock_get.return_value = mock_response
            
            # Mock database operations
            sync_service.employees_collection.replace_one = AsyncMock(
                return_value=MagicMock(upserted_id="new_id")
            )
            sync_service.candidates_collection.find_one = AsyncMock(return_value=None)
            sync_service.candidates_collection.insert_one = AsyncMock(
                return_value=MagicMock(inserted_id="candidate_id")
            )
            sync_service.sync_status_collection.replace_one = AsyncMock()
            
            # Mock LLM
            mock_llm_response = MagicMock()
            mock_llm_response.content = json.dumps({
                "profile": "Test profile",
                "skills": "Test skills",
                "experience": "Test experience",
                "summary": "Test summary"
            })
            sync_service.llm.invoke = AsyncMock(return_value=mock_llm_response)
            
            # Run sync
            result = await sync_service.run_sync()
            
            # Verify limit was respected
            assert result["employees_fetched"] == 50
            assert result["employees_processed"] == 50
            
            # Verify API was called with limit parameter
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["limit"] == 50