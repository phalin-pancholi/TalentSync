"""
File parsing service for TalentSync backend
Handles parsing of PDF and text files for job description extraction
"""
import io
from typing import Union, BinaryIO
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)


class FileParsingService:
    """Service for parsing uploaded files to extract text content"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.text'}
    
    @classmethod
    def is_supported_file_type(cls, filename: str) -> bool:
        """Check if the file type is supported for parsing"""
        if not filename:
            return False
        
        # Get file extension
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return f'.{extension}' in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def extract_text_from_file(cls, file_content: bytes, filename: str) -> str:
        """
        Extract text content from uploaded file
        
        Args:
            file_content: Raw bytes content of the file
            filename: Name of the uploaded file
            
        Returns:
            str: Extracted text content
            
        Raises:
            ValueError: If file type is not supported
            Exception: If file parsing fails
        """
        if not cls.is_supported_file_type(filename):
            raise ValueError(f"Unsupported file type. Supported types: {cls.SUPPORTED_EXTENSIONS}")
        
        try:
            # Get file extension
            extension = filename.lower().split('.')[-1] if '.' in filename else ''
            
            if extension == 'pdf':
                return cls._extract_text_from_pdf(file_content)
            elif extension in ['txt', 'text']:
                return cls._extract_text_from_text_file(file_content)
            else:
                raise ValueError(f"Unsupported file extension: .{extension}")
                
        except Exception as e:
            logger.error(f"Failed to parse file {filename}: {str(e)}")
            raise Exception(f"Failed to parse file: {str(e)}")
    
    @classmethod
    def _extract_text_from_pdf(cls, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            # Create a file-like object from bytes
            pdf_file = io.BytesIO(file_content)
            
            # Read PDF using PyPDF2
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    @classmethod
    def _extract_text_from_text_file(cls, file_content: bytes) -> str:
        """Extract text from text file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    return file_content.decode(encoding).strip()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 with error handling
            return file_content.decode('utf-8', errors='replace').strip()
            
        except Exception as e:
            raise Exception(f"Failed to parse text file: {str(e)}")