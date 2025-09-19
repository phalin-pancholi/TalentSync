import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app
import os

client = TestClient(app)

# Path to test data files
TEST_DATA_DIR = "/home/adarsh/hackathon/TalentSync/backend/tests/data"


def test_upload_llm_pdf_success():
    """Test successful PDF upload and job creation"""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_job.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip(f"Test data file not found: {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/jobs/upload_llm", 
            files={"file": ("sample_job.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    # Allow all fields to be None, but check structure
    expected_fields = ["title", "description", "skills", "experience_level", "department", "location"]
    for field in expected_fields:
        assert field in data


def test_upload_llm_txt_success():
    """Test successful text file upload and job creation"""
    txt_path = os.path.join(TEST_DATA_DIR, "sample_job.txt")
    if not os.path.exists(txt_path):
        pytest.skip(f"Test data file not found: {txt_path}")
    
    with open(txt_path, "rb") as f:
        response = client.post(
            "/api/jobs/upload_llm", 
            files={"file": ("sample_job.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


def test_upload_llm_missing_fields():
    """Test upload with file containing missing/incomplete job information"""
    txt_path = os.path.join(TEST_DATA_DIR, "sample_job_missing_fields.txt")
    if not os.path.exists(txt_path):
        pytest.skip(f"Test data file not found: {txt_path}")
    
    with open(txt_path, "rb") as f:
        response = client.post(
            "/api/jobs/upload_llm", 
            files={"file": ("sample_job_missing_fields.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    # Should succeed even with missing fields
    assert "id" in data


def test_upload_llm_unsupported_file():
    """Test upload with unsupported file type"""
    jpg_path = os.path.join(TEST_DATA_DIR, "unsupported_file.jpg")
    if not os.path.exists(jpg_path):
        pytest.skip(f"Test data file not found: {jpg_path}")
    
    with open(jpg_path, "rb") as f:
        response = client.post(
            "/api/jobs/upload_llm", 
            files={"file": ("unsupported_file.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_llm_empty_file():
    """Test upload with empty file"""
    response = client.post(
        "/api/jobs/upload_llm", 
        files={"file": ("empty.txt", b"", "text/plain")}
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()


def test_upload_llm_no_file():
    """Test endpoint without file upload"""
    response = client.post("/api/jobs/upload_llm")
    
    assert response.status_code == 422  # Validation error


@pytest.mark.skipif(
    not os.getenv('GOOGLE_API_KEY'), 
    reason="GOOGLE_API_KEY not available for testing"
)
def test_upload_llm_llm_unavailable(monkeypatch):
    """Test behavior when LLM service is unavailable"""
    # Mock the LLM service to simulate unavailability
    def mock_is_service_available(self):
        return False
    
    from backend.src.services.llm_extraction_service import LLMExtractionService
    monkeypatch.setattr(LLMExtractionService, "is_service_available", mock_is_service_available)
    
    txt_path = os.path.join(TEST_DATA_DIR, "sample_job.txt")
    if not os.path.exists(txt_path):
        pytest.skip(f"Test data file not found: {txt_path}")
    
    with open(txt_path, "rb") as f:
        response = client.post(
            "/api/jobs/upload_llm", 
            files={"file": ("sample_job.txt", f, "text/plain")}
        )
    
    assert response.status_code == 503
    assert "detail" in response.json()
    assert "LLM service is currently unavailable" in response.json()["detail"]
