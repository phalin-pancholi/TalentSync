"""
JobPosting model for TalentSync backend
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class JobPostingBase(BaseModel):
    """Base JobPosting model with common fields"""
    title: str
    description: str
    skills: List[str]
    experience_level: str
    department: str
    location: str


class JobPostingCreate(JobPostingBase):
    """Model for creating a new job posting"""
    pass


class JobPostingUpdate(BaseModel):
    """Model for updating an existing job posting"""
    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None


class JobPosting(JobPostingBase):
    """Complete JobPosting model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True