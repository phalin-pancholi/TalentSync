import pytest
from unittest.mock import mock_open, patch, MagicMock
import io
from bson import ObjectId
from datetime import datetime, timezone

from src.services.candidate_service import CandidateService
from src.services.file_parsing_service import FileParsingService
from src.models.candidate import CandidateExtraDetailResponse
from fastapi import HTTPException, UploadFile


class TestCandidateExtraDetailsService:
    """Unit tests for candidate extra details upload and text extraction"""
    
    @pytest.fixture
    def candidate_service(self):
        return CandidateService()
    
    @pytest.fixture
    def mock_candidate(self):
        return {
            '_id': ObjectId(),
            'name': 'Test Candidate',
            'email': 'test@example.com',
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    
    @pytest.fixture
    def mock_upload_file(self):
        file_content = b"This is test interview feedback content for the candidate."
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "interview_feedback.txt"
        mock_file.read.return_value = file_content
        return mock_file, file_content
    
    @patch('src.services.candidate_service.FileParsingService')
    @patch.object(CandidateService, 'get_candidate')
    @patch.object(CandidateService, 'extra_details_collection')
    async def test_upload_extra_details_text_file(self, mock_collection, mock_get_candidate, mock_parser, candidate_service, mock_candidate, mock_upload_file):
        """Test uploading a text file as extra details"""
        mock_file, file_content = mock_upload_file
        candidate_id = str(mock_candidate['_id'])
        
        # Setup mocks
        from src.models.candidate import Candidate
        mock_get_candidate.return_value = Candidate(**mock_candidate)
        mock_parser.is_supported_file_type.return_value = True
        mock_parser.extract_text_from_file.return_value = "Extracted interview feedback content"
        
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_insert_result
        
        # Execute
        result = await candidate_service.upload_extra_details(candidate_id, mock_file)
        
        # Verify
        assert isinstance(result, CandidateExtraDetailResponse)
        assert result.candidate_id == candidate_id
        assert result.text_content == "Extracted interview feedback content"
        assert result.type == "feedback"  # Should be detected from filename
        
        # Verify file parsing was called
        mock_parser.is_supported_file_type.assert_called_once_with("interview_feedback.txt")
        mock_parser.extract_text_from_file.assert_called_once_with(file_content, "interview_feedback.txt")
        
        # Verify database insert
        mock_collection.insert_one.assert_called_once()
        insert_data = mock_collection.insert_one.call_args[0][0]
        assert insert_data['candidate_id'] == ObjectId(candidate_id)
        assert insert_data['text_content'] == "Extracted interview feedback content"
        assert insert_data['type'] == "feedback"
    
    @patch.object(CandidateService, 'get_candidate')
    async def test_upload_extra_details_candidate_not_found(self, mock_get_candidate, candidate_service, mock_upload_file):
        """Test upload fails when candidate doesn't exist"""
        mock_file, _ = mock_upload_file
        mock_get_candidate.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await candidate_service.upload_extra_details("non-existent-id", mock_file)
        
        assert exc_info.value.status_code == 404
        assert "Candidate not found" in exc_info.value.detail
    
    @patch('src.services.candidate_service.FileParsingService')
    @patch.object(CandidateService, 'get_candidate')
    async def test_upload_extra_details_unsupported_file_type(self, mock_get_candidate, mock_parser, candidate_service, mock_candidate):
        """Test upload fails with unsupported file type"""
        from src.models.candidate import Candidate
        mock_get_candidate.return_value = Candidate(**mock_candidate)
        mock_parser.is_supported_file_type.return_value = False
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.read.return_value = b"fake image content"
        
        with pytest.raises(HTTPException) as exc_info:
            await candidate_service.upload_extra_details(str(mock_candidate['_id']), mock_file)
        
        assert exc_info.value.status_code == 415
        assert "Unsupported file type" in exc_info.value.detail
    
    @patch('src.services.candidate_service.FileParsingService')
    @patch.object(CandidateService, 'get_candidate')
    async def test_upload_extra_details_file_too_large(self, mock_get_candidate, mock_parser, candidate_service, mock_candidate):
        """Test upload fails when file is too large"""
        from src.models.candidate import Candidate
        mock_get_candidate.return_value = Candidate(**mock_candidate)
        mock_parser.is_supported_file_type.return_value = True
        
        # Create a file larger than 5MB
        large_content = b"x" * (5 * 1024 * 1024 + 1)
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "large_file.txt"
        mock_file.read.return_value = large_content
        
        with pytest.raises(HTTPException) as exc_info:
            await candidate_service.upload_extra_details(str(mock_candidate['_id']), mock_file)
        
        assert exc_info.value.status_code == 413
        assert "File too large" in exc_info.value.detail
    
    @patch('src.services.candidate_service.FileParsingService')
    @patch.object(CandidateService, 'get_candidate')
    async def test_upload_extra_details_empty_file(self, mock_get_candidate, mock_parser, candidate_service, mock_candidate):
        """Test upload fails when file is empty"""
        from src.models.candidate import Candidate
        mock_get_candidate.return_value = Candidate(**mock_candidate)
        mock_parser.is_supported_file_type.return_value = True
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "empty.txt"
        mock_file.read.return_value = b""
        
        with pytest.raises(HTTPException) as exc_info:
            await candidate_service.upload_extra_details(str(mock_candidate['_id']), mock_file)
        
        assert exc_info.value.status_code == 422
        assert "empty" in exc_info.value.detail.lower()
    
    @patch('src.services.candidate_service.FileParsingService')
    @patch.object(CandidateService, 'get_candidate')
    async def test_upload_extra_details_text_extraction_failure(self, mock_get_candidate, mock_parser, candidate_service, mock_candidate):
        """Test upload fails when text extraction fails"""
        from src.models.candidate import Candidate
        mock_get_candidate.return_value = Candidate(**mock_candidate)
        mock_parser.is_supported_file_type.return_value = True
        mock_parser.extract_text_from_file.side_effect = Exception("PDF parsing failed")
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "corrupted.pdf"
        mock_file.read.return_value = b"corrupted pdf content"
        
        with pytest.raises(HTTPException) as exc_info:
            await candidate_service.upload_extra_details(str(mock_candidate['_id']), mock_file)
        
        assert exc_info.value.status_code == 500
        assert "Error processing file" in exc_info.value.detail
    
    @patch('src.services.candidate_service.FileParsingService')
    @patch.object(CandidateService, 'get_candidate')
    async def test_upload_extra_details_empty_extracted_text(self, mock_get_candidate, mock_parser, candidate_service, mock_candidate):
        """Test upload fails when extracted text is empty"""
        from src.models.candidate import Candidate
        mock_get_candidate.return_value = Candidate(**mock_candidate)
        mock_parser.is_supported_file_type.return_value = True
        mock_parser.extract_text_from_file.return_value = "   "  # Only whitespace
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "whitespace.txt"
        mock_file.read.return_value = b"   "
        
        with pytest.raises(HTTPException) as exc_info:
            await candidate_service.upload_extra_details(str(mock_candidate['_id']), mock_file)
        
        assert exc_info.value.status_code == 422
        assert "no text" in exc_info.value.detail.lower()
    
    def test_file_type_detection(self, candidate_service):
        """Test automatic file type detection from filename"""
        test_cases = [
            ("interview_feedback.txt", "feedback"),
            ("feedback_form.pdf", "feedback"),
            ("new_skills.txt", "skills"),
            ("skill_assessment.pdf", "skills"),
            ("work_summary.txt", "summary"),
            ("resume_update.pdf", "summary"),
            ("random_document.txt", None)
        ]
        
        for filename, expected_type in test_cases:
            filename_lower = filename.lower()
            detected_type = None
            
            if 'feedback' in filename_lower or 'interview' in filename_lower:
                detected_type = 'feedback'
            elif 'skill' in filename_lower:
                detected_type = 'skills'
            elif 'summary' in filename_lower or 'resume' in filename_lower:
                detected_type = 'summary'
            
            assert detected_type == expected_type, f"Failed for filename: {filename}"


class TestFileParsingServiceUnit:
    """Additional unit tests for file parsing service"""
    
    def test_extract_text_from_simple_text_file(self):
        """Test extracting text from a simple text file"""
        content = b"This is a simple text file with candidate feedback."
        result = FileParsingService.extract_text_from_file(content, "feedback.txt")
        assert result == "This is a simple text file with candidate feedback."
    
    def test_extract_text_handles_unicode(self):
        """Test text extraction handles unicode characters"""
        content = "Excellent candidate with strong résumé and naïve approach.".encode('utf-8')
        result = FileParsingService.extract_text_from_file(content, "feedback.txt")
        assert "résumé" in result
        assert "naïve" in result
    
    def test_unsupported_file_type_check(self):
        """Test file type support checking"""
        assert FileParsingService.is_supported_file_type("document.pdf") == True
        assert FileParsingService.is_supported_file_type("document.txt") == True
        assert FileParsingService.is_supported_file_type("document.text") == True
        assert FileParsingService.is_supported_file_type("image.jpg") == False
        assert FileParsingService.is_supported_file_type("document.docx") == False
        assert FileParsingService.is_supported_file_type("") == False
        assert FileParsingService.is_supported_file_type("no_extension") == False