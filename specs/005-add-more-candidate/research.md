# Research: Add More Candidate Detail Functionality

## Unknowns and Clarifications
- Maximum document size for upload: 5MB (from spec)
- Supported file types: .txt, .pdf only
- Who is authorized to upload extra details? (No restriction specified; assume any user with access to candidate card can upload)
- How to handle corrupted/unreadable files: System must handle errors gracefully and notify user
- What if extracted text is empty: System should notify user and not store empty details
- How are duplicate uploads handled: Not specified; assume each upload is a new entry

## Technology Choices
- Use existing backend and frontend frameworks (Python FastAPI backend, React frontend)
- Use existing PDF/text parsing libraries already present in backend
- Use existing database (MongoDB)

## Best Practices
- Validate file type and size on both frontend and backend
- Extract text from PDF using existing library (e.g., PyPDF2 or similar)
- Store only extracted text in DB, not the file
- Provide clear user feedback on upload success/failure

## Decision Log
- Decision: Limit uploads to 5MB, .txt/.pdf only, allow all users with candidate card access to upload
- Rationale: Simplicity, aligns with current system, avoids new permissions logic
- Alternatives considered: Restricting by user role (not required by spec), storing files (rejected by spec)

---
*All clarifications resolved for planning. Ready for Phase 1.*
