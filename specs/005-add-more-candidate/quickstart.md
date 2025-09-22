# Quickstart: Add More Candidate Detail Functionality

## Prerequisites
- Backend and frontend running
- User has access to candidate card

## Steps
1. Go to a candidate card in the UI
2. Click the "Upload Details" button (green file upload icon)
3. Select a .txt or .pdf file (max 5MB)
4. Submit the upload
5. On success, see the new extra detail appear for the candidate
6. On error (wrong file type, too large, unreadable, or empty), see an error message

## Backend
- Endpoint: `POST /api/candidates/{candidate_id}/extra-details`
- Accepts: multipart/form-data with file
- Validates file type (.txt, .pdf) and size (max 5MB)
- Extracts text and stores in MongoDB collection `candidate_extra_details`
- Returns: CandidateExtraDetailResponse with id, candidate_id, text_content, type, created_at

## Frontend
- Only candidate card has upload button (green FileUp icon)
- Shows upload progress and result via toast notifications
- Displays existing extra details in candidate card with type badges and timestamps
- Shows up to 3 most recent details, with indicator for additional details

## Error Handling
- 404: Candidate not found
- 413: File too large (>5MB)
- 415: Unsupported file type (not .txt or .pdf)
- 422: Empty file or no extractable text
- 500: Server processing error

## File Type Detection
The system automatically detects the type of extra detail based on filename:
- Files containing "feedback" or "interview" → type: "feedback"
- Files containing "skill" → type: "skills"  
- Files containing "summary" or "resume" → type: "summary"
- Other files → type: null

---
*Ready for testing and deployment.*
