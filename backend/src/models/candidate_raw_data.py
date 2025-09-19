from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
import uuid

class FileData(BaseModel):
    """Model for file data within candidate raw data"""
    file_name: str
    file_type: str
    file_size: int
    file_data: bytes  # or GridFS reference
    uploaded_at: datetime = datetime.utcnow()
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['pdf', 'docx', 'txt', 'application/pdf', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'text/plain']
        if v not in allowed_types:
            raise ValueError(f'File type {v} not supported')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size {v} exceeds maximum allowed size of {max_size} bytes')
        return v

class CandidateRawData(BaseModel):
    """Model for candidate raw data storage"""
    candidate_id: str = str(uuid.uuid4())
    email: EmailStr
    raw_files: List[FileData] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Config:
        # MongoDB configuration
        collection = "candidate_raw_data"
        indexes = [
            [("email", 1)],  # Index on email for search
            [("candidate_id", 1)]  # Index on candidate_id
        ]

class ProfileSummary(BaseModel):
    """Model for generated profile summary"""
    summary_id: str = str(uuid.uuid4())
    candidate_id: str
    summary_text: str
    pdf_file: Optional[bytes] = None  # PDF data or GridFS reference
    generated_at: datetime = datetime.utcnow()
    llm_model: str = "Gemini-1.0-pro"
    status: str = "pending"  # pending, success, error
    error_message: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'success', 'error']
        if v not in allowed_statuses:
            raise ValueError(f'Status {v} not allowed')
        return v
    
    class Config:
        # MongoDB configuration
        collection = "profile_summaries"
        indexes = [
            [("candidate_id", 1)],  # Index on candidate_id
            [("summary_id", 1)]  # Index on summary_id
        ]

# Request/Response models for API
class CandidateRawDataRequest(BaseModel):
    email: EmailStr

class CandidateRawDataResponse(BaseModel):
    candidate_id: str
    email: str
    file_count: int
    created_at: datetime
    
class ProfileGenerationResponse(BaseModel):
    summary_id: str
    candidate_id: str
    status: str
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None