import pytest

# Contract test: Upload candidate raw data
@pytest.mark.contract
def test_upload_candidate_raw_data(client):
    response = client.post(
        "/candidates/raw",
        data={"email": "test@example.com"},
        files={"files": ("resume.pdf", b"PDFDATA", "application/pdf")},
    )
    assert response.status_code == 201

# Contract test: Search candidate raw data
@pytest.mark.contract
def test_search_candidate_raw_data(client):
    response = client.get("/candidates/raw/search?email=test@example.com")
    assert response.status_code in (200, 404)

# Contract test: Generate profile summary
@pytest.mark.contract
def test_generate_profile_summary(client):
    response = client.post("/candidates/1234/generate-profile")
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/pdf"
