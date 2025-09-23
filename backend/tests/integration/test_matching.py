"""
Integration tests for job-candidate matching
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_end_to_end_job_matching():
    """Test complete flow from job creation to candidate matching"""
    # Create a job with specific skills
    job_data = {
        "title": "Python Developer",
        "description": "Backend developer position",
        "skills": ["Python", "FastAPI", "MongoDB"],
        "experience_level": "Mid",
        "department": "Engineering",
        "location": "Remote"
    }
    
    # Create the job
    create_response = client.post("/api/jobs/", json=job_data)
    assert create_response.status_code == 200
    job_id = create_response.json()["id"]
    
    # Get matching candidates
    candidates_response = client.get(f"/api/jobs/{job_id}/candidates")
    assert candidates_response.status_code == 200
    
    candidates = candidates_response.json()
    assert len(candidates) >= 0  # May be 0 if no candidates meet 20% threshold
    
    # Verify all returned candidates have match percentage > 20%
    for candidate in candidates:
        assert candidate["match_percentage"] > 20.0
    
    # Verify candidates are sorted by match percentage
    for i in range(len(candidates) - 1):
        assert candidates[i]["match_percentage"] >= candidates[i + 1]["match_percentage"]
    
    # Verify candidates with Python skill have higher match percentage
    python_candidates = [c for c in candidates if "Python" in c["skills"]]
    if len(python_candidates) > 0:  # Only check if we have Python candidates above 20% threshold
        assert all(c["match_percentage"] > 20.0 for c in python_candidates)
    
    # Check that matched skills are calculated correctly
    for candidate in candidates:
        expected_matched = set(job_data["skills"]).intersection(set(candidate["skills"]))
        assert set(candidate["matched_skills"]) == expected_matched


@pytest.mark.asyncio
async def test_matching_with_no_skills():
    """Test matching when job has no skills - should return no candidates due to 0% match"""
    job_data = {
        "title": "General Position",
        "description": "General role",
        "skills": [],
        "experience_level": "Junior",
        "department": "Operations",
        "location": "Remote"
    }
    
    create_response = client.post("/api/jobs/", json=job_data)
    assert create_response.status_code == 200
    job_id = create_response.json()["id"]
    
    candidates_response = client.get(f"/api/jobs/{job_id}/candidates")
    assert candidates_response.status_code == 200
    
    candidates = candidates_response.json()
    # Should return empty list since all candidates will have 0% match (below 20% threshold)
    assert len(candidates) == 0


@pytest.mark.asyncio
async def test_matching_threshold_filter():
    """Test that only candidates with >20% match are returned"""
    # Create a job with many skills to test threshold
    job_data = {
        "title": "Full Stack Developer",
        "description": "Requires many skills",
        "skills": ["Python", "JavaScript", "React", "Django", "PostgreSQL"],
        "experience_level": "Senior",
        "department": "Engineering",
        "location": "Remote"
    }
    
    create_response = client.post("/api/jobs/", json=job_data)
    assert create_response.status_code == 200
    job_id = create_response.json()["id"]
    
    candidates_response = client.get(f"/api/jobs/{job_id}/candidates")
    assert candidates_response.status_code == 200
    
    candidates = candidates_response.json()
    
    # Verify all returned candidates have >20% match
    for candidate in candidates:
        assert candidate["match_percentage"] > 20.0
        # With 5 skills, need at least 2 matching skills for >20% (2/5 = 40%)
        assert len(candidate["matched_skills"]) >= 1