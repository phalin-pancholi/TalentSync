import requests
import sys
import json
from datetime import datetime
import tempfile
import os

class TalentSyncAPITester:
    def __init__(self, base_url="https://staffsync-11.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_job_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_jobs(self):
        """Test getting all jobs"""
        success, response = self.run_test(
            "Get All Jobs",
            "GET",
            "jobs",
            200
        )
        return success, response

    def test_create_job(self):
        """Test creating a new job"""
        job_data = {
            "title": "Senior Python Developer",
            "description": "We are looking for an experienced Python developer to join our team.",
            "skills": ["Python", "FastAPI", "MongoDB", "React"],
            "experience_level": "Senior",
            "department": "Engineering",
            "location": "San Francisco"
        }
        
        success, response = self.run_test(
            "Create Job",
            "POST",
            "jobs",
            200,
            data=job_data
        )
        
        if success and 'id' in response:
            self.created_job_id = response['id']
            print(f"Created job with ID: {self.created_job_id}")
        
        return success, response

    def test_get_specific_job(self):
        """Test getting a specific job by ID"""
        if not self.created_job_id:
            print("❌ No job ID available for testing")
            return False, {}
            
        success, response = self.run_test(
            "Get Specific Job",
            "GET",
            f"jobs/{self.created_job_id}",
            200
        )
        return success, response

    def test_update_job(self):
        """Test updating a job"""
        if not self.created_job_id:
            print("❌ No job ID available for testing")
            return False, {}
            
        update_data = {
            "title": "Senior Python Developer - Updated",
            "description": "Updated job description with more details.",
            "skills": ["Python", "FastAPI", "MongoDB", "React", "Docker"]
        }
        
        success, response = self.run_test(
            "Update Job",
            "PUT",
            f"jobs/{self.created_job_id}",
            200,
            data=update_data
        )
        return success, response

    def test_get_candidates(self):
        """Test getting candidates for a job"""
        if not self.created_job_id:
            print("❌ No job ID available for testing")
            return False, {}
            
        success, response = self.run_test(
            "Get Candidates for Job",
            "GET",
            f"jobs/{self.created_job_id}/candidates",
            200
        )
        
        if success and isinstance(response, list):
            print(f"Found {len(response)} candidates")
            for candidate in response[:2]:  # Show first 2 candidates
                print(f"- {candidate.get('name', 'Unknown')}: {candidate.get('match_percentage', 0)}% match")
        
        return success, response

    def test_file_upload(self):
        """Test file upload functionality"""
        # Create a temporary PDF file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_job.pdf', f, 'application/pdf')}
                success, response = self.run_test(
                    "Upload Job Document",
                    "POST",
                    "jobs/upload",
                    200,
                    files=files
                )
        finally:
            os.unlink(temp_file_path)
        
        return success, response

    def test_delete_job(self):
        """Test deleting a job"""
        if not self.created_job_id:
            print("❌ No job ID available for testing")
            return False, {}
            
        success, response = self.run_test(
            "Delete Job",
            "DELETE",
            f"jobs/{self.created_job_id}",
            200
        )
        return success, response

    def test_error_scenarios(self):
        """Test error handling scenarios"""
        print("\n🔍 Testing Error Scenarios...")
        
        # Test getting non-existent job
        success, _ = self.run_test(
            "Get Non-existent Job",
            "GET",
            "jobs/non-existent-id",
            404
        )
        
        # Test creating job with invalid data
        invalid_job_data = {
            "title": "",  # Empty title
            "description": "Test description"
            # Missing required fields
        }
        
        success2, _ = self.run_test(
            "Create Job with Invalid Data",
            "POST",
            "jobs",
            422  # Validation error
        )
        
        # Test uploading invalid file type
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'This is a text file, not a PDF or Word document')
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                success3, _ = self.run_test(
                    "Upload Invalid File Type",
                    "POST",
                    "jobs/upload",
                    400
                )
        finally:
            os.unlink(temp_file_path)
        
        return success and success2 and success3

def main():
    print("🚀 Starting TalentSync API Testing...")
    tester = TalentSyncAPITester()

    # Test sequence
    print("\n" + "="*50)
    print("BACKEND API TESTING")
    print("="*50)

    # 1. Test getting initial jobs
    tester.test_get_jobs()

    # 2. Test creating a job
    tester.test_create_job()

    # 3. Test getting the created job
    tester.test_get_specific_job()

    # 4. Test updating the job
    tester.test_update_job()

    # 5. Test getting candidates for the job
    tester.test_get_candidates()

    # 6. Test file upload
    tester.test_file_upload()

    # 7. Test error scenarios
    tester.test_error_scenarios()

    # 8. Test deleting the job (do this last)
    tester.test_delete_job()

    # Print final results
    print(f"\n" + "="*50)
    print(f"📊 FINAL RESULTS")
    print(f"="*50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())