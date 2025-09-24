# Quickstart: Zoho People Plus Sync Service

## Prerequisites
- Zoho People Plus access token
- Docker installed
- Existing application running (do not modify existing backend)

## Steps
1. Add the new sync service to `docker-compose.yml`:
   - Define service with environment variables for access token and sync interval
   - Set restart policy to always
2. Build and start the service using Docker Compose:
   - `docker-compose up --build zoho-sync-service`
3. Service will run every 5 minutes, fetch up to 50 employees from Zoho, and send each to LLM for candidate generation
4. Candidate details are persisted for new employees only
5. Check logs for sync status and error handling

## Environment Variables
- `ZOHO_ACCESS_TOKEN`: Zoho API access token
- `SYNC_INTERVAL`: Interval in minutes (default: 5)

## Troubleshooting
- If Zoho API call fails, check logs for error details
- If LLM candidate generation fails, check logs for error details
- Ensure no duplicate candidate records are created

---
This quickstart enables setup and validation of the Zoho sync service without modifying existing backend code or installing new packages.
