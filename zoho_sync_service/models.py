from datetime import datetime
from typing import Dict, List, Optional, Any, Annotated
from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from bson import ObjectId


# Pydantic v2 compatible ObjectId handler
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]


class EmployeeRecord(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    employee_id: str = Field(..., description="Unique identifier from Zoho")
    name: str = Field(..., description="Employee name")
    contact_info: Dict[str, Any] = Field(default_factory=dict, description="Contact information")
    job_title: str = Field(..., description="Employee job title")
    department: str = Field(..., description="Employee department")
    all_other_fields: Dict[str, Any] = Field(default_factory=dict, description="All other fields from Zoho")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CandidateDetails(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    candidate_id: str = Field(..., description="Unique candidate identifier")
    employee_id: str = Field(..., description="Reference to EmployeeRecord")
    profile: str = Field(..., description="Generated candidate profile")
    skills: List[str] = Field(default_factory=list, description="List of candidate skills")
    experience: str = Field(..., description="Candidate experience summary")
    summary: str = Field(..., description="Overall candidate summary")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class SyncStatus(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    last_sync_time: datetime = Field(default_factory=datetime.utcnow)
    sync_interval: int = Field(default=5, description="Sync interval in minutes")
    access_token: str = Field(..., description="Zoho API access token")
    processed_employee_ids: List[str] = Field(default_factory=list, description="List of processed employee IDs")
    sync_count: int = Field(default=0, description="Number of sync operations completed")
    last_error: Optional[str] = Field(default=None, description="Last error message if any")