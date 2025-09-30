"""
Integration tests for LLM-based job upload endpoint
Tests the complete flow: upload -> parsing -> LLM extraction -> DB storage
"""
import pytest
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from src.api.main import app
from src.services.db_service import database_service

client = TestClient(app)
TEST_DATA_DIR = "/home/adarsh/hackathon/TalentSync/backend/tests/data"


@pytest.mark.asyncio
async def test_end_to_end_job_upload_and_storage():
    """Test complete end-to-end flow from file upload to database storage"""
    # Prepare test file
    txt_path = os.path.join(TEST_DATA_DIR, "sample_job.txt")
    if not os.path.exists(txt_path):
        pytest.skip(f"Test data file not found: {txt_path}")
    
    # Upload file via API
    with open(txt_path, "rb") as f:
        response = client.post(
            "/api/jobs/upload_llm", 
            files={"file": ("sample_job.txt", f, "text/plain")}
        )
    
    # Verify API response
    assert response.status_code == 200
    job_data = response.json()
    job_id = job_data["id"]
    
    # Verify job was stored in database
    collection = database_service.get_collection("job_postings")
    stored_job = await collection.find_one({"id": job_id})
    
    assert stored_job is not None
    assert stored_job["id"] == job_id
    assert "created_at" in stored_job
    assert "updated_at" in stored_job
    
    # Clean up - delete the test job
    await collection.delete_one({"id": job_id})


@pytest.mark.asyncio
async def test_file_parsing_service_integration():
    """Test file parsing service with actual test files"""
    from src.services.file_parsing_service import FileParsingService
    
    # Test text file parsing
    txt_path = os.path.join(TEST_DATA_DIR, "sample_job.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "rb") as f:
            content = f.read()
        
        text_content = FileParsingService.extract_text_from_file(content, "sample_job.txt")
        assert isinstance(text_content, str)
        assert len(text_content.strip()) > 0
        assert "Software Engineer" in text_content or "job" in text_content.lower()
    
    # Test unsupported file type
    jpg_path = os.path.join(TEST_DATA_DIR, "unsupported_file.jpg")
    if os.path.exists(jpg_path):
        with open(jpg_path, "rb") as f:
            content = f.read()
        
        with pytest.raises(ValueError) as exc_info:
            FileParsingService.extract_text_from_file(content, "unsupported_file.jpg")
        assert "Unsupported file type" in str(exc_info.value)


@pytest.mark.skipif(
    not os.getenv('GOOGLE_API_KEY'), 
    reason="GOOGLE_API_KEY not available for LLM testing"
)
@pytest.mark.asyncio
async def test_llm_extraction_service_integration():
    """Test LLM extraction service with sample text"""
    from src.services.llm_extraction_service import LLMExtractionService
    
    llm_service = LLMExtractionService()
    
    # Test with sample job description
    sample_text = """
    Software Engineer - Full Stack
    
    We are seeking a talented Full Stack Software Engineer to join our team.
    
    Requirements:
    - 3+ years of experience in software development
    - Proficiency in JavaScript, Python, and React
    - Bachelor's degree in Computer Science
    
    Location: San Francisco, CA
    Department: Engineering
    """
    
    if llm_service.is_service_available():
        job_posting = llm_service.extract_job_info(sample_text)
        
        # Verify the structure (fields can be None)
        assert hasattr(job_posting, 'title')
        assert hasattr(job_posting, 'description')
        assert hasattr(job_posting, 'skills')
        assert hasattr(job_posting, 'experience_level')
        assert hasattr(job_posting, 'department')
        assert hasattr(job_posting, 'location')
    else:
        pytest.skip("LLM service not available for testing")


@pytest.mark.asyncio
async def test_database_job_creation_from_llm():
    """Test database job creation using LLM-extracted data"""
    from src.services.job_service import job_service
    from src.models.job_posting import JobPostingLLMCreate
    
    # Create test job data with some None fields
    job_data = JobPostingLLMCreate(
        title="Test Engineer",
        description="A test position",
        skills=["Python", "Testing"],
        experience_level=None,  # This field is None
        department="Engineering",
        location=None  # This field is None
    )
    
    # Create job in database
    created_job = await job_service.create_job_from_llm(job_data)
    
    assert created_job.id is not None
    assert created_job.title == "Test Engineer"
    assert created_job.description == "A test position"
    assert created_job.skills == ["Python", "Testing"]
    assert created_job.experience_level is None
    assert created_job.department == "Engineering"
    assert created_job.location is None
    assert created_job.created_at is not None
    assert created_job.updated_at is not None
    
    # Clean up - delete the test job
    collection = database_service.get_collection("job_postings")
    await collection.delete_one({"id": created_job.id})


@pytest.mark.asyncio  
async def test_error_handling_integration():
    """Test error handling in the complete integration flow"""
    
    # Test with completely empty file
    response = client.post(
        "/api/jobs/upload_llm", 
        files={"file": ("empty.txt", b"", "text/plain")}
    )
    assert response.status_code == 400
    
    # Test with file containing only whitespace
    response = client.post(
        "/api/jobs/upload_llm", 
        files={"file": ("whitespace.txt", b"   \n\t  ", "text/plain")}
    )
    assert response.status_code == 400