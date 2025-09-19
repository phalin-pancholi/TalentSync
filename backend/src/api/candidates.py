"""
Candidate API endpoints for TalentSync backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from ..models.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from ..services.candidate_service import CandidateService
from ..services.document_service import DocumentService

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """Get all candidates with pagination"""
    candidates = await candidate_service.get_candidates(skip=skip, limit=limit)
    return [candidate_service.to_response(candidate) for candidate in candidates]


@router.post("/", response_model=dict)
async def create_candidate(
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    skills: str = Form(...),  # Comma-separated skills
    document: Optional[UploadFile] = File(None),
    candidate_service: CandidateService = Depends(lambda: CandidateService()),
    document_service: DocumentService = Depends(lambda: DocumentService())
):
    """Create a new candidate with optional document upload"""
    try:
        # Parse skills from comma-separated string
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        
        candidate_data = CandidateCreate(
            name=name,
            email=email,
            phone=phone,
            skills=skills_list
        )
        
        # Create candidate first
        candidate_id = await candidate_service.create_candidate(candidate_data)
        
        # If document is provided, upload it
        document_id = None
        if document and document.filename:
            document_id = await document_service.create_document(candidate_id, document)
            
            # Update candidate with document_id
            await candidate_service.update_candidate(
                candidate_id, 
                CandidateUpdate(document_id=document_id)
            )
        
        return {
            "id": candidate_id,
            "message": "Candidate created successfully",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating candidate: {str(e)}")


@router.post("/json", response_model=dict)
async def create_candidate_json(
    candidate_data: CandidateCreate,
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """Create a new candidate from JSON data"""
    candidate_id = await candidate_service.create_candidate(candidate_data)
    return {
        "id": candidate_id,
        "message": "Candidate created successfully"
    }


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: str,
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """Get a specific candidate by ID"""
    candidate = await candidate_service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_service.to_response(candidate)


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: str,
    candidate_update: CandidateUpdate,
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """Update a specific candidate"""
    candidate = await candidate_service.update_candidate(candidate_id, candidate_update)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_service.to_response(candidate)


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    candidate_service: CandidateService = Depends(lambda: CandidateService()),
    document_service: DocumentService = Depends(lambda: DocumentService())
):
    """Delete a specific candidate and associated documents"""
    # First delete associated document if exists
    document = await document_service.get_document_by_candidate(candidate_id)
    if document:
        await document_service.delete_document(str(document.id))
    
    # Then delete candidate
    success = await candidate_service.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return JSONResponse(status_code=204, content={"message": "Candidate deleted successfully"})


@router.get("/search/", response_model=List[CandidateResponse])
async def search_candidates(
    q: Optional[str] = None,
    skills: Optional[str] = None,
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """Search candidates by name, email, or skills"""
    skills_list = None
    if skills:
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
    
    candidates = await candidate_service.search_candidates(q or "", skills_list)
    return [candidate_service.to_response(candidate) for candidate in candidates]