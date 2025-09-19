# Research for Candidate Management and Navigation Update

## Unknowns and Research Tasks

### 1. What file types are supported for candidate upload?
- **Task**: Research best practices for file type support in candidate document uploads (e.g., PDF, DOCX, TXT).

### 2. Should duplicate candidate entries be allowed, merged, or rejected?
- **Task**: Research industry standards for handling duplicate candidate entries in recruitment systems.

### 3. Required fields and validation rules for candidate creation?
- **Task**: Research common required fields and validation rules for candidate profiles (e.g., name, email, phone, skills).

### 4. Language/Version, Dependencies, Storage, Testing
- **Task**: Confirm backend stack (Python 3.11, FastAPI, MongoDB, pytest) and frontend stack (React, JS/TS, Jest).

### 5. Project Type, Target Platform, Performance, Constraints, Scale
- **Task**: Confirm web application structure (frontend + backend), Linux server deployment, and typical performance/scale expectations for recruitment platforms.

## Findings

### 1. Supported File Types
- **Decision**: Support PDF, DOCX, and TXT for candidate uploads.
- **Rationale**: These are the most common resume formats.
- **Alternatives considered**: Limiting to PDF/TXT for simplicity, but DOCX is widely used.

### 2. Duplicate Candidate Handling
- **Decision**: Reject exact duplicates based on email; allow manual merge for similar entries.
- **Rationale**: Prevents clutter and confusion, but allows flexibility.
- **Alternatives considered**: Auto-merge (risk of incorrect merges), allow all duplicates (poor UX).

### 3. Required Fields and Validation
- **Decision**: Require name, email, and at least one skill. Validate email format and uniqueness.
- **Rationale**: Ensures minimum viable candidate profile and data quality.
- **Alternatives considered**: Fewer required fields (risk of incomplete profiles), more required fields (higher friction).

### 4. Tech Stack
- **Decision**: Backend: Python 3.11, FastAPI, MongoDB; Frontend: React, JS, Jest.
- **Rationale**: Matches existing project stack.
- **Alternatives considered**: N/A (project already established).

### 5. Project Structure and Scale
- **Decision**: Web app with separate frontend and backend, Linux server, scale for 1k-10k users.
- **Rationale**: Standard for recruitment SaaS.
- **Alternatives considered**: Monolith, mobile-first.

## Constitution Alignment
- All research tasks and decisions align with project constitution principles (library-first, CLI, TDD, integration testing, observability, simplicity).

---

All NEEDS CLARIFICATION items from the spec are now resolved. Ready for Phase 1 design.
