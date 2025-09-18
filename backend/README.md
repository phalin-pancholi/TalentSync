# TalentSync Backend

Modular Python backend API for the TalentSync talent management system.

## Architecture

This backend follows a modular architecture with clear separation of concerns:

```
backend/
├── src/
│   ├── api/           # API route definitions
│   │   ├── main.py    # FastAPI app and middleware
│   │   ├── jobs.py    # Job posting endpoints
│   │   ├── upload.py  # File upload endpoints
│   │   └── matching.py # Candidate matching endpoints
│   ├── models/        # Pydantic models
│   │   ├── job_posting.py
│   │   └── candidate.py
│   ├── services/      # Business logic
│   │   ├── db_service.py
│   │   ├── job_service.py
│   │   └── matching_service.py
│   └── utils/         # Shared utilities
│       ├── config.py
│       └── logging.py
└── tests/             # Test suites
    ├── contract/      # API contract tests
    ├── integration/   # Integration tests
    └── unit/          # Unit tests
```

## Key Features

- **Modular Design**: Clear separation between API routes, business logic, and data models
- **Async/Await**: Full async support using FastAPI and Motor
- **Type Safety**: Pydantic models for request/response validation
- **Test Coverage**: Contract, integration, and unit tests
- **MongoDB Integration**: Async MongoDB operations using Motor
- **File Upload**: Support for PDF and Word document processing
- **Candidate Matching**: Algorithm for matching candidates to job postings

## Quick Start

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection details
   ```

3. **Start MongoDB**
   ```bash
   # Using Docker
   docker-compose up -d
   ```

4. **Run the Server**
   ```bash
   cd backend
   uvicorn src.api.main:app --reload
   ```

5. **Access API Documentation**
   - Interactive docs: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

## API Endpoints

### Jobs
- `GET /api/jobs/` - List all job postings
- `POST /api/jobs/` - Create a new job posting
- `GET /api/jobs/{id}` - Get a specific job posting
- `PUT /api/jobs/{id}` - Update a job posting
- `DELETE /api/jobs/{id}` - Delete a job posting

### File Upload
- `POST /api/upload/job` - Upload job document (PDF/Word)

### Candidate Matching
- `GET /api/jobs/{id}/candidates` - Get candidates matching a job

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Structure Guidelines

1. **Models** (`src/models/`): Pydantic models for data validation
2. **Services** (`src/services/`): Business logic and database operations
3. **API Routes** (`src/api/`): FastAPI route definitions
4. **Utils** (`src/utils/`): Shared utilities and configuration

### Adding New Features

1. Define models in `src/models/`
2. Implement business logic in `src/services/`
3. Create API routes in `src/api/`
4. Add tests in appropriate test directories
5. Update documentation

## Environment Variables

- `MONGO_URL`: MongoDB connection string
- `DB_NAME`: Database name
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Contributing

1. Follow the modular architecture patterns
2. Add tests for new functionality
3. Update documentation
4. Use type hints and Pydantic models
5. Follow async/await patterns