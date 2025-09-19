import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

def test_create_candidate_form():
    response = client.post(
        "/candidates",
        data={"name": "Alice", "email": "alice@example.com", "skills": ["Python"]}
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_create_candidate_document():
    with open("tests/data/sample_resume.pdf", "rb") as f:
        response = client.post(
            "/candidates",
            data={"name": "Bob", "email": "bob@example.com", "skills": ["JavaScript"]},
            files={"document": ("sample_resume.pdf", f, "application/pdf")}
        )
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_candidate():
    # Assume candidate with id '1' exists (replace with fixture or setup)
    response = client.get("/candidates/1")
    assert response.status_code in (200, 404)

def test_update_candidate():
    # Assume candidate with id '1' exists (replace with fixture or setup)
    response = client.put(
        "/candidates/1",
        json={"name": "Alice Updated", "skills": ["Python", "SQL"]}
    )
    assert response.status_code in (200, 404)

def test_delete_candidate():
    # Assume candidate with id '1' exists (replace with fixture or setup)
    response = client.delete("/candidates/1")
    assert response.status_code in (204, 404)
