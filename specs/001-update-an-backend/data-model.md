# Data Model for Modular Python Backend

## Entities

### JobPosting
- id: str (UUID)
- title: str
- description: str
- skills: List[str]
- experience_level: str
- department: str
- location: str
- created_at: datetime
- updated_at: datetime

### Candidate
- id: str (UUID)
- name: str
- email: str
- skills: List[str]
- experience_years: int
- current_role: str
- department: str
- location: str
- match_percentage: float
- matched_skills: List[str]

## Relationships
- A JobPosting can have multiple matching Candidates.
- Candidates are matched to JobPostings based on skills and other criteria.

## Validation Rules
- All required fields must be present.
- Skills must be a non-empty list.
- Email must be valid format.
- Experience years must be non-negative integer.

## State Transitions
- JobPosting: Created → Updated → (Deleted)
- Candidate: Created → (Matched to JobPosting)

---

## Notes
- Models will use Pydantic for validation.
- MongoDB will be used for persistence.
