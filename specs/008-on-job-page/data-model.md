# Data Model: Candidate Location and Experience

## Candidate Entity
- **id**: string (unique identifier)
- **name**: string
- **location**: string (free text, e.g., "Bangalore, India")
- **experience**: float (years, e.g., 3.5) and/or string (optional description)
- **skills**: list of strings
- ...existing fields...

## Validation Rules
- `experience` must be non-negative if provided
- `location` should be human-readable if provided

## Relationships
- Candidate is matched to Job via matching service

## State Transitions
- Candidate can be created, updated, or deleted
- Location and experience can be added/edited at any time
