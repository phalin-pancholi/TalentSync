import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_get_jobs():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_job():
    job = {
        "title": "Test Job",
        "description": "Test Description",
        "skills": ["Python", "FastAPI"],
        "experience_level": "Mid",
        "department": "Engineering",
        "location": "Remote"
    }
    response = client.post("/api/jobs", json=job)
    assert response.status_code == 200 or response.status_code == 201
    assert "id" in response.json()

def test_get_job_not_found():
    response = client.get("/api/jobs/nonexistent-id")
    assert response.status_code == 404

def test_upload_job_document_invalid_type():
    response = client.post("/api/jobs/upload", files={"file": ("test.txt", b"dummy", "text/plain")})
    assert response.status_code == 400

def test_get_candidates_for_job_not_found():
    response = client.get("/api/jobs/nonexistent-id/candidates")
    assert response.status_code == 404
