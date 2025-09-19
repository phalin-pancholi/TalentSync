# Quickstart: Candidate Document LLM Extraction and Storage

## Prerequisites
- Backend and frontend services running
- MongoDB running and accessible
- LLM integration configured (as per job page)

## Steps
1. Go to the Candidate page in the UI.
2. Click 'Upload Document' and select a resume or CV file.
3. Submit the form to upload the document.
4. The system will extract text, send it to the LLM, and create a candidate profile.
5. The candidate profile (even if incomplete) and raw text will be stored in the database.
6. If the document is unreadable or LLM extraction fails, the system will notify you and allow manual entry.
7. If you upload the same document again, the system will detect duplicates or allow override.

## Validation
- Check that the candidate appears in the candidate list.
- Check that the raw text is stored in MongoDB.
- Check that incomplete profiles can be saved.
- Check error handling for corrupt/unreadable files.

---

*Quickstart complete. Ready for implementation tasks.*
