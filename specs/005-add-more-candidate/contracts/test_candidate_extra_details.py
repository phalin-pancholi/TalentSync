import pytest
import requests

BASE_URL = "http://localhost:8000/api/candidates"

@pytest.mark.parametrize("file_path,file_type,status_code", [
    ("tests/data/sample_job.txt", "text/plain", 200),
    ("tests/data/sample_job.pdf", "application/pdf", 200),
    ("tests/data/unsupported_file.jpg", "image/jpeg", 415),
    ("tests/data/sample_job_missing_fields.txt", "text/plain", 200),
])
def test_upload_extra_details(file_path, file_type, status_code):
    candidate_id = "test-candidate-1"
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, file_type)}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
        assert response.status_code == status_code
        if status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["candidate_id"] == candidate_id
            assert data["text_content"]
            assert data["created_at"]
