"""
Unit tests for models
"""
import pytest
from datetime import datetime
from src.models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate
from src.models.candidate import Candidate


def test_job_posting_creation():
    """Test JobPosting model creation"""
    job_data = {
        "title": "Software Engineer",
        "description": "Backend developer role",
        "skills": ["Python", "FastAPI"],
        "experience_level": "Mid",
        "department": "Engineering",
        "location": "Remote"
    }
    
    job = JobPosting(**job_data)
    assert job.title == "Software Engineer"
    assert job.skills == ["Python", "FastAPI"]
    assert job.id is not None
    assert isinstance(job.created_at, datetime)
    assert isinstance(job.updated_at, datetime)


def test_job_posting_create_model():
    """Test JobPostingCreate model"""
    job_data = {
        "title": "Test Job",
        "description": "Test Description",
        "skills": ["Python"],
        "experience_level": "Junior",
        "department": "Engineering",
        "location": "Remote"
    }
    
    job_create = JobPostingCreate(**job_data)
    assert job_create.title == "Test Job"
    assert job_create.skills == ["Python"]


def test_job_posting_update_model():
    """Test JobPostingUpdate model with partial data"""
    update_data = {"title": "Updated Title", "skills": ["Python", "Django"]}
    
    job_update = JobPostingUpdate(**update_data)
    assert job_update.title == "Updated Title"
    assert job_update.skills == ["Python", "Django"]
    assert job_update.description is None  # Optional field


def test_candidate_creation():
    """Test Candidate model creation"""
    candidate_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "JavaScript"],
        "experience": "5 years",
        "location": "New York"
    }
    
    candidate = Candidate(**candidate_data)
    assert candidate.name == "John Doe"
    assert candidate.skills == ["Python", "JavaScript"]
    assert candidate.experience == "5 years"
    assert candidate.id is not None
    assert candidate.match_percentage == 0.0
    assert candidate.matched_skills == []


def test_candidate_with_matching_data():
    """Test Candidate with matching percentage and skills"""
    candidate_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "skills": ["Python", "React"],
        "experience_years": 3,
        "current_role": "Full Stack Developer",
        "department": "Engineering",
        "location": "Remote",
        "match_percentage": 85.5,
        "matched_skills": ["Python", "React"]
    }
    
    candidate = Candidate(**candidate_data)
    assert candidate.match_percentage == 85.5
    assert candidate.matched_skills == ["Python", "React"]