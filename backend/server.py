from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class JobPosting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    skills: List[str]
    experience_level: str
    department: str
    location: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobPostingCreate(BaseModel):
    title: str
    description: str
    skills: List[str]
    experience_level: str
    department: str
    location: str

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None

class Candidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    skills: List[str]
    experience_years: int
    current_role: str
    department: str
    location: str
    match_percentage: float = 0.0
    matched_skills: List[str] = []

# Dummy candidates data
DUMMY_CANDIDATES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Alice Johnson",
        "email": "alice.johnson@company.com",
        "skills": ["Python", "React", "MongoDB", "FastAPI", "Machine Learning"],
        "experience_years": 5,
        "current_role": "Senior Full Stack Developer",
        "department": "Engineering",
        "location": "New York"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Bob Smith",
        "email": "bob.smith@company.com",
        "skills": ["Java", "Spring Boot", "PostgreSQL", "Docker", "Kubernetes"],
        "experience_years": 7,
        "current_role": "DevOps Engineer",
        "department": "Engineering",
        "location": "San Francisco"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Carol Davis",
        "email": "carol.davis@company.com",
        "skills": ["React", "Vue.js", "TypeScript", "CSS", "UI/UX Design"],
        "experience_years": 4,
        "current_role": "Frontend Developer",
        "department": "Engineering",
        "location": "Remote"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "David Wilson",
        "email": "david.wilson@company.com",
        "skills": ["Python", "Django", "PostgreSQL", "AWS", "Data Analysis"],
        "experience_years": 6,
        "current_role": "Backend Developer",
        "department": "Engineering",
        "location": "Austin"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Emma Brown",
        "email": "emma.brown@company.com",
        "skills": ["Project Management", "Agile", "Scrum", "Team Leadership"],
        "experience_years": 8,
        "current_role": "Project Manager",
        "department": "Operations",
        "location": "Chicago"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Frank Miller",
        "email": "frank.miller@company.com",
        "skills": ["Node.js", "Express", "MongoDB", "GraphQL", "API Design"],
        "experience_years": 5,
        "current_role": "Backend Developer",
        "department": "Engineering",
        "location": "Seattle"
    }
]

# Job posting endpoints
@api_router.get("/jobs", response_model=List[JobPosting])
async def get_jobs():
    jobs = await db.job_postings.find().to_list(1000)
    return [JobPosting(**job) for job in jobs]

@api_router.post("/jobs", response_model=JobPosting)
async def create_job(job: JobPostingCreate):
    job_dict = job.dict()
    job_obj = JobPosting(**job_dict)
    await db.job_postings.insert_one(job_obj.dict())
    return job_obj

@api_router.get("/jobs/{job_id}", response_model=JobPosting)
async def get_job(job_id: str):
    job = await db.job_postings.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobPosting(**job)

@api_router.put("/jobs/{job_id}", response_model=JobPosting)
async def update_job(job_id: str, job_update: JobPostingUpdate):
    job = await db.job_postings.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_data = {k: v for k, v in job_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.job_postings.update_one({"id": job_id}, {"$set": update_data})
    
    updated_job = await db.job_postings.find_one({"id": job_id})
    return JobPosting(**updated_job)

@api_router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    result = await db.job_postings.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

# File upload endpoint
@api_router.post("/jobs/upload")
async def upload_job_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and Word documents are allowed")
    
    # In a real application, you would parse the document content
    # For now, we'll return dummy job data
    dummy_job = {
        "title": f"Senior Software Engineer - From {file.filename}",
        "description": f"Position extracted from uploaded document: {file.filename}. This is a senior-level software engineering role requiring strong technical skills and leadership experience.",
        "skills": ["Python", "React", "MongoDB", "Team Leadership", "System Design"],
        "experience_level": "Senior",
        "department": "Engineering",
        "location": "New York"
    }
    
    job_obj = JobPosting(**dummy_job)
    await db.job_postings.insert_one(job_obj.dict())
    return job_obj

# Candidate matching endpoint
@api_router.get("/jobs/{job_id}/candidates", response_model=List[Candidate])
async def get_candidates_for_job(job_id: str):
    job = await db.job_postings.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_skills = set(job["skills"])
    candidates_with_match = []
    
    for candidate_data in DUMMY_CANDIDATES:
        candidate_skills = set(candidate_data["skills"])
        matched_skills = list(job_skills.intersection(candidate_skills))
        match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
        
        candidate = Candidate(
            **candidate_data,
            match_percentage=round(match_percentage, 1),
            matched_skills=matched_skills
        )
        candidates_with_match.append(candidate)
    
    # Sort by match percentage (highest first)
    candidates_with_match.sort(key=lambda x: x.match_percentage, reverse=True)
    return candidates_with_match

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()