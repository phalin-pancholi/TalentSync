"""
Candidate model for TalentSync backend
"""
from pydantic import BaseModel, Field
from typing import List
import uuid


class CandidateBase(BaseModel):
    """Base Candidate model with common fields"""
    name: str
    email: str
    skills: List[str]
    experience_years: int
    current_role: str
    department: str
    location: str


class Candidate(CandidateBase):
    """Complete Candidate model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_percentage: float = 0.0
    matched_skills: List[str] = []

    class Config:
        from_attributes = True