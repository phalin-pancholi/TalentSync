# Research for Profile Summary Functionality (Phase 0)

## Unknowns and Clarifications

1. **LLM Integration (Gemini model)**
   - How will the backend communicate with Gemini? (Assume HTTP API, no new packages)
   - What is the expected input/output format for Gemini?
   - How to handle LLM errors, timeouts, or malformed responses?
2. **User Roles/Permissions**
   - Which user roles are allowed to generate profile summaries? (Recruiter, hiring manager, others?)
   - Should access be restricted at the API or UI level?
3. **Logging and Audit**
   - What details must be logged for each profile summary generation? (User, candidate, timestamp, status, etc.)
   - Where should logs be stored? (Assume existing logging infrastructure)
4. **Error Handling**
   - How should the system notify users of LLM or PDF generation failures?
   - Should partial/incomplete summaries be delivered or blocked?
5. **PDF Generation**
   - What template/format should be used for the PDF? (Use provided example)
   - How to handle missing or incomplete candidate data in the summary?
6. **Data Privacy**
   - Are there any restrictions on what candidate data can be sent to Gemini?
   - Should sensitive fields be redacted?

## Research Tasks

- Research Gemini API usage for LLM summary generation (HTTP, auth, input/output format)
- Review best practices for integrating LLMs in backend services without new dependencies
- Clarify user roles and permissions for summary generation
- Define logging requirements for auditability
- Document error handling and user notification strategies
- Review PDF generation approaches using only existing packages
- Identify privacy and data handling requirements for LLM input

## Consolidated Findings

- **Decision**: Use Gemini LLM via HTTP API for summary generation, using only built-in or already-installed Python packages for HTTP requests and PDF generation.
- **Rationale**: Meets user constraint (no new packages), leverages existing infrastructure, and aligns with project principles.
- **Alternatives considered**: Other LLMs or libraries, but Gemini is mandated; new packages rejected due to user constraint.

---

All major unknowns and clarifications are documented above. Further details will be resolved in design and contract phases.
