"""
Job service for TalentSync backend
"""
from typing import List, Optional
from datetime import datetime, timezone

from ..models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate, JobPostingLLMCreate
from .db_service import database_service


class JobService:
    """Service for managing job postings"""
    
    def __init__(self):
        self.collection_name = "job_postings"
    
    async def get_all_jobs(self) -> List[JobPosting]:
        """Get all job postings"""
        collection = database_service.get_collection(self.collection_name)
        jobs = await collection.find().to_list(1000)
        return [JobPosting(**job) for job in jobs]
    
    async def create_job(self, job_data: JobPostingCreate) -> JobPosting:
        """Create a new job posting"""
        collection = database_service.get_collection(self.collection_name)
        job_dict = job_data.dict()
        job_obj = JobPosting(**job_dict)
        await collection.insert_one(job_obj.dict())
        return job_obj
    
    async def get_job_by_id(self, job_id: str) -> Optional[JobPosting]:
        """Get a job posting by ID"""
        collection = database_service.get_collection(self.collection_name)
        job = await collection.find_one({"id": job_id})
        if job:
            return JobPosting(**job)
        return None
    
    async def update_job(self, job_id: str, job_update: JobPostingUpdate) -> Optional[JobPosting]:
        """Update an existing job posting"""
        collection = database_service.get_collection(self.collection_name)
        job = await collection.find_one({"id": job_id})
        if not job:
            return None
        
        update_data = {k: v for k, v in job_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await collection.update_one({"id": job_id}, {"$set": update_data})
        
        updated_job = await collection.find_one({"id": job_id})
        return JobPosting(**updated_job)
    
    async def create_job_from_llm(self, job_data: JobPostingLLMCreate) -> JobPosting:
        """Create a new job posting from LLM extraction (allows null fields)"""
        collection = database_service.get_collection(self.collection_name)
        job_dict = job_data.dict()
        job_obj = JobPosting(**job_dict)
        await collection.insert_one(job_obj.dict())
        return job_obj
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job posting"""
        collection = database_service.get_collection(self.collection_name)
        result = await collection.delete_one({"id": job_id})
        return result.deleted_count > 0


# Global job service instance
job_service = JobService()