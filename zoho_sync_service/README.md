# Zoho People Plus Sync Service

A standalone service that synchronizes employee data from Zoho People Plus and generates candidate details using LLM integration.

## Features

- **Automated Sync**: Fetches employee data from Zoho People Plus API every 5 minutes
- **LLM Integration**: Uses Google's Gemini Pro to generate candidate profiles, skills, experience summaries
- **Duplicate Prevention**: Only creates candidate details for new employees
- **Error Handling**: Robust error handling with logging and graceful degradation
- **REST API**: Provides endpoints for manual sync and data retrieval
- **Rate Limiting**: Respects API limits by processing maximum 50 employees per sync

## Prerequisites

- Docker and Docker Compose
- Zoho People Plus access token
- Google API key for Gemini Pro
- MongoDB database (provided by main application)

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ZOHO_ACCESS_TOKEN` | Zoho People Plus API access token | - | Yes |
| `GOOGLE_API_KEY` | Google API key for Gemini Pro | - | Yes |
| `SYNC_INTERVAL` | Sync interval in minutes | 5 | No |
| `MONGO_URL` | MongoDB connection URL | See docker-compose.yml | No |
| `DB_NAME` | Database name | talentsync_db | No |

## Setup

1. **Configure Environment Variables**:
   ```bash
   export ZOHO_ACCESS_TOKEN="your_zoho_token"
   export GOOGLE_API_KEY="your_google_api_key"
   ```

2. **Build and Start Service**:
   ```bash
   docker-compose up --build zoho-sync-service
   ```

3. **Verify Service is Running**:
   ```bash
   curl http://localhost:8002/health
   ```

## API Endpoints

### Health Check
- **GET** `/health` - Service health status
- **GET** `/` - Root endpoint with service info

### Sync Operations
- **POST** `/sync` - Trigger manual sync operation
- **GET** `/sync/status` - Get last sync status and statistics

### Data Retrieval
- **GET** `/candidates` - Get all generated candidate details
- **GET** `/candidates/{employee_id}` - Get candidate details for specific employee
- **GET** `/employees` - Get all employee records

## Data Flow

1. **Fetch**: Service calls Zoho People Plus API to retrieve employee records
2. **Store**: Employee data is stored in MongoDB employees collection
3. **Generate**: Each employee's data is sent to Google Gemini Pro LLM
4. **Parse**: LLM response is parsed to extract profile, skills, experience, summary
5. **Persist**: Candidate details are stored in MongoDB candidates collection
6. **Sync**: Process repeats every 5 minutes automatically

## Database Collections

### `employees`
Stores raw employee data from Zoho:
```json
{
  "employee_id": "EMP001",
  "name": "John Doe",
  "job_title": "Software Engineer",
  "department": "Engineering",
  "contact_info": {...},
  "all_other_fields": {...}
}
```

### `candidates`
Stores LLM-generated candidate details:
```json
{
  "candidate_id": "cand_EMP001",
  "employee_id": "EMP001",
  "profile": "Experienced software professional...",
  "skills": ["Python", "FastAPI", "MongoDB"],
  "experience": "5+ years in software development...",
  "summary": "Skilled engineer with expertise..."
}
```

### `sync_status`
Tracks sync operations:
```json
{
  "last_sync_time": "2025-09-23T10:30:00Z",
  "sync_interval": 5,
  "processed_employee_ids": ["EMP001", "EMP002"],
  "sync_count": 42,
  "last_error": null
}
```

## Error Handling

- **Zoho API Errors**: Logged and sync skipped, retry on next interval
- **LLM Generation Errors**: Logged and fallback candidate details created
- **Database Errors**: Logged and operation continues where possible
- **Service Failures**: Auto-restart via Docker Compose restart policy

## Monitoring

- **Logs**: All operations logged with INFO/ERROR levels
- **Health Endpoint**: `/health` for service monitoring
- **Sync Status**: `/sync/status` for sync operation monitoring
- **Metrics**: Available via sync status endpoint

## Testing

### Contract Tests
```bash
pytest specs/009-integrate-zoho-people/contracts/
```

### Integration Tests
```bash
pytest zoho_sync_service/tests/
```

## Troubleshooting

### Service Won't Start
- Check environment variables are set
- Verify MongoDB is running and accessible
- Check Docker logs: `docker-compose logs zoho-sync-service`

### Sync Failures
- Verify Zoho access token is valid
- Check Google API key permissions
- Review logs for specific error messages
- Test connectivity: `curl http://localhost:8002/sync/status`

### No Candidates Generated
- Ensure employees exist in Zoho
- Check LLM integration: Google API key and quotas
- Verify employees are not already processed (check processed_employee_ids in sync status)

## Architecture

The service follows a clean architecture pattern:

- **Models** (`models.py`): Pydantic models for data validation
- **Service** (`service.py`): Core business logic and external integrations
- **API** (`api.py`): FastAPI REST endpoints
- **Tests** (`tests/`): Integration and contract tests

## Security

- API tokens stored as environment variables
- No hardcoded credentials
- MongoDB access restricted to internal network
- Service runs in isolated Docker container

## Performance

- **Sync Interval**: 5 minutes (configurable)
- **Batch Size**: 50 employees per sync (API limit)
- **Async Operations**: Non-blocking I/O for database and API calls
- **Error Recovery**: Graceful failure handling without service interruption