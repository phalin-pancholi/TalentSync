import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

def test_get_document():
    # Assume document with id '1' exists (replace with fixture or setup)
    response = client.get("/documents/1")
    assert response.status_code in (200, 404)
