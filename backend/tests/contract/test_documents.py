import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

def test_get_document():
    # First create a candidate with a document
    with open("tests/data/sample_job.pdf", "rb") as f:
        create_response = client.post(
            "/candidates",
            data={"name": "Test User", "email": "testdoc@example.com", "skills": "Testing"},
            files={"document": ("test_resume.pdf", f, "application/pdf")}
        )
    assert create_response.status_code == 201
    candidate_data = create_response.json()
    
    # Get the document if document_id is provided
    if "document_id" in candidate_data:
        response = client.get(f"/documents/{candidate_data['document_id']}")
        assert response.status_code == 200
        assert response.json()["file_name"] == "test_resume.pdf"

def test_get_document_not_found():
    response = client.get("/documents/nonexistent")
    assert response.status_code == 404