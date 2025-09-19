# Data Model: Candidate Document LLM Extraction and Storage

## Entities

### Candidate Document
- **Attributes**:
  - file (binary or file reference)
  - extracted_text (string)
  - upload_timestamp (datetime)
  - associated_candidate (reference)

### Candidate Profile
- **Attributes**:
  - name (string, optional)
  - contact (string, optional)
  - skills (list of strings, optional)
  - experience (string, optional)
  - education (string, optional)
  - [other fields as returned by LLM, all optional]

### Raw Text Data
- **Attributes**:
  - text (string)
  - source_document (reference)
  - created_at (datetime)

## Relationships
- Candidate Document → Candidate Profile (1:1, document generates profile)
- Candidate Document → Raw Text Data (1:1, document generates raw text)

## Validation Rules
- Candidate Profile fields may be missing (optional)
- Document must be readable; if not, error is handled gracefully

---

*Data model complete. Ready for contract and quickstart generation.*
