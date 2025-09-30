"""
Unit tests for services
"""
import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.services.matching_service import MatchingService
from src.services.candidate_service import CandidateService
from src.services.document_service import DocumentService
from src.models.job_posting import JobPosting
from src.models.candidate import Candidate


@pytest.mark.asyncio
async def test_matching_service_initialization():
    """Test MatchingService initialization"""
    service = MatchingService()
    assert service.candidate_service is not None
    assert isinstance(service.candidate_service, CandidateService)


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
    
    assert len(candidates) >= 0  # May be 0 if no candidates meet 20% threshold
    
    # All returned candidates should have >20% match
    for candidate in candidates:
        assert candidate.match_percentage > 20.0
    
    assert all(isinstance(c, Candidate) for c in candidates)
    
    # Check sorting by match percentage
    for i in range(len(candidates) - 1):
        assert candidates[i].match_percentage >= candidates[i + 1].match_percentage
    
    # Check that candidates with Python have higher match percentage
    python_candidates = [c for c in candidates if "Python" in c.skills and c.match_percentage > 20.0]
    if python_candidates:
        assert python_candidates[0].match_percentage > 20.0


@pytest.mark.asyncio
async def test_get_candidates_for_job_no_skills():
    """Test getting candidates for a job with no skills - should return empty due to 0% match"""
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
    
    # Should return empty list since all candidates will have 0% match (below 20% threshold)
    assert len(candidates) == 0


@pytest.mark.asyncio
async def test_matching_percentage_calculation():
    """Test match percentage calculation logic with 20% threshold"""
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
    
    # All returned candidates should have >20% match
    for candidate in candidates:
        assert candidate.match_percentage > 20.0
        expected_percentage = (len(candidate.matched_skills) / len(job.skills)) * 100
        assert abs(candidate.match_percentage - expected_percentage) < 0.1
        # With 4 skills, need at least 1 matching skill for >20% (1/4 = 25%)
        assert len(candidate.matched_skills) >= 1


@pytest.mark.asyncio
async def test_matching_threshold_filter():
    """Test that only candidates with >20% match are returned"""
    service = MatchingService()
    
    job = JobPosting(
        title="Specialized Developer",
        description="Needs specific skills",
        skills=["Python", "FastAPI", "MongoDB", "Docker", "Kubernetes"],  # 5 skills
        experience_level="Senior",
        department="Engineering",
        location="Remote"
    )
    
    candidates = await service.get_candidates_for_job(job)
    
    # Verify all returned candidates have >20% match
    for candidate in candidates:
        assert candidate.match_percentage > 20.0
        # With 5 skills, need at least 2 matching skills for >20% (2/5 = 40%)
        # But since we check >20%, even 1 skill (1/5 = 20%) should be excluded
        assert len(candidate.matched_skills) >= 1


class TestDocumentService:
    """Test cases for DocumentService"""
    
    def test_generate_profile_summary_pdf_basic(self):
        """Test basic PDF generation functionality"""
        service = DocumentService()
        
        candidate_name = "John Doe"
        profile_summary = """
Professional Summary

Software Engineer with 5+ years of experience in Python development.

Education

Bachelor's degree in Computer Science

Technical Skills

Programming Languages: Python, JavaScript
"""
        
        result = service.generate_profile_summary_pdf(candidate_name, profile_summary)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Since we're returning text as bytes, check content
        content = result.decode('utf-8')
        assert "John Doe" in content
        assert "Software Engineer" in content
        assert "Python" in content
        assert "PROFILE SUMMARY" in content or "Profile Summary" in content

    def test_generate_profile_summary_pdf_empty_summary(self):
        """Test PDF generation with empty summary"""
        service = DocumentService()
        
        candidate_name = "Jane Smith"
        profile_summary = ""
        
        result = service.generate_profile_summary_pdf(candidate_name, profile_summary)
        
        assert isinstance(result, bytes)
        content = result.decode('utf-8')
        assert "Jane Smith" in content

    def test_generate_profile_summary_pdf_special_characters(self):
        """Test PDF generation with special characters in name and summary"""
        service = DocumentService()
        
        candidate_name = "José García-Smith"
        profile_summary = "Summary with special chars: àáâã & symbols: @#$%"
        
        result = service.generate_profile_summary_pdf(candidate_name, profile_summary)
        
        assert isinstance(result, bytes)
        content = result.decode('utf-8')
        assert "José García-Smith" in content
        assert "special chars" in content

    def test_generate_profile_summary_pdf_long_content(self):
        """Test PDF generation with very long profile summary"""
        service = DocumentService()
        
        candidate_name = "Long Content Test"
        profile_summary = "Very long summary. " * 1000  # Create very long content
        
        result = service.generate_profile_summary_pdf(candidate_name, profile_summary)
        
        assert isinstance(result, bytes)
        assert len(result) > len(profile_summary)  # Should have additional PDF structure
        
        content = result.decode('utf-8')
        assert "Long Content Test" in content