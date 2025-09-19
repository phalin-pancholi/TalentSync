"""
Service for managing candidate raw data operations
"""
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import uuid
from datetime import datetime
import base64

from ..models.candidate_raw_data import CandidateRawData, FileData, CandidateRawDataResponse
from .db_service import database_service
from .audit_service import audit_logger


class CandidateRawDataService:
    """Service for candidate raw data operations"""
    
    def __init__(self):
        self.collection_name = "candidate_raw_data"
    
    async def upload_candidate_raw_data(self, email: str, files: List[UploadFile]) -> Dict[str, Any]:
        """Upload and store candidate raw data"""
        # Validate files
        validated_files = []
        
        for file in files:
            # Validate file type
            allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported")
            
            # Read file content
            content = await file.read()
            
            # Validate file size (10MB limit)
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 10MB limit")
            
            # Store file in GridFS if large (>16MB), otherwise store as base64
            if len(content) > 16 * 1024 * 1024:
                file_id = await database_service.store_file_gridfs(content, file.filename, file.content_type)
                file_data = FileData(
                    file_name=file.filename,
                    file_type=file.content_type,
                    file_size=len(content),
                    file_data=file_id.encode(),  # Store GridFS ID
                    uploaded_at=datetime.utcnow()
                )
            else:
                file_data = FileData(
                    file_name=file.filename,
                    file_type=file.content_type,
                    file_size=len(content),
                    file_data=base64.b64encode(content),
                    uploaded_at=datetime.utcnow()
                )
            
            validated_files.append(file_data)
        
        # Check if candidate already exists
        collection = database_service.get_collection(self.collection_name)
        existing_candidate = await collection.find_one({"email": email})
        
        if existing_candidate:
            # Update existing candidate with new files
            candidate_id = existing_candidate["candidate_id"]
            await collection.update_one(
                {"candidate_id": candidate_id},
                {
                    "$push": {"raw_files": {"$each": [file.dict() for file in validated_files]}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        else:
            # Create new candidate record
            candidate_data = CandidateRawData(
                email=email,
                raw_files=validated_files
            )
            candidate_id = candidate_data.candidate_id
            
            await collection.insert_one(candidate_data.dict())
        
        # Log the upload operation
        total_size = sum(len(file.file_data) for file in validated_files)
        file_types = list(set(file.file_type for file in validated_files))
        
        await audit_logger.log_file_upload(
            candidate_id=candidate_id,
            file_count=len(validated_files),
            total_size=total_size,
            file_types=file_types,
            status="success"
        )
        
        return {
            "candidate_id": candidate_id,
            "email": email,
            "files_uploaded": len(validated_files),
            "message": "Files uploaded successfully"
        }
    
    async def search_candidate_by_email(self, email: str) -> Optional[CandidateRawDataResponse]:
        """Search candidate raw data by email"""
        collection = database_service.get_collection(self.collection_name)
        candidate = await collection.find_one({"email": email})
        
        if not candidate:
            return None
        
        return CandidateRawDataResponse(
            candidate_id=candidate["candidate_id"],
            email=candidate["email"],
            file_count=len(candidate.get("raw_files", [])),
            created_at=candidate["created_at"]
        )
    
    async def search_candidate_by_id(self, candidate_id: str) -> Optional[CandidateRawDataResponse]:
        """Search candidate raw data by ID"""
        collection = database_service.get_collection(self.collection_name)
        candidate = await collection.find_one({"candidate_id": candidate_id})
        
        if not candidate:
            return None
        
        return CandidateRawDataResponse(
            candidate_id=candidate["candidate_id"],
            email=candidate["email"],
            file_count=len(candidate.get("raw_files", [])),
            created_at=candidate["created_at"]
        )
    
    async def get_candidate_full_data(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get full candidate data including files for LLM processing"""
        collection = database_service.get_collection(self.collection_name)
        candidate = await collection.find_one({"candidate_id": candidate_id})
        
        if not candidate:
            return None
        
        # Decode file contents for LLM processing
        files_content = []
        for file_data in candidate.get("raw_files", []):
            try:
                # Check if it's GridFS ID or base64 content
                if len(file_data["file_data"]) < 100:  # Likely GridFS ID
                    content = await database_service.get_file_gridfs(file_data["file_data"].decode())
                else:
                    content = base64.b64decode(file_data["file_data"])
                
                files_content.append({
                    "filename": file_data["file_name"],
                    "content": content.decode('utf-8', errors='ignore'),  # Convert to text for LLM
                    "type": file_data["file_type"]
                })
            except Exception as e:
                # Log error but continue with other files
                print(f"Error processing file {file_data['file_name']}: {e}")
                continue
        
        return {
            "candidate_id": candidate_id,
            "email": candidate["email"],
            "files": files_content,
            "created_at": candidate["created_at"]
        }


# Global service instance
candidate_raw_data_service = CandidateRawDataService()