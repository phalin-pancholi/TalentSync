"""
Candidate API endpoints for TalentSync backend
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
import logging
import hashlib

from ..models.candidate import (CandidateCreate, CandidateUpdate, CandidateResponse, 
                               CandidateLLMCreate, CandidateExtraDetailResponse)
from ..services.candidate_service import CandidateService
from ..services.document_service import DocumentService
from ..services.file_parsing_service import FileParsingService
from ..services.llm_extraction_service import LLMExtractionService

logger = logging.getLogger(__name__)

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
    location: Optional[str] = Form(None),  # Added location field
    experience: Optional[str] = Form(None),  # Added experience field
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
            skills=skills_list,
            location=location,
            experience=experience
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
    
    return Response(status_code=204)


@router.post("/{candidate_id}/extra-details", response_model=CandidateExtraDetailResponse)
async def upload_candidate_extra_details(
    candidate_id: str,
    file: UploadFile = File(...),
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """
    Upload extra details for a candidate via document upload
    
    Accepts .txt or .pdf files (max 5MB) and extracts text to store as extra details.
    Text can include interview feedback, new skills, work summary, etc.
    """
    try:
        logger.info(f"Uploading extra details for candidate {candidate_id}: filename={file.filename}")
        
        # Upload and process the extra details
        extra_detail = await candidate_service.upload_extra_details(candidate_id, file)
        
        logger.info(f"Successfully uploaded extra details for candidate {candidate_id}")
        return extra_detail
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    except Exception as e:
        logger.error(f"Unexpected error uploading extra details for candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while uploading extra details"
        )


@router.get("/{candidate_id}/extra-details", response_model=List[CandidateExtraDetailResponse])
async def get_candidate_extra_details(
    candidate_id: str,
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """Get all extra details for a specific candidate"""
    try:
        # Verify candidate exists
        candidate = await candidate_service.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        extra_details = await candidate_service.get_candidate_extra_details(candidate_id)
        return extra_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving extra details for candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while retrieving extra details"
        )


@router.post("/upload", response_model=dict)
async def upload_candidate_document(
    file: UploadFile = File(...),
    candidate_service: CandidateService = Depends(lambda: CandidateService())
):
    """
    Upload a candidate document (resume/CV) and create a candidate entry using LLM extraction
    
    Accepts PDF or text files and uses AI to extract candidate information
    """
    try:
        # Log the upload attempt
        logger.info(f"Processing candidate document upload: filename={file.filename}, content_type={file.content_type}")
        
        # Validate file type
        if not FileParsingService.is_supported_file_type(file.filename):
            logger.warning(f"Unsupported file type uploaded: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported types: {FileParsingService.SUPPORTED_EXTENSIONS}"
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        # Calculate file hash for duplicate detection
        file_hash = hashlib.md5(file_content).hexdigest()
        
        # Check for duplicate documents
        existing_candidate = await candidate_service.get_candidate_by_file_hash(file_hash)
        if existing_candidate:
            logger.info(f"Duplicate document detected for file: {file.filename}")
            return {
                "message": "Document already exists",
                "candidate": candidate_service.to_response(existing_candidate),
                "duplicate": True
            }
        
        # Parse file to extract text
        try:
            text_content = FileParsingService.extract_text_from_file(file_content, file.filename)
            if not text_content.strip():
                raise HTTPException(status_code=400, detail="No text content found in file")
        except ValueError as e:
            logger.error(f"File parsing validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"File parsing error: {str(e)}")
            # Allow manual entry if file parsing fails
            return {
                "message": "Document parsing failed. Please enter candidate details manually.",
                "error": str(e),
                "raw_text": None,
                "parsing_failed": True
            }
        
        # Initialize LLM extraction service (reuse from job page)
        llm_service = LLMExtractionService()
        
        # Check if LLM service is available
        if not llm_service.is_service_available():
            logger.error("LLM service is not available")
            # Allow manual entry if LLM is unavailable
            return {
                "message": "LLM service unavailable. Please enter candidate details manually.",
                "raw_text": text_content,
                "llm_unavailable": True
            }
        
        # Extract candidate information using LLM
        candidate_data = None
        try:
            # We need to modify LLM service to handle candidate extraction
            candidate_data = await llm_service.extract_candidate_info(text_content)
            logger.info(f"LLM extraction successful for file: {file.filename}")
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            # Allow saving with incomplete data
            return {
                "message": "LLM extraction failed. Please review and complete candidate details.",
                "raw_text": text_content,
                "extraction_failed": True,
                "error": str(e)
            }
        
        # Create candidate entry in database (even if some fields are missing)
        try:
            candidate_id = await candidate_service.create_candidate_from_llm(
                candidate_data, text_content, file_hash
            )
            logger.info(f"Candidate created successfully with ID: {candidate_id}")
            
            # Get the created candidate for response
            candidate = await candidate_service.get_candidate(candidate_id)
            
            return {
                "message": "Candidate created successfully from document",
                "candidate": candidate_service.to_response(candidate),
                "raw_text": text_content
            }
        except Exception as e:
            logger.error(f"Database candidate creation failed: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to create candidate entry: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in upload_candidate_document: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred during candidate document upload"
        )


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


@router.post("/{candidate_id}/profile-summary")
async def generate_profile_summary(
    candidate_id: str,
    candidate_service: CandidateService = Depends(lambda: CandidateService()),
    document_service: DocumentService = Depends(lambda: DocumentService()),
    llm_service: LLMExtractionService = Depends(lambda: LLMExtractionService())
):
    """
    Generate a professional profile summary PDF for a candidate using Gemini LLM
    
    Collects all candidate data (structured, unstructured, feedback) and generates
    a comprehensive profile summary document.
    """
    try:
        logger.info(f"Generating profile summary for candidate {candidate_id}")
        
        # Verify candidate exists
        candidate = await candidate_service.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check if LLM service is available
        if not llm_service.is_service_available():
            logger.error("LLM service is not available for profile summary generation")
            raise HTTPException(
                status_code=503, 
                detail="LLM service is currently unavailable. Please try again later."
            )
        
        # Collect all candidate data
        candidate_data = {
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "skills": candidate.skills or [],
            "experience": candidate.experience,
            "education": candidate.education,
            "summary": candidate.summary,
            "raw_text": candidate.raw_text or ""
        }
        
        # Get feedback and extra details
        feedback_data = []
        try:
            extra_details = await candidate_service.get_candidate_extra_details(candidate_id)
            for detail in extra_details:
                if detail.text_content and detail.text_content.strip():
                    feedback_data.append(detail.text_content.strip())
        except Exception as e:
            logger.warning(f"Could not retrieve extra details for candidate {candidate_id}: {str(e)}")
            # Continue without feedback data
        
        # Generate profile summary using LLM
        try:
            profile_summary = await llm_service.generate_profile_summary(
                candidate_data, 
                feedback_data if feedback_data else None
            )
            logger.info(f"Profile summary generated successfully for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Profile summary generation failed for candidate {candidate_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate profile summary: {str(e)}"
            )
        
        # Generate PDF from the summary
        try:
            pdf_content = document_service.generate_profile_summary_pdf(
                candidate.name or "Unknown Candidate",
                profile_summary
            )
            logger.info(f"PDF generated successfully for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"PDF generation failed for candidate {candidate_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PDF: {str(e)}"
            )
        
        # Log the successful profile summary generation for audit
        logger.info(f"Profile summary generated and downloaded for candidate {candidate_id} ({candidate.name})")
        
        # Return PDF as response
        filename = f"profile_summary_{candidate.name or 'candidate'}_{candidate_id[:8]}.pdf"
        filename = filename.replace(" ", "_").replace("/", "_")  # Sanitize filename
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating profile summary for candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the profile summary"
        )