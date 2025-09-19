"""
Job API routes for TalentSync backend
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import logging

from ..models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate
from ..services.job_service import job_service
from ..services.file_parsing_service import FileParsingService
from ..services.llm_extraction_service import LLMExtractionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobPosting])
async def get_jobs():
    """Get all job postings"""
    return await job_service.get_all_jobs()


@router.post("/", response_model=JobPosting)
async def create_job(job: JobPostingCreate):
    """Create a new job posting"""
    return await job_service.create_job(job)


@router.get("/{job_id}", response_model=JobPosting)
async def get_job(job_id: str):
    """Get a job posting by ID"""
    job = await job_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobPosting)
async def update_job(job_id: str, job_update: JobPostingUpdate):
    """Update an existing job posting"""
    job = await job_service.update_job(job_id, job_update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job posting"""
    success = await job_service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}


@router.post("/upload", response_model=JobPosting)
async def upload_job_llm(file: UploadFile = File(...)):
    """
    Upload a job description document and create a job entry using LLM extraction
    
    Accepts PDF or text files and uses AI to extract job information
    """
    try:
        # Log the upload attempt
        logger.info(f"Processing LLM job upload: filename={file.filename}, content_type={file.content_type}")
        
        # Validate file type
        if not FileParsingService.is_supported_file_type(file.filename):
            logger.warning(f"Unsupported file type uploaded: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported types: {FileParsingService.SUPPORTED_EXTENSIONS}"
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Parse file to extract text
        try:
            text_content = FileParsingService.extract_text_from_file(file_content, file.filename)
            if not text_content.strip():
                raise HTTPException(status_code=400, detail="No text content found in file")
        except ValueError as e:
            logger.error(f"File parsing validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"File parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
        
        # Initialize LLM extraction service
        llm_service = LLMExtractionService()
        
        # Check if LLM service is available
        if not llm_service.is_service_available():
            logger.error("LLM service is not available")
            raise HTTPException(
                status_code=503, 
                detail="LLM service is currently unavailable. Please check configuration."
            )
        
        # Extract job information using LLM
        try:
            job_data = llm_service.extract_job_info(text_content)
            logger.info(f"LLM extraction successful for file: {file.filename}")
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to extract job information: {str(e)}"
            )
        
        # Create job entry in database
        try:
            job_posting = await job_service.create_job_from_llm(job_data)
            logger.info(f"Job created successfully with ID: {job_posting.id}")
            return job_posting
        except Exception as e:
            logger.error(f"Database job creation failed: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to create job entry: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in upload_job_llm: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred during job upload"
        )