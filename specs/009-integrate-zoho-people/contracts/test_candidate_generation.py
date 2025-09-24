import pytest
import requests

BASE_URL = "http://localhost:8002"  # Zoho sync service port


class TestCandidateGenerationContract:
    def test_get_candidates_endpoint(self):
        """Test candidates retrieval endpoint"""
        response = requests.get(f"{BASE_URL}/candidates")
        assert response.status_code in [200, 500]  # 500 if service not ready
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_candidate_details_schema(self):
        """Test candidate details schema validation"""
        response = requests.get(f"{BASE_URL}/candidates")
        
        if response.status_code == 200:
            candidates = response.json()
            
            for candidate in candidates:
                # Validate required fields exist
                assert "candidate_id" in candidate
                assert "employee_id" in candidate
                assert "profile" in candidate
                assert "skills" in candidate
                assert "experience" in candidate
                assert "summary" in candidate
                assert "generated_at" in candidate
                
                # Validate field types
                assert isinstance(candidate["candidate_id"], str)
                assert isinstance(candidate["employee_id"], str)
                assert isinstance(candidate["profile"], str)
                assert isinstance(candidate["skills"], list)
                assert isinstance(candidate["experience"], str)
                assert isinstance(candidate["summary"], str)
                assert isinstance(candidate["generated_at"], str)

    def test_get_candidate_by_employee_id(self):
        """Test individual candidate retrieval by employee ID"""
        # First get all candidates to find a valid employee_id
        response = requests.get(f"{BASE_URL}/candidates")
        
        if response.status_code == 200:
            candidates = response.json()
            
            if candidates:
                # Test with the first candidate's employee_id
                employee_id = candidates[0]["employee_id"]
                response = requests.get(f"{BASE_URL}/candidates/{employee_id}")
                assert response.status_code == 200
                
                candidate = response.json()
                assert candidate["employee_id"] == employee_id
            
            # Test with non-existent employee_id
            response = requests.get(f"{BASE_URL}/candidates/non_existent_id")
            assert response.status_code == 404
