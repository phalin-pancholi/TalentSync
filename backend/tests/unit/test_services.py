"""
Unit tests for services
"""
import pytest
from unittest.mock import AsyncMock, patch
from src.services.matching_service import MatchingService
from src.models.job_posting import JobPosting
from src.models.candidate import Candidate


@pytest.mark.asyncio
async def test_matching_service_initialization():
    """Test MatchingService initialization"""
    service = MatchingService()
    assert service.dummy_candidates is not None
    assert len(service.dummy_candidates) > 0


@pytest.mark.asyncio
async def test_get_candidates_for_job_with_skills():
    """Test getting candidates for a job with specific skills"""
    service = MatchingService()
    
    job = JobPosting(
        title="Python Developer",
        description="Backend role",
        skills=["Python", "FastAPI"],
        experience_level="Mid",
        department="Engineering",
        location="Remote"
    )
    
    candidates = await service.get_candidates_for_job(job)
    
    assert len(candidates) > 0
    assert all(isinstance(c, Candidate) for c in candidates)
    
    # Check sorting by match percentage
    for i in range(len(candidates) - 1):
        assert candidates[i].match_percentage >= candidates[i + 1].match_percentage
    
    # Check that candidates with Python have higher match percentage
    python_candidates = [c for c in candidates if "Python" in c.skills]
    if python_candidates:
        assert python_candidates[0].match_percentage > 0


@pytest.mark.asyncio
async def test_get_candidates_for_job_no_skills():
    """Test getting candidates for a job with no skills"""
    service = MatchingService()
    
    job = JobPosting(
        title="General Role",
        description="General position",
        skills=[],
        experience_level="Junior",
        department="Operations",
        location="Remote"
    )
    
    candidates = await service.get_candidates_for_job(job)
    
    assert len(candidates) > 0
    for candidate in candidates:
        assert candidate.match_percentage == 0.0
        assert candidate.matched_skills == []


@pytest.mark.asyncio
async def test_matching_percentage_calculation():
    """Test match percentage calculation logic"""
    service = MatchingService()
    
    job = JobPosting(
        title="Full Stack Developer",
        description="Full stack role",
        skills=["Python", "React", "MongoDB", "Docker"],  # 4 skills
        experience_level="Senior",
        department="Engineering",
        location="Remote"
    )
    
    candidates = await service.get_candidates_for_job(job)
    
    # Find a candidate with some matching skills
    for candidate in candidates:
        if candidate.match_percentage > 0:
            expected_percentage = (len(candidate.matched_skills) / len(job.skills)) * 100
            assert abs(candidate.match_percentage - expected_percentage) < 0.1
            break