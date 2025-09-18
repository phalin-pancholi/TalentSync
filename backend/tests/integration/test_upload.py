"""
Integration tests for file upload functionality
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_file_upload_creates_job():
    """Test that uploading a file creates a job posting"""
    # Simulate PDF upload
    files = {"file": ("job_description.pdf", b"dummy pdf content", "application/pdf")}
    
    response = client.post("/api/upload/job", files=files)
    assert response.status_code == 200
    
    job_data = response.json()
    assert "id" in job_data
    assert "Senior Software Engineer" in job_data["title"]
    assert "job_description.pdf" in job_data["title"]
    assert job_data["experience_level"] == "Senior"
    assert len(job_data["skills"]) > 0
    
    # Verify the job was actually created in the system
    job_id = job_data["id"]
    get_response = client.get(f"/api/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == job_id


@pytest.mark.asyncio
async def test_file_upload_word_document():
    """Test uploading a Word document"""
    files = {"file": ("job_posting.docx", b"dummy docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    
    response = client.post("/api/upload/job", files=files)
    assert response.status_code == 200
    
    job_data = response.json()
    assert "job_posting.docx" in job_data["title"]


@pytest.mark.asyncio
async def test_file_upload_invalid_file_type():
    """Test that invalid file types are rejected"""
    files = {"file": ("document.txt", b"text content", "text/plain")}
    
    response = client.post("/api/upload/job", files=files)
    assert response.status_code == 400
    assert "Only PDF and Word documents are allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_uploaded_job_can_match_candidates():
    """Test that jobs created from uploads can match candidates"""
    # Upload a file to create a job
    files = {"file": ("python_job.pdf", b"dummy content", "application/pdf")}
    upload_response = client.post("/api/upload/job", files=files)
    assert upload_response.status_code == 200
    
    job_id = upload_response.json()["id"]
    
    # Get matching candidates for the uploaded job
    candidates_response = client.get(f"/api/jobs/{job_id}/candidates")
    assert candidates_response.status_code == 200
    
    candidates = candidates_response.json()
    assert len(candidates) > 0
    
    # Since the uploaded job has Python skills, verify some candidates match
    python_matches = [c for c in candidates if c["match_percentage"] > 0]
    assert len(python_matches) > 0