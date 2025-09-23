# Research for Candidate Location and Experience Fields

## Unknowns from Technical Context
- What format should experience be in? (e.g., years, months, text description?)
- Is location a city, region, country, or free text?

## Research Tasks

### 1. Candidate Experience Format
- **Decision:** Use years of experience as a numeric field (e.g., 3.5 years). Optionally, allow a text description for special cases (e.g., "Internship", "Entry-level").
- **Rationale:** Numeric years is standard for filtering and matching. Text allows flexibility for edge cases.
- **Alternatives considered:** Only text (less filterable), only integer years (less precise).

### 2. Candidate Location Format
- **Decision:** Use free text for location, but recommend city and country (e.g., "Bangalore, India").
- **Rationale:** Free text is flexible for remote, hybrid, or special cases. City+country is most useful for recruiters.
- **Alternatives considered:** Strict city/country fields (less flexible for remote/relocation cases).

## Best Practices
- Always display "Not provided" if a field is missing.
- Validate numeric experience is non-negative.
- Location should be human-readable and not empty if provided.

## Integration Patterns
- Backend: Add `location` (string) and `experience` (float or string) to Candidate model, API, and database.
- Frontend: Display these fields on candidate cards, fallback to "Not provided" if missing.
- LLM prompt: Ensure prompt template requests extraction of location and experience from candidate data.

---

All clarifications resolved for this feature. Ready for Phase 1 design.
