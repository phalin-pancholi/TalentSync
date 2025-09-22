# Contract Test: Candidate Extra Details API

## Purpose
Test the upload of extra details for a candidate via the API.

## Scenarios
- Upload valid .txt file (should succeed)
- Upload valid .pdf file (should succeed)
- Upload unsupported file type (should fail)
- Upload file >5MB (should fail)
- Upload file with no extractable text (should fail)

## Steps
1. Prepare candidate and test files
2. POST to `/api/candidates/{candidate_id}/extra-details` with file
3. Assert response code and content

---
*See test_candidate_extra_details.py for implementation.*
