"""
Candidate service for TalentSync backend
"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException

from ..models.candidate import Candidate, CandidateCreate, CandidateUpdate, CandidateResponse
from ..services.db_service import get_database


class CandidateService:
    def __init__(self):
        self._db = None
        self._collection = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.candidates
        return self._collection

    async def create_candidate(self, candidate_data: CandidateCreate, document_id: Optional[str] = None) -> str:
        """Create a new candidate"""
        try:
            candidate_dict = candidate_data.dict()
            candidate_dict['created_at'] = datetime.utcnow()
            candidate_dict['updated_at'] = datetime.utcnow()
            
            if document_id:
                candidate_dict['document_id'] = ObjectId(document_id)
            
            result = await self.collection.insert_one(candidate_dict)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise HTTPException(status_code=400, detail="Email already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating candidate: {str(e)}")

    async def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        """Get a candidate by ID"""
        try:
            candidate = await self.collection.find_one({"_id": ObjectId(candidate_id)})
            if candidate:
                return Candidate(**candidate)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving candidate: {str(e)}")

    async def get_candidates(self, skip: int = 0, limit: int = 100) -> List[Candidate]:
        """Get all candidates with pagination"""
        try:
            cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            candidate_docs = await cursor.to_list(length=limit)
            candidates = []
            for candidate_doc in candidate_docs:
                candidates.append(Candidate(**candidate_doc))
            return candidates
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving candidates: {str(e)}")

    async def update_candidate(self, candidate_id: str, candidate_update: CandidateUpdate) -> Optional[Candidate]:
        """Update a candidate"""
        try:
            update_data = candidate_update.dict(exclude_unset=True)
            if update_data:
                update_data['updated_at'] = datetime.utcnow()
                
                # Check for email uniqueness if email is being updated
                if 'email' in update_data:
                    existing = await self.collection.find_one({
                        "email": update_data['email'],
                        "_id": {"$ne": ObjectId(candidate_id)}
                    })
                    if existing:
                        raise HTTPException(status_code=400, detail="Email already exists")
                
                result = await self.collection.find_one_and_update(
                    {"_id": ObjectId(candidate_id)},
                    {"$set": update_data},
                    return_document=True
                )
                
                if result:
                    return Candidate(**result)
            return None
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating candidate: {str(e)}")

    async def delete_candidate(self, candidate_id: str) -> bool:
        """Delete a candidate"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(candidate_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting candidate: {str(e)}")

    async def search_candidates(self, query: str, skills: Optional[List[str]] = None) -> List[Candidate]:
        """Search candidates by name, email, or skills"""
        try:
            search_filter = {}
            
            if query:
                search_filter["$or"] = [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}}
                ]
            
            if skills:
                if "$and" not in search_filter:
                    search_filter["$and"] = []
                search_filter["$and"].append({"skills": {"$in": skills}})
            
            cursor = self.collection.find(search_filter).sort("created_at", -1)
            candidates = []
            for candidate_doc in cursor:
                candidates.append(Candidate(**candidate_doc))
            return candidates
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching candidates: {str(e)}")

    async def get_candidate_by_email(self, email: str) -> Optional[Candidate]:
        """Get a candidate by email"""
        try:
            candidate = await self.collection.find_one({"email": email})
            if candidate:
                return Candidate(**candidate)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving candidate by email: {str(e)}")

    def to_response(self, candidate: Candidate) -> CandidateResponse:
        """Convert Candidate to CandidateResponse"""
        return CandidateResponse(
            id=str(candidate.id),
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            skills=candidate.skills,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            document_id=str(candidate.document_id) if candidate.document_id else None
        )