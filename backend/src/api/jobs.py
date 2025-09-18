"""
Job API routes for TalentSync backend
"""
from fastapi import APIRouter, HTTPException
from typing import List

from ..models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate
from ..services.job_service import job_service

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