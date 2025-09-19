"""
API endpoints for candidate raw data and profile generation
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
import io

from ..models.candidate_raw_data import CandidateRawDataRequest, CandidateRawDataResponse, ProfileGenerationResponse
from ..services.candidate_raw_data_service import candidate_raw_data_service
from ..services.gemini_llm_service import profile_summary_service
from ..services.pdf_generation_service import pdf_generation_service

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/raw", response_model=dict, status_code=201)
async def upload_candidate_raw_data(
    email: str,
    files: List[UploadFile] = File(...)
):
    """Upload candidate raw data (resume, feedback, etc.)"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        result = await candidate_raw_data_service.upload_candidate_raw_data(email, files)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading candidate raw data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/raw/search", response_model=CandidateRawDataResponse)
async def search_candidate_raw_data(
    email: Optional[str] = Query(None),
    candidate_id: Optional[str] = Query(None)
):
    """Search candidate raw data by email or candidate ID"""
    try:
        if not email and not candidate_id:
            raise HTTPException(status_code=400, detail="Either email or candidate_id must be provided")
        
        if email:
            candidate = await candidate_raw_data_service.search_candidate_by_email(email)
        else:
            candidate = await candidate_raw_data_service.search_candidate_by_id(candidate_id)
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error searching candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{candidate_id}/generate-profile")
async def generate_profile_summary(candidate_id: str):
    """Generate profile summary PDF using Gemini LLM"""
    try:
        # Get candidate data
        candidate_data = await candidate_raw_data_service.get_candidate_full_data(candidate_id)
        if not candidate_data:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Generate profile summary using LLM
        profile_summary = await profile_summary_service.create_profile_summary(candidate_id, candidate_data)
        
        if profile_summary.status == "error":
            raise HTTPException(
                status_code=500, 
                detail=f"Profile generation failed: {profile_summary.error_message}"
            )
        
        # Generate PDF
        try:
            pdf_data = pdf_generation_service.generate_profile_pdf(
                profile_summary, 
                candidate_data["email"]
            )
            
            # Return PDF as streaming response
            pdf_stream = io.BytesIO(pdf_data)
            
            return StreamingResponse(
                io.BytesIO(pdf_data),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=profile_{candidate_id}.pdf"
                }
            )
            
        except Exception as pdf_error:
            logging.error(f"PDF generation error: {str(pdf_error)}")
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating profile for candidate {candidate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")