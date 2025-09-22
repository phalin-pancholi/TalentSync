"""
Unit tests for LLM extraction service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from backend.src.services.llm_extraction_service import LLMExtractionService
from backend.src.models.job_posting import JobPostingLLMCreate


class TestLLMExtractionService:
    """Test cases for LLM extraction service"""
    
    def test_init_without_api_key(self):
        """Test initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            service = LLMExtractionService()
            assert service.llm is None
            assert not service.is_service_available()
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            with patch('backend.src.services.llm_extraction_service.ChatGoogleGenerativeAI') as mock_llm:
                service = LLMExtractionService()
                assert service.api_key == 'test_key'
                mock_llm.assert_called_once()
    
    def test_extract_job_info_without_llm(self):
        """Test extraction when LLM is not available"""
        service = LLMExtractionService()
        service.llm = None
        
        with pytest.raises(Exception) as exc_info:
            service.extract_job_info("test content")
        assert "LLM service is not available" in str(exc_info.value)
    
    def test_extract_job_info_empty_content(self):
        """Test extraction with empty content"""
        service = LLMExtractionService()
        service.llm = Mock()
        
        with pytest.raises(ValueError) as exc_info:
            service.extract_job_info("")
        assert "Empty text content" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            service.extract_job_info("   \n\t  ")
        assert "Empty text content" in str(exc_info.value)
    
    @patch('backend.src.services.llm_extraction_service.ChatGoogleGenerativeAI')
    def test_extract_job_info_success(self, mock_llm_class):
        """Test successful job information extraction"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = json.dumps({
            "title": "Software Engineer",
            "description": "A great job",
            "skills": ["Python", "JavaScript"],
            "experience_level": "3+ years",
            "department": "Engineering",
            "location": "San Francisco"
        })
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            service = LLMExtractionService()
            result = service.extract_job_info("Sample job description")
        
        assert isinstance(result, JobPostingLLMCreate)
        assert result.title == "Software Engineer"
        assert result.description == "A great job"
        assert result.skills == ["Python", "JavaScript"]
        assert result.experience_level == "3+ years"
        assert result.department == "Engineering"
        assert result.location == "San Francisco"
    
    @patch('backend.src.services.llm_extraction_service.ChatGoogleGenerativeAI')
    def test_extract_job_info_with_json_markers(self, mock_llm_class):
        """Test extraction with JSON wrapped in markdown markers"""
        # Mock LLM response with markdown JSON
        mock_response = Mock()
        mock_response.content = '''```json
{
    "title": "Data Scientist",
    "description": null,
    "skills": ["Python", "R"],
    "experience_level": null,
    "department": "Data Science",
    "location": "New York"
}
```'''
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            service = LLMExtractionService()
            result = service.extract_job_info("Sample job description")
        
        assert result.title == "Data Scientist"
        assert result.description is None
        assert result.skills == ["Python", "R"]
        assert result.experience_level is None
        assert result.department == "Data Science"
        assert result.location == "New York"
    
    @patch('backend.src.services.llm_extraction_service.ChatGoogleGenerativeAI')
    def test_extract_job_info_invalid_json(self, mock_llm_class):
        """Test extraction with invalid JSON response"""
        # Mock LLM response with invalid JSON
        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            service = LLMExtractionService()
            result = service.extract_job_info("Sample job description")
        
        # Should fallback to empty structure with description
        assert result.title is None
        assert "Sample job description" in result.description
        assert result.skills is None
        assert result.experience_level is None
        assert result.department is None
        assert result.location is None
    
    @patch('backend.src.services.llm_extraction_service.ChatGoogleGenerativeAI')
    def test_extract_job_info_missing_fields(self, mock_llm_class):
        """Test extraction with missing fields in response"""
        # Mock LLM response with missing fields
        mock_response = Mock()
        mock_response.content = json.dumps({
            "title": "Backend Engineer",
            "skills": ["Java", "Spring"]
            # Missing other fields
        })
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            service = LLMExtractionService()
            result = service.extract_job_info("Sample job description")
        
        assert result.title == "Backend Engineer"
        assert result.skills == ["Java", "Spring"]
        # Missing fields should be None
        assert result.description is None
        assert result.experience_level is None
        assert result.department is None
        assert result.location is None
    
    @patch('backend.src.services.llm_extraction_service.ChatGoogleGenerativeAI')
    def test_extract_job_info_empty_strings_to_none(self, mock_llm_class):
        """Test that empty strings are converted to None"""
        # Mock LLM response with empty strings
        mock_response = Mock()
        mock_response.content = json.dumps({
            "title": "Engineer",
            "description": "",
            "skills": [],
            "experience_level": "   ",
            "department": "Tech",
            "location": ""
        })
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            service = LLMExtractionService()
            result = service.extract_job_info("Sample job description")
        
        assert result.title == "Engineer"
        assert result.description is None  # Empty string converted to None
        assert result.skills is None  # Empty list converted to None
        assert result.experience_level is None  # Whitespace string converted to None
        assert result.department == "Tech"
        assert result.location is None  # Empty string converted to None
    
    def test_create_extraction_prompt(self):
        """Test prompt creation"""
        service = LLMExtractionService()
        prompt = service._create_extraction_prompt("Test job description")
        
        assert "Test job description" in prompt
        assert "JSON" in prompt
        assert "title" in prompt
        assert "description" in prompt
        assert "skills" in prompt
        assert "experience_level" in prompt
        assert "department" in prompt
        assert "location" in prompt

    @pytest.mark.asyncio
    async def test_generate_profile_summary_without_llm(self):
        """Test profile summary generation when LLM is not available"""
        service = LLMExtractionService()
        service.llm = None
        
        candidate_data = {"name": "John Doe", "skills": ["Python"]}
        
        with pytest.raises(Exception) as exc_info:
            await service.generate_profile_summary(candidate_data)
        assert "LLM service is not available" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_profile_summary_success(self):
        """Test successful profile summary generation"""
        mock_response = Mock()
        mock_response.content = """
Professional Summary

Software Engineer with 4+ years of experience in Python development.

Education

Bachelor's degree in Computer Science

Key Strengths

• Strong problem-solving skills
• Experience with agile methodologies

Technical Skills

Programming Languages: Python, JavaScript
Frontend: React, HTML, CSS
Databases: PostgreSQL, MongoDB

Professional Experience

Developed multiple web applications using Python and React.

Project Summary:
Successfully delivered 5+ projects on time.
"""
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        service = LLMExtractionService()
        service.llm = mock_llm
        
        candidate_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "JavaScript"],
            "experience": "4+ years in software development",
            "education": "Bachelor's degree in Computer Science"
        }
        feedback_data = ["Great technical interview", "Strong problem solver"]
        
        result = await service.generate_profile_summary(candidate_data, feedback_data)
        
        assert "Software Engineer" in result
        assert "Python" in result
        assert "Bachelor's degree" in result
        mock_llm.invoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_profile_summary_with_minimal_data(self):
        """Test profile summary generation with minimal candidate data"""
        mock_response = Mock()
        mock_response.content = "Basic profile summary for candidate with limited data."
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        service = LLMExtractionService()
        service.llm = mock_llm
        
        candidate_data = {"name": "Jane Smith"}  # Minimal data
        
        result = await service.generate_profile_summary(candidate_data)
        
        assert result == "Basic profile summary for candidate with limited data."
        mock_llm.invoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_profile_summary_llm_error(self):
        """Test profile summary generation when LLM service fails"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM API error")
        
        service = LLMExtractionService()
        service.llm = mock_llm
        
        candidate_data = {"name": "Test Candidate"}
        
        with pytest.raises(Exception) as exc_info:
            await service.generate_profile_summary(candidate_data)
        assert "Profile summary generation failed" in str(exc_info.value)

    def test_create_profile_summary_prompt(self):
        """Test profile summary prompt creation"""
        service = LLMExtractionService()
        
        candidate_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "JavaScript"],
            "experience": "5 years",
            "education": "BS Computer Science",
            "summary": "Experienced developer",
            "raw_text": "Resume content here"
        }
        feedback_data = ["Excellent communication", "Strong technical skills"]
        
        prompt = service._create_profile_summary_prompt(candidate_data, feedback_data)
        
        # Check that all candidate data is included in prompt
        assert "John Doe" in prompt
        assert "john@example.com" in prompt
        assert "Python, JavaScript" in prompt
        assert "5 years" in prompt
        assert "BS Computer Science" in prompt
        assert "Experienced developer" in prompt
        assert "Resume content here" in prompt
        
        # Check that feedback is included
        assert "Excellent communication" in prompt
        assert "Strong technical skills" in prompt
        
        # Check that template structure is mentioned
        assert "Professional Summary" in prompt
        assert "Education" in prompt
        assert "Technical Skills" in prompt
        assert "Professional Experience" in prompt

    def test_create_profile_summary_prompt_without_feedback(self):
        """Test profile summary prompt creation without feedback data"""
        service = LLMExtractionService()
        
        candidate_data = {"name": "Jane Doe", "skills": ["Python"]}
        
        prompt = service._create_profile_summary_prompt(candidate_data, None)
        
        assert "Jane Doe" in prompt
        assert "Python" in prompt
        assert "Feedback and Additional Information" not in prompt