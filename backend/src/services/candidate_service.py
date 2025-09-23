"""
Candidate service for TalentSync backend
"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException, UploadFile
import io

from ..models.candidate import (Candidate, CandidateCreate, CandidateUpdate, CandidateResponse, 
                               CandidateLLMCreate, CandidateExtraDetail, CandidateExtraDetailCreate,
                               CandidateExtraDetailResponse)
from ..models.document import RawTextData
from ..services.db_service import get_database
from ..services.file_parsing_service import FileParsingService


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
    
    @property
    def raw_text_collection(self):
        """Get collection for raw text data"""
        return self.db.raw_text_data

    @property
    def extra_details_collection(self):
        """Get collection for candidate extra details"""
        return self.db.candidate_extra_details

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

    async def create_candidate_from_llm(
        self, 
        candidate_data: CandidateLLMCreate, 
        raw_text: str, 
        file_hash: str
    ) -> str:
        """Create a candidate from LLM extraction with raw text storage"""
        try:
            # Create candidate document with optional fields
            candidate_dict = candidate_data.dict()
            candidate_dict['created_at'] = datetime.utcnow()
            candidate_dict['updated_at'] = datetime.utcnow()
            candidate_dict['raw_text'] = raw_text
            candidate_dict['file_hash'] = file_hash
            
            # Insert candidate
            result = await self.collection.insert_one(candidate_dict)
            candidate_id = result.inserted_id
            
            # Store raw text data separately for future reference
            raw_text_data = {
                'text': raw_text,
                'candidate_id': candidate_id,
                'created_at': datetime.utcnow(),
                'extraction_method': 'LLM',
                'file_hash': file_hash
            }
            await self.raw_text_collection.insert_one(raw_text_data)
            
            return str(candidate_id)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating candidate from LLM: {str(e)}")

    async def get_candidate_by_file_hash(self, file_hash: str) -> Optional[Candidate]:
        """Get a candidate by file hash to detect duplicates"""
        try:
            candidate = await self.collection.find_one({"file_hash": file_hash})
            if candidate:
                return Candidate(**candidate)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving candidate by file hash: {str(e)}")

    def to_response(self, candidate: Candidate) -> CandidateResponse:
        """Convert Candidate to CandidateResponse"""
        return CandidateResponse(
            id=str(candidate.id),
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            skills=candidate.skills,
            experience=getattr(candidate, 'experience', None),
            location=getattr(candidate, 'location', None),  # Added location field
            education=getattr(candidate, 'education', None),
            summary=getattr(candidate, 'summary', None),
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            document_id=str(candidate.document_id) if candidate.document_id else None,
            raw_text=getattr(candidate, 'raw_text', None)
        )

    async def upload_extra_details(self, candidate_id: str, file: UploadFile) -> CandidateExtraDetailResponse:
        """
        Upload and process extra details for a candidate
        
        Args:
            candidate_id: ID of the candidate
            file: Uploaded file containing extra details
            
        Returns:
            CandidateExtraDetailResponse: Created extra detail
            
        Raises:
            HTTPException: If validation fails or processing errors occur
        """
        # Validate candidate exists
        candidate = await self.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not FileParsingService.is_supported_file_type(file.filename):
            raise HTTPException(status_code=415, detail="Unsupported file type. Only .txt and .pdf files are allowed")
        
        # Validate file size (5MB limit)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB")
        
        if len(file_content) == 0:
            raise HTTPException(status_code=422, detail="File is empty")
        
        try:
            # Extract text from file
            text_content = FileParsingService.extract_text_from_file(file_content, file.filename)
            
            if not text_content or len(text_content.strip()) == 0:
                raise HTTPException(status_code=422, detail="Could not extract text from file or file contains no text")
            
            # Determine type based on filename (optional)
            file_type = None
            filename_lower = file.filename.lower()
            if 'feedback' in filename_lower or 'interview' in filename_lower:
                file_type = 'feedback'
            elif 'skill' in filename_lower:
                file_type = 'skills'
            elif 'summary' in filename_lower or 'resume' in filename_lower:
                file_type = 'summary'
            
            # Create extra detail record
            extra_detail_data = {
                'candidate_id': ObjectId(candidate_id),
                'text_content': text_content.strip(),
                'type': file_type,
                'created_at': datetime.utcnow()
            }
            
            result = await self.extra_details_collection.insert_one(extra_detail_data)
            extra_detail_id = str(result.inserted_id)
            
            # Return response
            return CandidateExtraDetailResponse(
                id=extra_detail_id,
                candidate_id=candidate_id,
                text_content=text_content.strip(),
                type=file_type,
                created_at=extra_detail_data['created_at']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    async def get_candidate_extra_details(self, candidate_id: str) -> List[CandidateExtraDetailResponse]:
        """
        Get all extra details for a candidate
        
        Args:
            candidate_id: ID of the candidate
            
        Returns:
            List[CandidateExtraDetailResponse]: List of extra details
        """
        try:
            cursor = self.extra_details_collection.find(
                {"candidate_id": ObjectId(candidate_id)}
            ).sort("created_at", -1)
            
            extra_details = []
            async for detail_doc in cursor:
                extra_details.append(CandidateExtraDetailResponse(
                    id=str(detail_doc['_id']),
                    candidate_id=candidate_id,
                    text_content=detail_doc['text_content'],
                    type=detail_doc.get('type'),
                    created_at=detail_doc['created_at']
                ))
            
            return extra_details
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving extra details: {str(e)}")

    async def to_response_with_extra_details(self, candidate: Candidate) -> CandidateResponse:
        """Convert Candidate to CandidateResponse with extra details included"""
        response = self.to_response(candidate)
        response.extra_details = await self.get_candidate_extra_details(str(candidate.id))
        return response