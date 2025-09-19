# Data Model: LLM-based Job Upload Endpoint

## Entities

### Job Description Document
- file_type: str (pdf, txt)
- content: bytes or str
- upload_timestamp: datetime
- uploader: str (user id or email)

### JobPostingBase (Pydantic Model)
- title: Optional[str]
- description: Optional[str]
- skills: Optional[List[str]]
- experience_level: Optional[str]
- department: Optional[str]
- location: Optional[str]

### Job Entry
- All fields from JobPostingBase
- id: str (UUID)
- created_at: datetime
- updated_at: datetime

## Relationships
- Each Job Entry is created from a Job Description Document via LLM extraction.

## Validation Rules
- All fields in JobPostingBase are optional (can be None).
- File type must be pdf or txt.
