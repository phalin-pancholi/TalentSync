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