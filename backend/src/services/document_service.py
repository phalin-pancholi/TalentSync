"""
Document service for TalentSync backend
"""
import os
import io
from datetime import datetime
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException, UploadFile
import PyPDF2
from docx import Document as DocxDocument

from ..models.document import Document, DocumentCreate, DocumentResponse
from ..services.db_service import get_database


class DocumentService:
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
            self._collection = self.db.documents
        return self._collection
        self.upload_directory = "uploads"
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_directory, exist_ok=True)

    async def create_document(self, candidate_id: str, file: UploadFile) -> str:
        """Create a new document from uploaded file"""
        try:
            # Validate file type
            file_extension = file.filename.split('.')[-1].upper() if file.filename else ""
            if file_extension not in ['PDF', 'DOCX', 'TXT']:
                raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT are allowed.")
            
            # Extract text content
            content = await file.read()
            text_content = await self._extract_text(content, file_extension)
            
            # Save file to disk
            file_path = await self._save_file(content, file.filename, candidate_id)
            
            # Create document record
            document_data = {
                'candidate_id': ObjectId(candidate_id),
                'file_name': file.filename,
                'file_type': file_extension,
                'content_text': text_content,
                'raw_file_path': file_path,
                'upload_date': datetime.utcnow()
            }
            
            result = await self.collection.insert_one(document_data)
            return str(result.inserted_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating document: {str(e)}")

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        try:
            document = await self.collection.find_one({"_id": ObjectId(document_id)})
            if document:
                return Document(**document)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

    async def get_document_by_candidate(self, candidate_id: str) -> Optional[Document]:
        """Get a document by candidate ID"""
        try:
            document = await self.collection.find_one({"candidate_id": ObjectId(candidate_id)})
            if document:
                return Document(**document)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving document by candidate: {str(e)}")

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        try:
            # Get document to find file path
            document = await self.get_document(document_id)
            if document:
                # Delete file from disk
                try:
                    if os.path.exists(document.raw_file_path):
                        os.remove(document.raw_file_path)
                except OSError:
                    pass  # Continue even if file deletion fails
                
                # Delete from database
                result = await self.collection.delete_one({"_id": ObjectId(document_id)})
                return result.deleted_count > 0
            return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

    async def _extract_text(self, content: bytes, file_type: str) -> str:
        """Extract text content from file based on type"""
        try:
            if file_type == 'TXT':
                return content.decode('utf-8')
            
            elif file_type == 'PDF':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
            
            elif file_type == 'DOCX':
                doc = DocxDocument(io.BytesIO(content))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.strip()
            
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            # If text extraction fails, return empty string rather than failing
            print(f"Warning: Text extraction failed for {file_type}: {str(e)}")
            return ""

    async def _save_file(self, content: bytes, filename: str, candidate_id: str) -> str:
        """Save file to disk and return file path"""
        try:
            # Create candidate-specific directory
            candidate_dir = os.path.join(self.upload_directory, candidate_id)
            os.makedirs(candidate_dir, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_extension = filename.split('.')[-1] if filename and '.' in filename else 'bin'
            unique_filename = f"{timestamp}_{filename}"
            
            file_path = os.path.join(candidate_dir, unique_filename)
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return file_path
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    def to_response(self, document: Document) -> DocumentResponse:
        """Convert Document to DocumentResponse"""
        return DocumentResponse(
            id=str(document.id),
            candidate_id=str(document.candidate_id),
            file_name=document.file_name,
            file_type=document.file_type,
            content_text=document.content_text,
            raw_file_path=document.raw_file_path,
            upload_date=document.upload_date
        )

    def generate_profile_summary_pdf(self, candidate_name: str, profile_summary: str) -> bytes:
        """
        Generate a PDF from profile summary text using available libraries
        Since we cannot install new packages, this creates a simple text-based PDF
        """
        try:
            # Create a simple HTML structure
            html_content = f"""
            <html>
            <head>
                <title>Profile Summary - {candidate_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    h2 {{ color: #34495e; margin-top: 25px; margin-bottom: 10px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .content {{ white-space: pre-line; }}
                    .footer {{ margin-top: 50px; text-align: center; font-size: 10px; color: #7f8c8d; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Profile Summary</h1>
                    <h2>{candidate_name}</h2>
                </div>
                <div class="content">
{profile_summary}
                </div>
                <div class="footer">
                    Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC by TalentSync
                </div>
            </body>
            </html>
            """
            
            # For now, return the HTML as text since we cannot install weasyprint or reportlab
            # In a real implementation, this would be converted to PDF
            # As a workaround, we'll create a simple text-based representation
            text_content = f"""
PROFILE SUMMARY
{candidate_name}

{profile_summary}

Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC by TalentSync
"""
            
            # Since we can't create a real PDF, return the text content as bytes
            # This should be replaced with actual PDF generation when proper libraries are available
            return text_content.encode('utf-8')
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating profile summary PDF: {str(e)}")