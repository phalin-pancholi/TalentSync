import pytest
from fastapi.testclient import TestClient
import io

# Task 1: Contract test for uploading candidate raw data
@pytest.mark.contract
def test_upload_candidate_raw_data_contract(client: TestClient):
    """Test contract for uploading candidate raw data"""
    # Prepare test data
    email = "test@example.com"
    file_content = b"This is a test resume content"
    
    response = client.post(
        "/candidates/raw",
        data={"email": email},
        files={"files": ("resume.pdf", file_content, "application/pdf")},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "candidate_id" in data
    assert data["email"] == email

# Task 2: Contract test for searching candidate raw data
@pytest.mark.contract
def test_search_candidate_raw_data_by_email_contract(client: TestClient):
    """Test contract for searching candidate raw data by email"""
    response = client.get("/candidates/raw/search?email=test@example.com")
    assert response.status_code in (200, 404)
    
    if response.status_code == 200:
        data = response.json()
        assert "candidate_id" in data
        assert "email" in data

@pytest.mark.contract
def test_search_candidate_raw_data_by_id_contract(client: TestClient):
    """Test contract for searching candidate raw data by ID"""
    response = client.get("/candidates/raw/search?candidate_id=test-id-123")
    assert response.status_code in (200, 404)

# Task 3: Contract test for generating profile summary
@pytest.mark.contract
def test_generate_profile_summary_contract(client: TestClient):
    """Test contract for generating profile summary PDF"""
    candidate_id = "test-candidate-123"
    response = client.post(f"/candidates/{candidate_id}/generate-profile")
    
    assert response.status_code in (200, 404, 500)
    
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

# Task 4: Integration test for uploading multiple file types
@pytest.mark.integration
def test_upload_multiple_file_types(client: TestClient):
    """Test uploading different file types (pdf, docx, txt)"""
    email = "multifile@example.com"
    
    files = [
        ("files", ("resume.pdf", b"PDF content", "application/pdf")),
        ("files", ("feedback.docx", b"DOCX content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ("files", ("notes.txt", b"Text content", "text/plain"))
    ]
    
    response = client.post(
        "/candidates/raw",
        data={"email": email},
        files=files
    )
    
    assert response.status_code in (201, 400)

# Task 5: Integration test for error handling
@pytest.mark.integration
def test_llm_pdf_error_handling(client: TestClient):
    """Test error handling when LLM or PDF generation fails"""
    # First upload some data
    response = client.post(
        "/candidates/raw",
        data={"email": "error@example.com"},
        files={"files": ("resume.pdf", b"content", "application/pdf")}
    )
    
    if response.status_code == 201:
        candidate_id = response.json()["candidate_id"]
        
        # Try to generate profile (might fail due to LLM/PDF issues)
        profile_response = client.post(f"/candidates/{candidate_id}/generate-profile")
        
        if profile_response.status_code == 500:
            error_data = profile_response.json()
            assert "error" in error_data or "message" in error_data

# Task 6: Integration test for large file upload validation
@pytest.mark.integration
def test_large_file_upload_validation(client: TestClient):
    """Test validation for large files and unsupported types"""
    email = "validation@example.com"
    
    # Test file too large (>10MB simulated)
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    response = client.post(
        "/candidates/raw",
        data={"email": email},
        files={"files": ("large.pdf", large_content, "application/pdf")}
    )
    assert response.status_code == 400
    
    # Test unsupported file type
    response = client.post(
        "/candidates/raw",
        data={"email": email},
        files={"files": ("image.jpg", b"JPEG content", "image/jpeg")}
    )
    assert response.status_code == 400