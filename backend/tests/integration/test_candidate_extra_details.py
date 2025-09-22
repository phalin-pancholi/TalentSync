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

@pytest.mark.integration 
@patch('backend.src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
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
DevOps: Docker, AWS, CI/CD pipelines

Professional Experience

Developed and maintained multiple web applications serving thousands of users. Led technical initiatives and mentored junior developers. Strong focus on performance optimization and user experience.

Project Summary:
Successfully delivered 10+ projects including e-commerce platforms, data analytics dashboards, and API integrations. Consistently met project deadlines and exceeded performance targets.
"""
    mock_generate_summary.return_value = mock_profile_summary
    
    # Step 1: Create a test candidate with comprehensive data
    candidate_data = {
        "name": "John Smith",
        "email": "john.smith@example.com", 
        "phone": "+1-555-0123",
        "skills": ["Python", "JavaScript", "React", "Django"],
        "experience": "5+ years in full-stack development",
        "education": "Bachelor's Degree in Computer Science",
        "summary": "Experienced software engineer with expertise in web development"
    }
    
    create_response = requests.post(f"{BASE_URL}/", json=candidate_data)
    assert create_response.status_code == 200 or create_response.status_code == 201
    response_data = create_response.json()
    candidate_id = response_data.get("candidate_id") or response_data.get("id")
    
    try:
        # Step 2: Add some feedback/extra details
        feedback_data = {
            "text_content": "Excellent technical interview performance. Strong problem-solving skills demonstrated during coding challenge. Great cultural fit for the team.",
            "type": "feedback"
        }
        
        feedback_response = requests.post(
            f"{BASE_URL}/{candidate_id}/extra-details",
            json=feedback_data
        )
        assert feedback_response.status_code in [200, 201]
        
        # Step 3: Generate profile summary
        summary_response = requests.post(f"{BASE_URL}/{candidate_id}/profile-summary")
        
        # Verify successful response
        assert summary_response.status_code == 200
        assert summary_response.headers.get("content-type") == "application/pdf"
        assert len(summary_response.content) > 0
        
        # Verify LLM service was called with correct data
        mock_generate_summary.assert_called_once()
        call_args = mock_generate_summary.call_args[0]
        candidate_data_arg = call_args[0]
        feedback_data_arg = call_args[1] if len(call_args) > 1 else None
        
        # Verify candidate data was passed correctly
        assert candidate_data_arg["name"] == "John Smith"
        assert candidate_data_arg["email"] == "john.smith@example.com"
        assert "Python" in candidate_data_arg["skills"]
        
        # Verify feedback data was included
        assert feedback_data_arg is not None
        assert len(feedback_data_arg) > 0
        assert any("technical interview" in fb.lower() for fb in feedback_data_arg)
        
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
    """Integration test for profile summary generation with non-existent candidate"""
    fake_candidate_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
    
    summary_response = requests.post(f"{BASE_URL}/{fake_candidate_id}/profile-summary")
    assert summary_response.status_code == 404

@pytest.mark.integration
@patch('backend.src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
def test_profile_summary_llm_service_error_integration(mock_generate_summary):
    """Integration test for handling LLM service errors during profile summary generation"""
    
    # Mock LLM service to raise an error
    mock_generate_summary.side_effect = Exception("Gemini API service temporarily unavailable")
    
    # Create a test candidate
    candidate_data = {
        "name": "Error Test Candidate",
        "email": "error.test@example.com",
        "skills": ["Testing"]
    }
    
    create_response = requests.post(f"{BASE_URL}/", json=candidate_data)
    assert create_response.status_code in [200, 201]
    response_data = create_response.json()
    candidate_id = response_data.get("candidate_id") or response_data.get("id")
    
    try:
        # Attempt to generate profile summary
        summary_response = requests.post(f"{BASE_URL}/{candidate_id}/profile-summary")
        
        # Should return 500 internal server error
        assert summary_response.status_code == 500
        error_data = summary_response.json()
        assert "error" in error_data or "detail" in error_data
        
    finally:
        # Cleanup
        requests.delete(f"{BASE_URL}/{candidate_id}")
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
        delete_response = requests.delete(f"{BASE_URL}/{candidate_id}")
        assert delete_response.status_code == 204


@pytest.mark.integration 
def test_candidate_extra_details_error_handling():
    """Test error handling for candidate extra details upload"""
    
    # Test with non-existent candidate
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = requests.post(f"{BASE_URL}/non-existent-id/extra-details", files=files)
    assert response.status_code == 404
    
    # Create a test candidate for remaining tests
    candidate_data = {
        "name": "Test Candidate 2",
        "email": "test2@example.com", 
        "skills": "Testing"
    }
    
    create_response = requests.post(f"{BASE_URL}/", data=candidate_data)
    assert create_response.status_code == 200
    candidate_id = create_response.json()["candidate_id"]
    
    try:
        # Test unsupported file type
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
        assert response.status_code == 415
        assert "Unsupported file type" in response.json()["detail"]
        
        # Test empty file
        files = {"file": ("empty.txt", b"", "text/plain")}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
        assert response.status_code == 422
        assert "empty" in response.json()["detail"].lower()
        
        # Test file too large (simulate with large content)
        large_content = b"x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        files = {"file": ("large.txt", large_content, "text/plain")}
        response = requests.post(f"{BASE_URL}/{candidate_id}/extra-details", files=files)
        assert response.status_code == 413
        assert "too large" in response.json()["detail"].lower()
        
    finally:
        # Cleanup
        delete_response = requests.delete(f"{BASE_URL}/{candidate_id}")
        assert delete_response.status_code == 204