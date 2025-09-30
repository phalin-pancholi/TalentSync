import pytest
import requests
import os
from unittest.mock import patch

BASE_URL = "http://localhost:8000/api/candidates"

@pytest.mark.integration
def test_candidate_extra_details_integration():
    """Integration test for the complete candidate extra details workflow"""
    
    # Step 1: Create a test candidate first
    candidate_data = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "skills": "Python,JavaScript"
    }
    
    # Create candidate via form data
    create_response = requests.post(
        f"{BASE_URL}/",
        data=candidate_data
    )
    assert create_response.status_code == 200
    candidate_id = create_response.json()["candidate_id"]
    
    try:
        # Step 2: Upload extra details for the candidate
        test_file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "data", 
            "sample_job.txt"
        )
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("interview_feedback.txt", f, "text/plain")}
            upload_response = requests.post(
                f"{BASE_URL}/{candidate_id}/extra-details", 
                files=files
            )
        
        assert upload_response.status_code == 200
        extra_detail = upload_response.json()
        assert extra_detail["candidate_id"] == candidate_id
        assert extra_detail["text_content"]
        assert len(extra_detail["text_content"]) > 0
        assert extra_detail["created_at"]
        
        # Step 3: Retrieve extra details for the candidate
        get_response = requests.get(f"{BASE_URL}/{candidate_id}/extra-details")
        assert get_response.status_code == 200
        
        extra_details = get_response.json()
        assert len(extra_details) == 1
        assert extra_details[0]["id"] == extra_detail["id"]
        assert extra_details[0]["text_content"] == extra_detail["text_content"]
        
        # Step 4: Upload another extra detail
        test_content = "Additional interview feedback: Excellent problem-solving skills."
        files = {"file": ("additional_feedback.txt", test_content.encode(), "text/plain")}
        upload_response2 = requests.post(
            f"{BASE_URL}/{candidate_id}/extra-details", 
            files=files
        )
        
        assert upload_response2.status_code == 200
        
        # Step 5: Verify both extra details are returned
        get_response2 = requests.get(f"{BASE_URL}/{candidate_id}/extra-details")
        assert get_response2.status_code == 200
        
        extra_details2 = get_response2.json()
        assert len(extra_details2) == 2
        
        # Verify most recent is first (sorted by created_at desc)
        assert extra_details2[0]["text_content"] == test_content
        
    finally:
        # Cleanup: Delete the test candidate
        if 'candidate_id' in locals():
            delete_response = requests.delete(f"{BASE_URL}/{candidate_id}")
            # Don't assert on delete response as it might not be implemented yet


@pytest.mark.integration 
@patch('src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
def test_profile_summary_generation_integration(mock_generate_summary):
    """Integration test for the complete profile summary generation workflow"""
    
    # Mock the LLM response
    mock_profile_summary = """
Professional Summary

Software Engineer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and cloud technologies. Proven track record in developing scalable web applications and APIs.

Education

Bachelor's Degree in Computer Science
Relevant certifications in cloud computing

Key Strengths

• Strong problem-solving abilities and analytical thinking
• Excellent communication and collaboration skills  
• Experience with agile development methodologies
• Passionate about clean code and best practices

Technical Skills

Programming Languages: Python, JavaScript, TypeScript
Frontend: React, Vue.js, HTML5, CSS3
Backend: Django, FastAPI, Node.js
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Azure, Docker, Kubernetes

Professional Experience

2019-2024: Senior Software Engineer at TechCorp
• Led development of microservices architecture serving 1M+ users
• Implemented CI/CD pipelines reducing deployment time by 60%
• Mentored junior developers and conducted code reviews

2017-2019: Software Engineer at StartupXYZ  
• Built full-stack web applications using React and Node.js
• Designed and optimized database schemas for high performance
• Collaborated with cross-functional teams in agile environment
    """
    mock_generate_summary.return_value = mock_profile_summary
    
    # Step 1: Create a test candidate  
    candidate_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1-555-0123",
        "skills": "Python,JavaScript,React"
    }
    
    create_response = requests.post(f"{BASE_URL}/", data=candidate_data)
    assert create_response.status_code == 200
    candidate_id = create_response.json()["candidate_id"]
    
    try:
        # Step 2: Upload extra details (resume/CV) for the candidate
        test_file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "data", 
            "sample_job.txt"  # Using sample text file as resume
        )
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("resume.txt", f, "text/plain")}
            upload_response = requests.post(
                f"{BASE_URL}/{candidate_id}/extra-details", 
                files=files
            )
        
        assert upload_response.status_code == 200
        
        # Step 3: Generate profile summary using the uploaded document
        summary_response = requests.post(
            f"http://localhost:8000/api/documents/{candidate_id}/generate-summary"
        )
        
        assert summary_response.status_code == 200
        
        # Step 4: Verify PDF content (basic check)
        pdf_content = summary_response.content
        # Since we're returning text as bytes for now, check it contains expected content
        content_str = pdf_content.decode('utf-8')
        assert "John Smith" in content_str
        assert "Profile Summary" in content_str or "PROFILE SUMMARY" in content_str
        
    finally:
        # Cleanup: Delete the test candidate
        delete_response = requests.delete(f"{BASE_URL}/{candidate_id}")
        # Don't assert on delete response as it might not be implemented yet


@pytest.mark.integration
def test_profile_summary_missing_candidate():
    """Test profile summary generation for non-existent candidate"""
    response = requests.post("http://localhost:8000/api/documents/nonexistent-id/generate-summary")
    assert response.status_code == 404


@pytest.mark.integration
@patch('src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
def test_profile_summary_llm_service_error_integration(mock_generate_summary):
    """Integration test for handling LLM service errors"""
    # Mock LLM service failure
    mock_generate_summary.side_effect = Exception("LLM service unavailable")
    
    # Create a test candidate
    candidate_data = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "skills": "Python"
    }
    
    create_response = requests.post(f"{BASE_URL}/", data=candidate_data)
    assert create_response.status_code == 200
    candidate_id = create_response.json()["candidate_id"]
    
    try:
        # Upload some extra details first
        test_content = "Test resume content"
        files = {"file": ("resume.txt", test_content.encode(), "text/plain")}
        upload_response = requests.post(
            f"{BASE_URL}/{candidate_id}/extra-details", 
            files=files
        )
        assert upload_response.status_code == 200
        
        # Try to generate profile summary - should handle LLM error gracefully
        summary_response = requests.post(
            f"http://localhost:8000/api/documents/{candidate_id}/generate-summary"
        )
        
        # Should return error or fallback response
        assert summary_response.status_code in [500, 503]  # Server error due to LLM failure
        
    finally:
        # Cleanup
        requests.delete(f"{BASE_URL}/{candidate_id}")


@pytest.mark.integration 
def test_candidate_extra_details_error_handling():
    """Test error handling for candidate extra details upload"""
    
    # Test with non-existent candidate
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = requests.post(f"{BASE_URL}/non-existent-id/extra-details", files=files)
    assert response.status_code == 404
    
    # Create a test candidate for remaining tests
    candidate_data = {
        "name": "Error Test Candidate",
        "email": "error.test@example.com",
        "skills": "Testing"
    }
    
    create_response = requests.post(f"{BASE_URL}/", data=candidate_data)
    assert create_response.status_code == 200
    candidate_id = create_response.json()["candidate_id"]
    
    try:
        # Test with invalid file type
        invalid_files = {"file": ("test.exe", b"binary content", "application/octet-stream")}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=invalid_files)
        assert response.status_code == 400
        
        # Test with empty file
        empty_files = {"file": ("empty.txt", b"", "text/plain")}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=empty_files)
        assert response.status_code == 400
        
    finally:
        # Cleanup
        requests.delete(f"{BASE_URL}/{candidate_id}")