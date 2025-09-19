# Research for Candidate Raw Data Storage & LLM Profile Generation

## Unknowns/Clarifications

### 1. Email Uniqueness
- **Unknown**: Should the system enforce unique email for candidate raw data, or allow alternate unique keys?
- **Decision**: [PENDING CLARIFICATION]
- **Rationale**: Email is a common unique identifier, but candidates may share emails or have multiple records. Alternate keys (UUID, phone) may be needed.
- **Alternatives**: Enforce unique email; allow composite key (email+timestamp); use system-generated ID.

### 2. Data Retention Policy
- **Unknown**: What is the retention policy for raw candidate data (resumes, feedback)?
- **Decision**: [PENDING CLARIFICATION]
- **Rationale**: Retention affects storage, compliance, and privacy. Needs business input.
- **Alternatives**: Retain indefinitely; auto-delete after X years; allow user-configurable retention.

### 3. Gemini LLM Integration
- **Unknown**: What is the best practice for integrating Gemini LLM for profile summary generation?
- **Decision**: Use Gemini API via backend service. Send all candidate data (raw + structured) to Gemini endpoint, receive summary, generate PDF.
- **Rationale**: Centralizes LLM usage, secures API keys, and allows for logging and error handling.
- **Alternatives**: Direct frontend-to-Gemini call (less secure); use other LLMs (OpenAI, Claude).

### 4. Error Handling for LLM/PDF Generation
- **Unknown**: How should errors from Gemini LLM or PDF generation be handled?
- **Decision**: Backend should catch and log errors, return user-friendly error messages to frontend, and provide retry option.
- **Rationale**: Prevents user confusion, supports troubleshooting.
- **Alternatives**: Silent failure (not recommended); auto-retry without user input.

### 5. File Uploads and Validation
- **Unknown**: What file types and sizes should be supported for raw data uploads?
- **Decision**: Support PDF, DOCX, TXT, max 10MB per file. Validate on both frontend and backend.
- **Rationale**: Covers common resume/feedback formats, prevents abuse.
- **Alternatives**: Allow more types (images, audio); larger files (riskier).

## Gemini LLM Best Practices
- Use backend service to call Gemini API.
- Secure API keys in environment variables.
- Validate and sanitize all data sent to LLM.
- Log all LLM requests/responses for audit (without PII).
- Handle rate limits and API errors gracefully.

## MongoDB Best Practices
- Use indexed fields (email, candidate_id) for search.
- Store raw files in GridFS if large, or as base64 if small.
- Encrypt sensitive data at rest.

## PDF Generation Best Practices
- Use a reliable library (e.g., ReportLab, WeasyPrint) in backend.
- Template the summary for consistent formatting.
- Validate PDF output before sending to frontend.

## Summary
All major unknowns are documented. Gemini LLM will be integrated via backend API. Pending clarifications on email uniqueness and data retention. All other technical decisions are based on best practices for security, reliability, and maintainability.
