# Data Model for Candidate Management

## Entities

### Candidate (Structured)
- **_id**: ObjectId
- **name**: string (required)
- **email**: string (required, unique)
- **phone**: string (optional)
- **skills**: array of strings (at least one required)
- **created_at**: datetime
- **updated_at**: datetime
- **document_id**: ObjectId (reference to Document)

### Document (Unstructured)
- **_id**: ObjectId
- **candidate_id**: ObjectId (reference to Candidate)
- **file_name**: string
- **file_type**: string (PDF, DOCX, TXT)
- **content_text**: string (full extracted text)
- **upload_date**: datetime
- **raw_file_path**: string (path or storage ref)

## Relationships
- One-to-one: Each Candidate may have one associated Document (resume), and each Document is linked to one Candidate.
- Foreign keys: `candidate.document_id` ↔ `document._id`, `document.candidate_id` ↔ `candidate._id`

## Indexes
- **Candidate**: Unique index on `email`, index on `skills`
- **Document**: Index on `candidate_id`, index on `file_type`

## Validation Rules
- `name` and `email` are required for Candidate
- `email` must be unique and valid format
- At least one skill required
- Document `file_type` must be one of: PDF, DOCX, TXT

## State Transitions
- Candidate and Document are created together (if uploading a document)
- Candidate can be created/updated without a document
- Document can be added/updated for an existing candidate
- Deleting a candidate should also delete the associated document

---

This model supports efficient CRUD, search, and document extraction for candidate management.
