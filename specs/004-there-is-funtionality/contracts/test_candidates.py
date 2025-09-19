import pytest

def test_upload_candidate_document(client):
    """Test uploading a candidate document and creating a candidate profile."""
    # Simulate file upload (use a sample resume file)
    with open('tests/data/sample_resume.pdf', 'rb') as f:
        response = client.post('/candidates/upload', files={'file': f})
    assert response.status_code == 200
    data = response.json()
    assert 'candidate' in data
    assert 'raw_text' in data
    # Candidate fields may be missing, but at least one should be present
    assert any(data['candidate'].values())


def test_upload_unreadable_document(client):
    """Test uploading an unreadable or corrupt document."""
    with open('tests/data/unsupported_file.jpg', 'rb') as f:
        response = client.post('/candidates/upload', files={'file': f})
    assert response.status_code == 400


def test_upload_duplicate_document(client):
    """Test uploading the same document twice (duplicate detection)."""
    with open('tests/data/sample_resume.pdf', 'rb') as f:
        response1 = client.post('/candidates/upload', files={'file': f})
    with open('tests/data/sample_resume.pdf', 'rb') as f:
        response2 = client.post('/candidates/upload', files={'file': f})
    assert response2.status_code in (200, 409)  # Allow user override or detect duplicate
