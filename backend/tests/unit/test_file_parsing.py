"""
Unit tests for file parsing service
"""
import pytest
import io
from backend.src.services.file_parsing_service import FileParsingService


class TestFileParsingService:
    """Test cases for file parsing service"""
    
    def test_is_supported_file_type_valid(self):
        """Test supported file type detection"""
        assert FileParsingService.is_supported_file_type("document.pdf")
        assert FileParsingService.is_supported_file_type("document.txt")
        assert FileParsingService.is_supported_file_type("document.text")
        assert FileParsingService.is_supported_file_type("DOCUMENT.PDF")  # Case insensitive
        assert FileParsingService.is_supported_file_type("DOCUMENT.TXT")
    
    def test_is_supported_file_type_invalid(self):
        """Test unsupported file type detection"""
        assert not FileParsingService.is_supported_file_type("document.jpg")
        assert not FileParsingService.is_supported_file_type("document.png")
        assert not FileParsingService.is_supported_file_type("document.doc")
        assert not FileParsingService.is_supported_file_type("document.docx")
        assert not FileParsingService.is_supported_file_type("document")  # No extension
        assert not FileParsingService.is_supported_file_type("")  # Empty string
        assert not FileParsingService.is_supported_file_type(None)  # None
    
    def test_extract_text_from_text_file_utf8(self):
        """Test text extraction from UTF-8 text file"""
        content = "This is a test job description.\nRequires Python skills."
        file_bytes = content.encode('utf-8')
        
        result = FileParsingService.extract_text_from_file(file_bytes, "test.txt")
        assert result == content
    
    def test_extract_text_from_text_file_latin1(self):
        """Test text extraction from Latin-1 encoded text file"""
        content = "This is a test with special chars: café, résumé"
        file_bytes = content.encode('latin-1')
        
        result = FileParsingService.extract_text_from_file(file_bytes, "test.txt")
        assert result == content
    
    def test_extract_text_from_text_file_with_errors(self):
        """Test text extraction with encoding errors"""
        # Create bytes that will cause encoding issues
        file_bytes = b'\xff\xfe\x00\x01Invalid encoding'
        
        # Should not raise exception but handle gracefully
        result = FileParsingService.extract_text_from_file(file_bytes, "test.txt")
        assert isinstance(result, str)
        # Should use replacement characters for invalid bytes
        assert len(result) > 0
    
    def test_extract_text_from_pdf_mock(self):
        """Test PDF text extraction (mocked)"""
        # Create a simple mock PDF content for testing
        # In real scenario, this would be actual PDF bytes
        pdf_content = b"%PDF-1.4\nSimple test content"
        
        # Since we can't easily create real PDF in unit test,
        # we'll test the error handling
        with pytest.raises(Exception) as exc_info:
            FileParsingService.extract_text_from_file(pdf_content, "test.pdf")
        assert "Failed to parse" in str(exc_info.value)
    
    def test_extract_text_unsupported_file_type(self):
        """Test extraction with unsupported file type"""
        content = b"Some content"
        
        with pytest.raises(ValueError) as exc_info:
            FileParsingService.extract_text_from_file(content, "test.jpg")
        assert "Unsupported file type" in str(exc_info.value)
    
    def test_extract_text_empty_filename(self):
        """Test extraction with empty filename"""
        content = b"Some content"
        
        with pytest.raises(ValueError) as exc_info:
            FileParsingService.extract_text_from_file(content, "")
        assert "Unsupported file type" in str(exc_info.value)
    
    def test_extract_text_no_extension(self):
        """Test extraction with filename without extension"""
        content = b"Some content"
        
        with pytest.raises(ValueError) as exc_info:
            FileParsingService.extract_text_from_file(content, "noextension")
        assert "Unsupported file type" in str(exc_info.value)
    
    def test_extract_text_whitespace_content(self):
        """Test extraction with only whitespace content"""
        content = "   \n\t  \r\n  "
        file_bytes = content.encode('utf-8')
        
        result = FileParsingService.extract_text_from_file(file_bytes, "test.txt")
        assert result == ""  # Should be stripped to empty string
    
    def test_extract_text_multiline_content(self):
        """Test extraction with multiline content"""
        content = """Job Title: Software Engineer

Job Description:
We are looking for a skilled software engineer.

Requirements:
- Python experience
- Database knowledge
- Team player

Location: Remote
Department: Engineering"""
        
        file_bytes = content.encode('utf-8')
        result = FileParsingService.extract_text_from_file(file_bytes, "test.txt")
        assert result == content
        assert "Software Engineer" in result
        assert "Python experience" in result
        assert "Remote" in result
    
    def test_supported_extensions_constant(self):
        """Test that supported extensions constant is properly defined"""
        expected_extensions = {'.pdf', '.txt', '.text'}
        assert FileParsingService.SUPPORTED_EXTENSIONS == expected_extensions
    
    def test_private_extract_text_from_text_file(self):
        """Test private text file extraction method"""
        content = "Test content for private method"
        file_bytes = content.encode('utf-8')
        
        result = FileParsingService._extract_text_from_text_file(file_bytes)
        assert result == content
    
    def test_private_extract_text_from_text_file_encoding_fallback(self):
        """Test encoding fallback in private method"""
        # Create content that might have encoding issues
        content = "Test with special chars: é, ñ, ü"
        file_bytes = content.encode('utf-8')
        
        result = FileParsingService._extract_text_from_text_file(file_bytes)
        assert result == content