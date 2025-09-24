# Data Model: Zoho People Plus Sync Service

## Entities

### EmployeeRecord
- employee_id: string
- name: string
- contact_info: object
- job_title: string
- department: string
- all_other_fields: object

### CandidateDetails
- candidate_id: string
- employee_id: string (reference)
- profile: string
- skills: list[string]
- experience: string
- summary: string
- generated_at: datetime

### SyncService
- last_sync_time: datetime
- sync_interval: integer (minutes)
- access_token: string
- processed_employee_ids: list[string]

## Relationships
- CandidateDetails references EmployeeRecord by employee_id
- SyncService tracks processed_employee_ids to avoid duplicates

## Validation Rules
- Only create CandidateDetails for new employees (not previously processed)
- All fields from EmployeeRecord are passed to LLM for candidate generation
- Errors in sync or candidate generation are logged, not retried
- Maximum 50 employees processed per sync

---
This data model supports the requirements for a standalone Zoho sync service.
