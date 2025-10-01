import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from datetime import datetime

from src.models.candidate import CandidateCreate, CandidateUpdate, CandidateLLMCreate, Candidate
from src.services.candidate_service import CandidateService


class TestCandidateModel:
    """Test candidate model with location and experience fields"""
    
    def test_candidate_create_with_location_and_experience(self):
        """Test CandidateCreate model accepts location and experience"""
        candidate_data = CandidateCreate(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            skills=["Python", "JavaScript"],
            location="San Francisco, CA",
            experience="5 years"
        )
        
        assert candidate_data.name == "Test User"
        assert candidate_data.location == "San Francisco, CA"
        assert candidate_data.experience == "5 years"
        assert candidate_data.skills == ["Python", "JavaScript"]
    
    def test_candidate_create_without_location_and_experience(self):
        """Test CandidateCreate model works without location and experience"""
        candidate_data = CandidateCreate(
            name="Test User",
            email="test@example.com"
        )
        
        assert candidate_data.name == "Test User"
        assert candidate_data.location is None
        assert candidate_data.experience is None
    
    def test_candidate_update_with_location(self):
        """Test CandidateUpdate model accepts location"""
        update_data = CandidateUpdate(
            location="New York, NY"
        )
        
        assert update_data.location == "New York, NY"
    
    def test_candidate_llm_create_with_location(self):
        """Test CandidateLLMCreate model accepts location"""
        llm_data = CandidateLLMCreate(
            name="LLM Extracted User",
            location="Remote",
            experience="3+ years"
        )
        
        assert llm_data.name == "LLM Extracted User"
        assert llm_data.location == "Remote"
        assert llm_data.experience == "3+ years"


@pytest.mark.asyncio
class TestCandidateService:
    """Test candidate service with location and experience fields"""
    
    async def test_create_candidate_with_location_and_experience(self):
        """Test creating candidate with location and experience"""
        service = CandidateService()
        
        # Mock the database collection
        with patch.object(service, 'collection') as mock_collection:
            mock_collection.insert_one = AsyncMock(return_value=type('Result', (), {'inserted_id': ObjectId()})())
            
            candidate_data = CandidateCreate(
                name="Test User",
                email="test@example.com",
                location="Austin, TX",
                experience="2 years"
            )
            
            candidate_id = await service.create_candidate(candidate_data)
            
            # Verify the candidate was created with location and experience
            assert candidate_id is not None
            mock_collection.insert_one.assert_called_once()
            
            # Check the data passed to insert_one
            call_args = mock_collection.insert_one.call_args[0][0]
            assert call_args['name'] == "Test User"
            assert call_args['location'] == "Austin, TX"
            assert call_args['experience'] == "2 years"
    
    async def test_update_candidate_with_location(self):
        """Test updating candidate with location"""
        service = CandidateService()
        candidate_id = str(ObjectId())
        
        # Mock the database collection
        with patch.object(service, 'collection') as mock_collection:
            mock_result = {
                '_id': ObjectId(candidate_id),
                'name': 'Test User',
                'location': 'Boston, MA',
                'created_at': datetime.now(datetime.timezone.utc),
                'updated_at': datetime.now(datetime.timezone.utc)
            }
            mock_collection.find_one_and_update = AsyncMock(return_value=mock_result)
            
            update_data = CandidateUpdate(location="Boston, MA")
            
            result = await service.update_candidate(candidate_id, update_data)
            
            assert result is not None
            assert result.location == "Boston, MA"
            mock_collection.find_one_and_update.assert_called_once()
    
    def test_to_response_includes_location(self):
        """Test that to_response method includes location field"""
        service = CandidateService()
        
        candidate = Candidate(
            id=ObjectId(),
            name="Test User",
            location="Seattle, WA",
            experience="4 years",
            created_at=datetime.now(datetime.timezone.utc),
            updated_at=datetime.now(datetime.timezone.utc)
        )
        
        response = service.to_response(candidate)
        
        assert response.location == "Seattle, WA"
        assert response.experience == "4 years"
        assert response.name == "Test User"


@pytest.mark.asyncio
class TestCandidateAPI:
    """Test candidate API endpoints with location and experience fields"""
    
    async def test_create_candidate_api_with_location_and_experience(self):
        """Test API endpoint accepts location and experience in form data"""
        # This is a conceptual test - in actual implementation,
        # you would use FastAPI TestClient to test the endpoint
        
        form_data = {
            'name': 'API Test User',
            'email': 'api@example.com',
            'skills': 'Python, FastAPI',
            'location': 'Denver, CO',
            'experience': '3 years'
        }
        
        # Verify that CandidateCreate can be constructed from this data
        skills_list = [skill.strip() for skill in form_data['skills'].split(',')]
        candidate_data = CandidateCreate(
            name=form_data['name'],
            email=form_data['email'],
            skills=skills_list,
            location=form_data['location'],
            experience=form_data['experience']
        )
        
        assert candidate_data.location == 'Denver, CO'
        assert candidate_data.experience == '3 years'
        assert candidate_data.skills == ['Python', 'FastAPI']