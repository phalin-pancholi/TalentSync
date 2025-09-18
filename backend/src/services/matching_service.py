"""
Matching service for TalentSync backend
"""
from typing import List
import uuid

from ..models.candidate import Candidate
from ..models.job_posting import JobPosting


class MatchingService:
    """Service for matching candidates to job postings"""
    
    def __init__(self):
        # Dummy candidates data for now
        self.dummy_candidates = [
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
    
    async def get_candidates_for_job(self, job: JobPosting) -> List[Candidate]:
        """Get candidates matching a job posting"""
        job_skills = set(job.skills)
        candidates_with_match = []
        
        for candidate_data in self.dummy_candidates:
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


# Global matching service instance
matching_service = MatchingService()