"""
Document model for TalentSync backend
"""
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.no_info_plain_validator_function(cls.validate),
        ])

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class DocumentBase(BaseModel):
    """Base Document model with common fields"""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., pattern="^(PDF|DOCX|TXT)$")
    content_text: str = Field(..., min_length=0)
    raw_file_path: str = Field(..., min_length=1)

    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v):
        allowed_types = ['PDF', 'DOCX', 'TXT']
        if v.upper() not in allowed_types:
            raise ValueError(f'File type must be one of: {", ".join(allowed_types)}')
        return v.upper()


class DocumentCreate(DocumentBase):
    candidate_id: PyObjectId


class DocumentUpdate(BaseModel):
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    file_type: Optional[str] = Field(None, pattern="^(PDF|DOCX|TXT)$")
    content_text: Optional[str] = None
    raw_file_path: Optional[str] = Field(None, min_length=1)

    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v):
        if v is not None:
            allowed_types = ['PDF', 'DOCX', 'TXT']
            if v.upper() not in allowed_types:
                raise ValueError(f'File type must be one of: {", ".join(allowed_types)}')
            return v.upper()
        return v


class Document(DocumentBase):
    """Complete Document model with all fields"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    candidate_id: PyObjectId
    upload_date: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "file_name": "resume.pdf",
                "file_type": "PDF",
                "content_text": "John Doe - Software Engineer with 5 years experience...",
                "raw_file_path": "/uploads/resume.pdf",
                "candidate_id": "507f1f77bcf86cd799439011",
                "upload_date": "2023-01-01T00:00:00"
            }
        }
    )


class DocumentInDB(Document):
    pass


class DocumentResponse(BaseModel):
    id: str
    candidate_id: str
    file_name: str
    file_type: str
    content_text: str
    raw_file_path: str
    upload_date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "candidate_id": "507f1f77bcf86cd799439011",
                "file_name": "resume.pdf",
                "file_type": "PDF",
                "content_text": "John Doe - Software Engineer with 5 years experience...",
                "raw_file_path": "/uploads/resume.pdf",
                "upload_date": "2023-01-01T00:00:00"
            }
        }
    )