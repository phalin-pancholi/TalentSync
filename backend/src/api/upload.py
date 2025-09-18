"""
File upload API routes for TalentSync backend
"""
from fastapi import APIRouter, File, UploadFile, HTTPException

from ..models.job_posting import JobPosting
from ..services.job_service import job_service

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/job", response_model=JobPosting)
async def upload_job_document(file: UploadFile = File(...)):
    """Upload a job document and extract job posting"""
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and Word documents are allowed")
    
    # In a real application, you would parse the document content
    # For now, we'll return dummy job data
    from ..models.job_posting import JobPostingCreate
    
    dummy_job_data = JobPostingCreate(
        title=f"Senior Software Engineer - From {file.filename}",
        description=f"Position extracted from uploaded document: {file.filename}. This is a senior-level software engineering role requiring strong technical skills and leadership experience.",
        skills=["Python", "React", "MongoDB", "Team Leadership", "System Design"],
        experience_level="Senior",
        department="Engineering",
        location="New York"
    )
    
    return await job_service.create_job(dummy_job_data)