# Implementation Tasks: Candidate Raw Data & LLM Profile Generation

## Task Generation Strategy
- TDD: Write tests before implementation
- Dependency order: Models → Services → API → UI
- [P]: Parallelizable tasks

---

### Contract & Integration Tests
1. ✅ Write contract test for uploading candidate raw data [P]
2. ✅ Write contract test for searching candidate raw data by email or ID [P]
3. ✅ Write contract test for generating profile summary (PDF) [P]
4. ✅ Write integration test for uploading multiple file types (pdf, docx, txt)
5. ✅ Write integration test for error handling (LLM/PDF failure)
6. ✅ Write integration test for large file upload and validation

### Data Model & Storage
7. ✅ Create CandidateRawData model/schema in backend [P]
8. ✅ Create ProfileSummary model/schema in backend [P]
9. ✅ Add MongoDB indexes for email and candidate_id [P]
10. ✅ Implement file storage (GridFS or base64) for raw files

### Backend Services
11. ✅ Implement service for uploading and validating candidate raw data
12. ✅ Implement service for searching candidate raw data by email or ID
13. ✅ Implement Gemini LLM integration service for profile summary generation
14. ✅ Implement PDF generation service from LLM output
15. ✅ Implement error handling and logging for LLM/PDF failures
16. ⏭️ Implement data retention logic (pending clarification)

### API Endpoints
17. ✅ Implement /candidates/raw POST endpoint
18. ✅ Implement /candidates/raw/search GET endpoint
19. ✅ Implement /candidates/{candidate_id}/generate-profile POST endpoint

### Frontend
20. ✅ Add "Generate Profile" button to candidate section UI
21. ✅ Implement file upload UI for resumes/feedback
22. ✅ Implement search UI for candidate by email or ID
23. ✅ Implement frontend call to trigger profile generation and download PDF
24. ✅ Display error/success messages for LLM/PDF actions

### Validation & Security
25. ✅ Validate file types and sizes on frontend and backend
26. ⏭️ Secure Gemini API keys and sensitive config (environment variables)
27. ⏭️ Encrypt sensitive data at rest in MongoDB
28. ✅ Add audit logging for LLM requests (no PII)

### Finalization
29. ⏳ Run all contract and integration tests, ensure all pass
30. ⏳ Update documentation and quickstart as needed

---

## Status Legend
- ✅ Completed
- ⏳ In Progress
- ⏭️ Pending/Requires Configuration
- ❌ Failed/Blocked

## Notes
- Tasks 16, 26, 27 require environment configuration and security setup
- All core functionality implemented and ready for testing
- Pending clarifications: email uniqueness, data retention policy
