# Zoho Sync Service - API Data Flow Documentation

## Overview
This document describes the detailed data flow for each API endpoint in the Zoho People Plus sync service.

---

## 1. GET /health

### Purpose
Health check endpoint for service monitoring

### Data Flow
```
Client Request
    ↓
FastAPI Router (/health)
    ↓
Return Static Response
    ↓
Response: {"status": "healthy", "service": "zoho-sync-service"}
```

### Details
- **Input**: None
- **Processing**: Static response generation
- **Output**: Health status JSON
- **Database Access**: None
- **External APIs**: None

---

## 2. POST /sync (Manual Sync Trigger)

### Purpose
Trigger a manual synchronization operation

### Data Flow
```
Client Request (POST /sync)
    ↓
FastAPI Router (/sync)
    ↓
ZohoSyncService.run_sync()
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    SYNC OPERATION FLOW                     │
├─────────────────────────────────────────────────────────────┤
│ 1. Fetch Employees from Zoho                               │
│    ↓                                                        │
│    HTTP GET → https://people.zoho.in/people/api/forms/     │
│                P_EmployeeView/records                       │
│    Headers: Authorization: Zoho-oauthtoken {token}         │
│    Params: limit=50                                         │
│    ↓                                                        │
│    Raw Employee Data (JSON Array)                          │
│                                                             │
│ 2. For Each Employee:                                       │
│    ↓                                                        │
│    Parse Employee Data → EmployeeRecord Model              │
│    ↓                                                        │
│    MongoDB.employees.replace_one()                         │
│    (Upsert: employee_id as key)                           │
│    ↓                                                        │
│    Check if Candidate Exists                               │
│    MongoDB.candidates.find_one({employee_id})             │
│    ↓                                                        │
│    If NOT EXISTS:                                          │
│        ↓                                                    │
│        Generate LLM Prompt                                 │
│        ↓                                                    │
│        Google Gemini Pro API Call                         │
│        LLM.invoke(employee_data_prompt)                    │
│        ↓                                                    │
│        Parse LLM Response (JSON)                           │
│        ↓                                                    │
│        Create CandidateDetails Model                      │
│        ↓                                                    │
│        MongoDB.candidates.insert_one()                    │
│    ↓                                                        │
│ 3. Update Sync Status                                       │
│    MongoDB.sync_status.replace_one()                      │
│    (Store: processed_employee_ids, timestamps, errors)    │
└─────────────────────────────────────────────────────────────┘
    ↓
Compile Sync Result
    ↓
Response: {
  "message": "Manual sync completed",
  "sync_result": {
    "timestamp": "2025-09-23T10:30:00Z",
    "employees_fetched": 25,
    "employees_processed": 25,
    "candidates_created": 8,
    "errors": []
  }
}
```

### Detailed Processing Steps

#### Step 1: Zoho API Call
```
Request: GET https://people.zoho.in/people/api/forms/P_EmployeeView/records
Headers: 
  - Authorization: Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}
  - Content-Type: application/json
Params:
  - limit: 50

Response Format:
{
  "response": {
    "result": [
      {
        "Employeeid": "EMP001",
        "Firstname": "John",
        "Lastname": "Doe",
        "Designation": "Software Engineer",
        "Department": "Engineering",
        "Emailid": "john.doe@example.com",
        "Mobile": "+1234567890",
        // ... other Zoho fields
      }
    ]
  }
}
```

#### Step 2: Employee Processing
```
For each employee in response.result:
  1. Transform Zoho data → EmployeeRecord:
     {
       "employee_id": "EMP001",
       "name": "John Doe",
       "contact_info": {"email": "john.doe@example.com", "phone": "+1234567890"},
       "job_title": "Software Engineer",
       "department": "Engineering",
       "all_other_fields": {original_zoho_data},
       "created_at": "2025-09-23T10:30:00Z",
       "updated_at": "2025-09-23T10:30:00Z"
     }
  
  2. Database Upsert:
     MongoDB.employees.replace_one(
       filter: {"employee_id": "EMP001"},
       replacement: employee_record,
       upsert: true
     )
  
  3. Check Candidate Existence:
     existing_candidate = MongoDB.candidates.find_one({"employee_id": "EMP001"})
     
  4. If no existing candidate, generate via LLM...
```

#### Step 3: LLM Processing
```
Prompt Generation:
"Based on the following employee information, generate a comprehensive candidate profile:
- Name: John Doe
- Job Title: Software Engineer
- Department: Engineering
- Contact: {email, phone}
- Additional Info: {all_zoho_fields}

Please provide:
1. Professional profile summary (2-3 sentences)
2. Key skills (comma-separated list)
3. Experience summary (2-3 sentences)
4. Overall candidate summary (3-4 sentences)

Format as JSON: {profile, skills, experience, summary}"

LLM API Call:
GoogleGenerativeAI.invoke(prompt) → response.content

Response Parsing:
{
  "profile": "Experienced software professional with expertise in backend development...",
  "skills": "Python, FastAPI, MongoDB, Docker, Git",
  "experience": "5+ years in software development with focus on scalable web applications...",
  "summary": "John is a skilled software engineer with strong technical abilities..."
}

Transform to CandidateDetails:
{
  "candidate_id": "cand_EMP001",
  "employee_id": "EMP001",
  "profile": "...",
  "skills": ["Python", "FastAPI", "MongoDB", "Docker", "Git"],
  "experience": "...",
  "summary": "...",
  "generated_at": "2025-09-23T10:30:00Z"
}

Database Insert:
MongoDB.candidates.insert_one(candidate_details)
```

---

## 3. GET /candidates

### Purpose
Retrieve all generated candidate details

### Data Flow
```
Client Request (GET /candidates)
    ↓
FastAPI Router (/candidates)
    ↓
ZohoSyncService.get_all_candidates()
    ↓
MongoDB Query
    ↓
cursor = db.candidates.find({})
    ↓
Iterate Through Results
    ↓
For each document:
  - Convert ObjectId to string
  - Add to results array
    ↓
Response: Array of Candidate Objects
[
  {
    "_id": "64f8a1b2c3d4e5f6g7h8i9j0",
    "candidate_id": "cand_EMP001",
    "employee_id": "EMP001",
    "profile": "Experienced software professional...",
    "skills": ["Python", "FastAPI", "MongoDB"],
    "experience": "5+ years in software development...",
    "summary": "John is a skilled software engineer...",
    "generated_at": "2025-09-23T10:30:00Z"
  },
  // ... more candidates
]
```

### Database Query Details
```sql
-- MongoDB Query (conceptual SQL equivalent)
SELECT * FROM candidates
-- Actual MongoDB:
db.candidates.find({})

-- Processing:
for document in cursor:
    document["_id"] = str(document["_id"])  # ObjectId → String
    results.append(document)
```

---

## 4. GET /candidates/{employee_id}

### Purpose
Retrieve candidate details for a specific employee

### Data Flow
```
Client Request (GET /candidates/EMP001)
    ↓
FastAPI Router (/candidates/{employee_id})
    ↓
Extract employee_id from URL path
    ↓
MongoDB Query
    ↓
candidate = db.candidates.find_one({"employee_id": "EMP001"})
    ↓
Check if Found
    ↓
If Found:
  - Convert ObjectId to string
  - Return candidate object
    ↓
If Not Found:
  - Raise HTTPException(404)
    ↓
Response: Single Candidate Object or 404 Error
```

### Database Query Details
```sql
-- MongoDB Query (conceptual SQL equivalent)
SELECT * FROM candidates WHERE employee_id = 'EMP001' LIMIT 1
-- Actual MongoDB:
db.candidates.find_one({"employee_id": "EMP001"})

-- Response Processing:
if candidate:
    candidate["_id"] = str(candidate["_id"])
    return candidate
else:
    raise HTTPException(404, "Candidate not found for employee: EMP001")
```

---

## 5. GET /sync/status

### Purpose
Get current synchronization status and statistics

### Data Flow
```
Client Request (GET /sync/status)
    ↓
FastAPI Router (/sync/status)
    ↓
MongoDB Query
    ↓
status = db.sync_status.find_one({})
    ↓
Check if Found
    ↓
If Found:
  - Convert ObjectId to string
  - Return status object
    ↓
If Not Found:
  - Return "No sync operations completed yet"
    ↓
Response: Sync Status Object
{
  "_id": "64f8a1b2c3d4e5f6g7h8i9j0",
  "last_sync_time": "2025-09-23T10:30:00Z",
  "sync_interval": 5,
  "access_token": "zoho_token_here",
  "processed_employee_ids": ["EMP001", "EMP002", "EMP003"],
  "sync_count": 42,
  "last_error": null
}
```

---

## 6. GET /employees

### Purpose
Retrieve all employee records from Zoho

### Data Flow
```
Client Request (GET /employees)
    ↓
FastAPI Router (/employees)
    ↓
MongoDB Query
    ↓
cursor = db.employees.find({})
    ↓
Iterate Through Results
    ↓
For each document:
  - Convert ObjectId to string
  - Add to results array
    ↓
Response: Array of Employee Objects
[
  {
    "_id": "64f8a1b2c3d4e5f6g7h8i9j0",
    "employee_id": "EMP001",
    "name": "John Doe",
    "contact_info": {"email": "john.doe@example.com", "phone": "+1234567890"},
    "job_title": "Software Engineer",
    "department": "Engineering",
    "all_other_fields": {original_zoho_data},
    "created_at": "2025-09-23T10:30:00Z",
    "updated_at": "2025-09-23T10:30:00Z"
  },
  // ... more employees
]
```

---

## Error Handling Data Flow

### Zoho API Errors
```
Zoho API Call Fails
    ↓
requests.exceptions.RequestException
    ↓
Log Error: "Failed to fetch employees from Zoho: {error}"
    ↓
Update sync_status with error
    ↓
Return sync_result with errors array populated
```

### LLM Generation Errors
```
LLM API Call Fails
    ↓
Exception in generate_candidate_details_with_llm()
    ↓
Log Error: "Failed to generate candidate details: {error}"
    ↓
Create Fallback Candidate Details:
{
  "candidate_id": "cand_EMP001",
  "employee_id": "EMP001",
  "profile": "Employee: John Doe",
  "skills": ["Software Engineer"],
  "experience": "Experience information unavailable",
  "summary": "Basic profile for John Doe"
}
    ↓
Continue Processing Next Employee
```

### Database Errors
```
MongoDB Operation Fails
    ↓
Log Error: "Database operation failed: {error}"
    ↓
Continue Processing (graceful degradation)
    ↓
Include error in sync_result.errors array
```

---

## Background Periodic Sync

### Data Flow
```
Service Startup
    ↓
asyncio.create_task(start_periodic_sync())
    ↓
Infinite Loop:
  1. await run_sync()  # Same flow as manual sync
  2. await asyncio.sleep(sync_interval * 60)  # Wait 5 minutes
  3. Repeat
    ↓
On Error:
  - Log error
  - Wait 60 seconds (shorter retry interval)
  - Continue loop
```

This comprehensive data flow documentation shows exactly how data moves through each API endpoint, including all database operations, external API calls, error handling, and response formatting.