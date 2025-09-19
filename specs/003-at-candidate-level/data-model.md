# Data Model: Candidate Raw Data & Profile Summary

## Entities

### CandidateRawData
- **candidate_id**: string (unique, system-generated)
- **email**: string (indexed, [NEEDS CLARIFICATION: unique?])
- **raw_files**: array of file objects (resume, feedback, etc.)
  - file_name: string
  - file_type: string (pdf, docx, txt)
  - file_size: int (bytes)
  - file_data: binary or GridFS reference
  - uploaded_at: datetime
- **created_at**: datetime
- **updated_at**: datetime

### ProfileSummary
- **summary_id**: string (unique, system-generated)
- **candidate_id**: string (reference to CandidateRawData)
- **summary_text**: string (LLM output)
- **pdf_file**: binary or file reference
- **generated_at**: datetime
- **llm_model**: string (e.g., "Gemini-1.0-pro")
- **status**: enum (pending, success, error)
- **error_message**: string (nullable)

## Relationships
- One CandidateRawData can have multiple ProfileSummary records (for re-generation/versioning).

## Validation Rules
- email: must be valid email format; [NEEDS CLARIFICATION: enforce uniqueness?]
- raw_files: only allow pdf, docx, txt; max 10MB per file
- candidate_id, summary_id: UUIDv4

## State Transitions
- ProfileSummary: pending → success | error

## Notes
- All sensitive data must be encrypted at rest.
- Large files stored in GridFS if >16MB.
- All LLM requests/responses logged (no PII).
