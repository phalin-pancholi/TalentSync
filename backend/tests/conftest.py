"""
Test configuration and fixtures
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        "title": "Software Engineer",
        "description": "Backend developer position",
        "skills": ["Python", "FastAPI", "MongoDB"],
        "experience_level": "Mid",
        "department": "Engineering",
        "location": "Remote"
    }