"""
Candidate model for TalentSync backend
"""
from datetime import datetime
from typing import Optional, List, Any
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from pydantic_core import core_schema
import uuid


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.no_info_plain_validator_function(cls.validate),
        ])

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    def __str__(self):
        return str(super())


class CandidateBase(BaseModel):
    """Base Candidate model with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    skills: List[str] = Field(..., min_items=1)

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one skill is required')
        return [skill.strip() for skill in v if skill.strip()]


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    skills: Optional[List[str]] = None

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError('At least one skill is required')
            return [skill.strip() for skill in v if skill.strip()]
        return v


class Candidate(CandidateBase):
    """Complete Candidate model with all fields"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    document_id: Optional[PyObjectId] = None
    # Legacy fields for backward compatibility
    match_percentage: float = 0.0
    matched_skills: List[str] = []

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        from_attributes=True
    )


class CandidateResponse(BaseModel):
    """Response model for Candidate with string IDs"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    skills: List[str]
    created_at: datetime
    updated_at: datetime
    document_id: Optional[str] = None