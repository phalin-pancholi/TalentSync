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
        Generate a PDF from profile summary text using basic PDF format
        Creates a minimal but valid PDF document without external libraries
        """
        try:
            # Escape special characters for PDF
            def escape_pdf_string(text):
                if not text:
                    return ""
                return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            
            candidate_name_escaped = escape_pdf_string(candidate_name or "Unknown Candidate")
            
            # Split long text into lines (approximate 70 chars per line for readability)
            def split_text_to_lines(text, max_chars=70):
                if not text:
                    return ["No summary available"]
                
                # Split by existing newlines first
                paragraphs = text.split('\n')
                lines = []
                
                for paragraph in paragraphs:
                    if not paragraph.strip():
                        lines.append("")  # Keep empty lines for spacing
                        continue
                        
                    words = paragraph.split()
                    current_line = ""
                    
                    for word in words:
                        if len(current_line + " " + word) <= max_chars:
                            current_line += " " + word if current_line else word
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                
                return lines if lines else ["No summary available"]
            
            # Create PDF content using basic PDF format
            pdf_lines = split_text_to_lines(profile_summary, 70)
            
            # Calculate approximate object sizes
            content_lines = []
            content_lines.append("PROFILE SUMMARY")
            content_lines.append("")
            content_lines.append(candidate_name or "Unknown Candidate")
            content_lines.append("")
            content_lines.extend(pdf_lines)
            content_lines.append("")
            content_lines.append(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC by TalentSync")
            
            # Create page content stream with proper PDF text formatting
            page_content = "BT\n"
            page_content += "/F1 16 Tf\n"  # Set font size 16
            page_content += "50 750 Td\n"  # Position for title
            
            y_position = 750
            for i, line in enumerate(content_lines):
                if line == "PROFILE SUMMARY":
                    page_content += "/F1 16 Tf\n"
                    page_content += f"({escape_pdf_string(line)}) Tj\n"
                elif line == candidate_name:
                    page_content += "/F1 14 Tf\n" 
                    page_content += f"({escape_pdf_string(line)}) Tj\n"
                elif line.strip():  # Only process non-empty lines
                    page_content += "/F1 10 Tf\n"
                    page_content += f"({escape_pdf_string(line)}) Tj\n"
                
                # Move to next line
                if i < len(content_lines) - 1:  # Don't move after last line
                    page_content += "0 -15 Td\n"  # Move down 15 points
                    y_position -= 15
                    
                    if y_position < 50:  # If near bottom of page, stop
                        break
            
            page_content += "\nET"
            
            # Basic PDF structure
            pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length {len(page_content)}
>>
stream
{page_content}
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000356 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
{456 + len(page_content)}
%%EOF"""
            
            return pdf_content.encode('utf-8')
            
        except Exception as e:
            # Fallback: return a very basic PDF with error message
            def simple_escape(text):
                if not text:
                    return ""
                return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            
            error_msg = f"Error generating PDF: {str(e)}"
            candidate_safe = simple_escape(candidate_name or "Unknown")[:50]  # Limit length
            error_safe = simple_escape(error_msg)[:100]  # Limit length
            
            basic_pdf = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 120>>stream
BT
/F1 12 Tf
50 750 Td
(Profile Summary - {candidate_safe}) Tj
0 -20 Td
({error_safe}) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000356 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
440
%%EOF"""
            return basic_pdf.encode('utf-8')