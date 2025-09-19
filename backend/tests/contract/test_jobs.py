"""
Contract tests for job API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_get_jobs():
    """Test GET /api/jobs endpoint"""
    response = client.get("/api/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_job():
    """Test POST /api/jobs endpoint"""
    job = {
        "title": "Test Job",
        "description": "Test Description",
        "skills": ["Python", "FastAPI"],
        "experience_level": "Mid",
        "department": "Engineering",
        "location": "Remote"
    }
    response = client.post("/api/jobs/", json=job)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["title"] == "Test Job"


def test_get_job_by_id():
    """Test GET /api/jobs/{job_id} endpoint"""
    # First create a job
    job = {
        "title": "Test Job for Get",
        "description": "Test Description",
        "skills": ["Python"],
        "experience_level": "Junior",
        "department": "Engineering",
        "location": "Remote"
    }
    create_response = client.post("/api/jobs/", json=job)
    job_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_get_job_not_found():
    """Test GET /api/jobs/{job_id} with non-existent ID"""
    response = client.get("/api/jobs/nonexistent-id")
    assert response.status_code == 404


def test_update_job():
    """Test PUT /api/jobs/{job_id} endpoint"""
    # First create a job
    job = {
        "title": "Job to Update",
        "description": "Original description",
        "skills": ["Python"],
        "experience_level": "Junior",
        "department": "Engineering",
        "location": "Remote"
    }
    create_response = client.post("/api/jobs/", json=job)
    job_id = create_response.json()["id"]
    
    # Then update it
    update_data = {"title": "Updated Job Title"}
    response = client.put(f"/api/jobs/{job_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Job Title"


def test_delete_job():
    """Test DELETE /api/jobs/{job_id} endpoint"""
    # First create a job
    job = {
        "title": "Job to Delete",
        "description": "Will be deleted",
        "skills": ["Python"],
        "experience_level": "Junior",
        "department": "Engineering",
        "location": "Remote"
    }
    create_response = client.post("/api/jobs/", json=job)
    job_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted successfully"


def test_get_candidates_for_job():
    """Test GET /api/jobs/{job_id}/candidates endpoint"""
    # First create a job
    job = {
        "title": "Job for Candidates",
        "description": "Test Description",
        "skills": ["Python", "React"],
        "experience_level": "Mid",
        "department": "Engineering",
        "location": "Remote"
    }
    create_response = client.post("/api/jobs/", json=job)
    job_id = create_response.json()["id"]
    
    # Then get candidates
    response = client.get(f"/api/jobs/{job_id}/candidates")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_candidates_for_nonexistent_job():
    """Test GET /api/jobs/{job_id}/candidates with non-existent job"""
    response = client.get("/api/jobs/nonexistent-id/candidates")
    assert response.status_code == 404