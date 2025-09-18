"""
Candidate matching API routes for TalentSync backend
"""
from fastapi import APIRouter, HTTPException
from typing import List

from ..models.candidate import Candidate
from ..services.job_service import job_service
from ..services.matching_service import matching_service

router = APIRouter(prefix="/jobs", tags=["matching"])


@router.get("/{job_id}/candidates", response_model=List[Candidate])
async def get_candidates_for_job(job_id: str):
    """Get candidates matching a job posting"""
    job = await job_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return await matching_service.get_candidates_for_job(job)