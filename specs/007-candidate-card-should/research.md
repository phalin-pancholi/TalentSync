# Research for Cleaner Candidate Card UI

## Unknowns from Technical Context
- Language/Version: React (frontend), Python (backend) [assumed from repo structure]
- Primary Dependencies: React, Tailwind CSS (frontend); FastAPI, Pydantic (backend) [assumed]
- Storage: N/A (UI only)
- Testing: Jest (frontend), pytest (backend) [assumed]
- Target Platform: Web (Linux server)
- Project Type: Web (frontend + backend)
- Performance Goals: Not specified
- Constraints: Not specified
- Scale/Scope: Not specified

## Research Tasks
- Best practices for minimal, clean card UI in React with Tailwind CSS
- Handling missing or long data fields in UI
- UX patterns for expandable/collapsible cards
- Accessibility for "Show all details" button

## Findings

### Decision: Use React functional components with Tailwind CSS for card UI
- Rationale: Aligns with existing frontend stack, enables rapid styling and responsive design
- Alternatives considered: Custom CSS, Material UI (adds more dependencies)

### Decision: Show placeholders or hide fields for missing data
- Rationale: Prevents broken UI, keeps cards uniform
- Alternatives considered: Always show all fields (leads to clutter)

### Decision: Use expandable/collapsible card pattern for "Show all details"
- Rationale: Familiar UX, keeps main view clean
- Alternatives considered: Modal dialog (can be used optionally for more details)

### Decision: Truncate long lists with ellipsis and tooltip for full view
- Rationale: Prevents overflow, keeps card compact
- Alternatives considered: Scrollable area (less clean visually)

### Decision: Button must be keyboard accessible and screen-reader friendly
- Rationale: Accessibility compliance
- Alternatives considered: Non-accessible button (not acceptable)

---
All research tasks complete. No open NEEDS CLARIFICATION remain.
