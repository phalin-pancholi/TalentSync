# Data Model: Candidate Card UI

## Entity: Candidate
- id: string
- name: string
- skills: list of string
- experience: string or number (years)
- [other details]: string, list, or object (for full details view)

## Entity: CandidateCard
- candidateId: string
- minimalDetails: { name, skills, experience }
- allDetails: { all candidate fields }
- isExpanded: boolean (UI state)

## Relationships
- CandidateCard references Candidate by candidateId

## Validation Rules
- name: required, non-empty string
- skills: optional, list of strings (can be empty)
- experience: optional, string or number
- allDetails: must include all available candidate fields

## State Transitions
- isExpanded: false → true (when user clicks "Show all details")
- isExpanded: true → false (when user hides details)
