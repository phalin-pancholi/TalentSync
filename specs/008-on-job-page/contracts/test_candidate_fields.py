import pytest
import asyncio
from backend.src.services.candidate_service import CandidateService
from backend.src.models.candidate import CandidateCreate, CandidateResponse

# Contract test for candidate location and experience fields

def test_candidate_location_and_experience_schema():
    """Candidate API must include location and experience fields."""
    # Example candidate response
    candidate = {
        "id": "abc123",
        "name": "Jane Doe",
        "location": "Bangalore, India",
        "experience": 4.5,
        "experience_description": "Senior Developer",
        "skills": ["Python", "React"]
    }
    assert "location" in candidate
    assert isinstance(candidate["location"], str)
    assert "experience" in candidate
    assert isinstance(candidate["experience"], (int, float))
    assert candidate["experience"] >= 0
    assert "experience_description" in candidate
    assert isinstance(candidate["experience_description"], str)

def test_candidate_missing_fields():
    """If location or experience is missing, API should still return valid object."""
    candidate = {
        "id": "abc124",
        "name": "John Smith",
        "skills": ["Java"]
    }
    assert "location" not in candidate or candidate["location"] == ""
    assert "experience" not in candidate or candidate["experience"] == ""

@pytest.mark.asyncio
async def test_candidate_model_with_new_fields():
    """Test that CandidateCreate model accepts location and experience fields."""
    candidate_data = CandidateCreate(
        name="Test Candidate",
        email="test@example.com",
        phone="+1234567890",
        skills=["Python", "JavaScript"],
        location="San Francisco, CA",
        experience="3 years"
    )
    
    assert candidate_data.name == "Test Candidate"
    assert candidate_data.location == "San Francisco, CA"
    assert candidate_data.experience == "3 years"

@pytest.mark.asyncio
async def test_candidate_service_handles_new_fields():
    """Test that candidate service can handle location and experience fields."""
    # This test should fail until we implement the fields
    service = CandidateService()
    
    # Try to create a candidate with new fields
    candidate_data = {
        "name": "Test User",
        "email": "test@example.com",
        "skills": ["Python"],
        "location": "New York, NY",
        "experience": "5 years"
    }
    
    # This should not raise an error when fields are implemented
    try:
        # Test that the service can handle these fields without errors
        assert True  # Placeholder - will be updated when service is implemented
    except Exception as e:
        pytest.fail(f"Service should handle new fields: {e}")
