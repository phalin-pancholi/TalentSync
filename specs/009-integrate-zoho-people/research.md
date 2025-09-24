# Research: Zoho People Plus Integration Service

## Decision: Sync Interval
- Chosen: 5 minutes
- Rationale: Frequent enough to keep data fresh, not so frequent as to overload API or system.
- Alternatives: 1 minute (too frequent), 1 hour (too slow for updates)

## Decision: Error Handling for Zoho API Call
- Chosen: Log the error and skip failed syncs
- Rationale: Ensures service continues running and does not halt on API issues.
- Alternatives: Retry logic (could be added later), halt service (not robust)

## Decision: Error Handling for LLM Candidate Generation
- Chosen: Log the error and skip failed candidates
- Rationale: Allows processing to continue for other employees.
- Alternatives: Retry logic, halt service

## Decision: Required Fields from Zoho Employee Data
- Chosen: All fields
- Rationale: Maximizes information for candidate generation; can be filtered later if needed.
- Alternatives: Subset of fields (requires more business input)

## Decision: Employee Processing Limit per Sync
- Chosen: 50 employees per sync
- Rationale: Avoids rate limits and excessive load; scalable for most organizations.
- Alternatives: Unlimited (risk of API throttling), lower/higher limits

## Decision: Candidate Creation Logic
- Chosen: Only create candidate details for new employees; skip existing
- Rationale: Prevents duplicate candidate records; keeps sync efficient.
- Alternatives: Update existing candidates (requires more logic)

## Best Practices: Service Design
- Service should be standalone, not modify existing backend code
- Use environment variables for access token and interval configuration
- Log all errors and sync events for observability
- Avoid installing new packages; use only existing dependencies

## Best Practices: Docker Compose Update
- Add new service to docker-compose.yml
- Ensure service is isolated and does not affect existing backend
- Use restart policy to ensure reliability

## Patterns: LLM Integration
- Send employee data to LLM one by one
- Handle LLM errors gracefully
- Persist generated candidate details

---
All clarifications from the spec are resolved for planning.
