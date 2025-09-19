# Research for Candidate Document LLM Extraction and Storage

## Unresolved Questions (NEEDS CLARIFICATION)
- What happens when the document is unreadable or corrupt? [NEEDS CLARIFICATION: Should the system reject, notify the user, or allow manual entry?]
- How does the system handle LLM extraction failures? [NEEDS CLARIFICATION: Should it retry, notify the user, or allow manual entry?]
- What if the same document is uploaded multiple times? [NEEDS CLARIFICATION: Should duplicates be detected or allowed?]

## Decisions & Rationale
- **No extra packages**: The implementation must use only existing dependencies.
  - *Rationale*: User explicitly requested not to add new packages.
- **Job Page Parity**: The candidate document upload and processing flow must match the job page's logic and user experience.
  - *Rationale*: Ensures consistency and reusability of patterns.
- **Allow incomplete candidate profiles**: Candidate data can be saved even if some fields are missing after LLM extraction.
  - *Rationale*: User wants flexibility and robustness in data capture.

## Alternatives Considered
- **Rejecting incomplete profiles**: Not chosen, as user wants to allow saving with missing fields.
- **Adding new parsing or LLM libraries**: Not allowed per user constraints.

## Best Practices
- **Graceful error handling**: For unreadable/corrupt documents and LLM failures, notify the user and allow manual entry if possible.
- **Duplicate handling**: Detect duplicates by file hash or metadata, but allow user override if needed.
- **Data storage**: Store both structured candidate data and raw extracted text in MongoDB for future reference.

## Integration Patterns
- **Reuse job page logic**: Mirror the job page's document processing and storage logic for candidates, adapting only where necessary.

---

*All research tasks complete. Ready for Phase 1 design.*
