"""
Matching service for TalentSync backend
"""
from typing import List

from ..models.candidate import Candidate
from ..models.job_posting import JobPosting
from ..services.candidate_service import CandidateService


class MatchingService:
    """Service for matching candidates to job postings"""
    
    def __init__(self):
        self.candidate_service = CandidateService()
    
    async def get_candidates_for_job(self, job: JobPosting) -> List[Candidate]:
        """Get candidates matching a job posting with minimum 20% match score"""
        # Get all candidates from database
        all_candidates = await self.candidate_service.get_candidates(skip=0, limit=1000)
        
        job_skills = set(job.skills) if job.skills else set()
        candidates_with_match = []
        
        for candidate in all_candidates:
            candidate_skills = set(candidate.skills) if candidate.skills else set()
            matched_skills = list(job_skills.intersection(candidate_skills))
            match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
            
            # Only include candidates with match percentage > 20%
            if match_percentage > 20:
                # Update candidate with match information
                candidate.match_percentage = round(match_percentage, 1)
                candidate.matched_skills = matched_skills
                candidates_with_match.append(candidate)
        
        # Sort by match percentage (highest first)
        candidates_with_match.sort(key=lambda x: x.match_percentage, reverse=True)
        return candidates_with_match


# Global matching service instance
matching_service = MatchingService()