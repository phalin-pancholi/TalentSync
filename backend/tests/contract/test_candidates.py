import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_list_candidates():
    response = client.get("/api/candidates/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_candidate_form():
    response = client.post(
        "/api/candidates/",
        json={"name": "Alice", "email": "alice@example.com", "skills": ["Python"]}
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_create_candidate_document():
    with open("tests/data/sample_job.pdf", "rb") as f:
        response = client.post(
            "/api/candidates/",
            data={"name": "Bob", "email": "bob@example.com", "skills": "JavaScript"},
            files={"document": ("sample_resume.pdf", f, "application/pdf")}
        )
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_candidate():
    # First create a candidate
    create_response = client.post(
        "/api/candidates/",
        json={"name": "Test User", "email": "test@example.com", "skills": ["Testing"]}
    )
    assert create_response.status_code == 201
    candidate_id = create_response.json()["id"]
    
    # Then get the candidate
    response = client.get(f"/api/candidates/{candidate_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"

def test_update_candidate():
    # First create a candidate
    create_response = client.post(
        "/api/candidates/",
        json={"name": "Test User", "email": "test2@example.com", "skills": ["Testing"]}
    )
    assert create_response.status_code == 201
    candidate_id = create_response.json()["id"]
    
    # Then update the candidate
    response = client.put(
        f"/api/candidates/{candidate_id}",
        json={"name": "Updated User", "skills": ["Testing", "Python"]}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"

def test_delete_candidate():
    # First create a candidate
    create_response = client.post(
        "/api/candidates/",
        json={"name": "Test User", "email": "test3@example.com", "skills": ["Testing"]}
    )
    assert create_response.status_code == 201
    candidate_id = create_response.json()["id"]
    
    # Then delete the candidate
    response = client.delete(f"/api/candidates/{candidate_id}")
    assert response.status_code == 204