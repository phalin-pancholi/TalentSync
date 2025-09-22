# Data Model: Add More Candidate Detail Functionality

## Entities

### Candidate
- id: string
- name: string
- existing_details: string
- extra_details: [CandidateExtraDetail]

### CandidateExtraDetail
- id: string
- candidate_id: string (reference to Candidate)
- text_content: string (extracted from uploaded file)
- type: string (e.g., feedback, skills, summary, etc.)
- created_at: datetime

## Relationships
- Candidate has many CandidateExtraDetail entries

## Validation Rules
- Only .txt and .pdf files accepted
- Maximum file size: 5MB
- text_content must not be empty

---
*Ready for contract and quickstart design.*
