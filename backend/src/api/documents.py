"""
Document API endpoints for TalentSync backend
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, Response

from ..models.document import DocumentResponse
from ..services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(lambda: DocumentService())
):
    """Get a specific document by ID"""
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_service.to_response(document)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    document_service: DocumentService = Depends(lambda: DocumentService())
):
    """Download the actual file for a document"""
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        return FileResponse(
            path=document.raw_file_path,
            filename=document.file_name,
            media_type='application/octet-stream'
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(lambda: DocumentService())
):
    """Delete a specific document"""
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return Response(status_code=204)