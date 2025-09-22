import pytest
import requests
import os

BASE_URL = "http://localhost:8000/api/candidates"

@pytest.mark.parametrize("file_path,file_type,status_code", [
    ("backend/tests/data/sample_job.txt", "text/plain", 200),
    ("backend/tests/data/sample_job.pdf", "application/pdf", 200),
    ("backend/tests/data/unsupported_file.jpg", "image/jpeg", 415),
    ("backend/tests/data/sample_job_missing_fields.txt", "text/plain", 200),
])
def test_upload_extra_details(file_path, file_type, status_code):
    """Contract test for uploading candidate extra details endpoint"""
    candidate_id = "test-candidate-1"
    
    # Get absolute path to test file
    test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
    
    with open(test_file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, file_type)}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
        
        assert response.status_code == status_code
        
        if status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["candidate_id"] == candidate_id
            assert data["text_content"]
            assert data["created_at"]
            assert len(data["text_content"]) > 0  # Ensure text was extracted
        elif status_code == 415:
            error_data = response.json()
            assert "detail" in error_data
            assert "Unsupported file type" in error_data["detail"]

def test_upload_large_file():
    """Test that files larger than 5MB are rejected"""
    candidate_id = "test-candidate-1"
    
    # Create a large file content (> 5MB)
    large_content = "x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
    
    files = {"file": ("large_file.txt", large_content, "text/plain")}
    response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
    
    assert response.status_code == 413  # Request Entity Too Large

def test_upload_empty_file():
    """Test that empty files are rejected"""
    candidate_id = "test-candidate-1"
    
    files = {"file": ("empty.txt", "", "text/plain")}
    response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
    
    assert response.status_code == 422  # Unprocessable Entity