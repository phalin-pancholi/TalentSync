import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.src.api.main import app

client = TestClient(app)

def test_get_document():
    # First create a candidate with a document
    with open("tests/data/sample_job.pdf", "rb") as f:
        create_response = client.post(
            "/candidates",
            data={"name": "Test User", "email": "testdoc@example.com", "skills": "Testing"},
            files={"document": ("test_resume.pdf", f, "application/pdf")}
        )
    assert create_response.status_code == 201
    candidate_data = create_response.json()
    
    # Get the document if document_id is provided
    if "document_id" in candidate_data:
        response = client.get(f"/documents/{candidate_data['document_id']}")
        assert response.status_code == 200
        assert response.json()["file_name"] == "test_resume.pdf"

def test_get_document_not_found():
    response = client.get("/documents/nonexistent")
    assert response.status_code == 404

@patch('backend.src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
def test_generate_profile_summary_contract(mock_generate_summary):
    """Contract test for profile summary generation endpoint"""
    # Mock the LLM response
    mock_generate_summary.return_value = """
Professional Summary

Software Engineer with 4+ years of experience in frontend development, specializing in ReactJS, TypeScript, and Tailwind CSS. Attention to detail, collaborating with teams. Participating in entire software development life-cycle.

Education

Bachelor's degree in Computer Science

Key Strengths

Good problem-solving skills with the ability to manage challenges methodically and successfully deliver feature implementations.

Technical Skills

Programming Languages: JavaScript, TypeScript
Frontend: ReactJS, TypeScript, Tailwind CSS
Databases: MongoDB
DevOps: Docker

Professional Experience

Contributed in development and maintenance of applications. Documentation for future reference and knowledge sharing.

Project Summary:
Developed multiple web applications using modern frontend technologies.
"""
    
    # First create a test candidate
    create_response = client.post(
        "/candidates",
        json={
            "name": "John Doe",
            "email": "john.doe@example.com", 
            "skills": ["ReactJS", "TypeScript", "Tailwind CSS"],
            "experience": "4+ years in frontend development",
            "education": "Bachelor's degree in Computer Science"
        }
    )
    assert create_response.status_code == 201
    candidate_data = create_response.json()
    candidate_id = candidate_data["id"]
    
    # Test the profile summary generation endpoint
    response = client.post(f"/candidates/{candidate_id}/profile-summary")
    
    # Verify the response structure and content
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0
    
    # Verify the LLM service was called with the candidate data
    mock_generate_summary.assert_called_once()
    call_args = mock_generate_summary.call_args[0][0]  # First argument (candidate_data)
    assert call_args["name"] == "John Doe"
    assert call_args["email"] == "john.doe@example.com"
    assert "ReactJS" in call_args["skills"]

@patch('backend.src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
def test_generate_profile_summary_with_feedback_contract(mock_generate_summary):
    """Contract test for profile summary generation with feedback data"""
    mock_generate_summary.return_value = "Mock profile summary with feedback"
    
    # Create a test candidate with extra details (feedback)
    create_response = client.post(
        "/candidates",
        json={
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "skills": ["Python", "Django"]
        }
    )
    assert create_response.status_code == 201
    candidate_data = create_response.json()
    candidate_id = candidate_data["id"]
    
    # Add feedback/extra details
    feedback_response = client.post(
        f"/candidates/{candidate_id}/extra-details",
        json={
            "text_content": "Excellent problem-solving skills and great team player",
            "type": "feedback"
        }
    )
    assert feedback_response.status_code == 201
    
    # Test profile summary generation
    response = client.post(f"/candidates/{candidate_id}/profile-summary")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # Verify LLM was called with feedback data
    mock_generate_summary.assert_called_once()
    call_args = mock_generate_summary.call_args
    candidate_data_arg = call_args[0][0]
    feedback_data_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('feedback_data')
    
    assert candidate_data_arg["name"] == "Jane Smith"
    assert feedback_data_arg is not None
    assert len(feedback_data_arg) > 0

def test_generate_profile_summary_candidate_not_found():
    """Test profile summary generation for non-existent candidate"""
    response = client.post("/candidates/nonexistent_id/profile-summary")
    assert response.status_code == 404

@patch('backend.src.services.llm_extraction_service.LLMExtractionService.generate_profile_summary')
def test_generate_profile_summary_llm_error_contract(mock_generate_summary):
    """Contract test for handling LLM service errors"""
    # Mock LLM service failure
    mock_generate_summary.side_effect = Exception("LLM service unavailable")
    
    # Create a test candidate
    create_response = client.post(
        "/candidates",
        json={"name": "Error Test", "email": "error@example.com"}
    )
    assert create_response.status_code == 201
    candidate_data = create_response.json()
    candidate_id = candidate_data["id"]
    
    # Test error handling
    response = client.post(f"/candidates/{candidate_id}/profile-summary")
    assert response.status_code == 500
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data