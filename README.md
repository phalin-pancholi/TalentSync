# TalentSync

A comprehensive talent matching platform that connects job seekers with opportunities using AI-powered job description processing.

## Features

### Core Features
- Job posting management
- Candidate profile management 
- AI-powered job matching

### 🆕 NEW: LLM-based Job Upload
Upload job description documents (PDF or text files) and automatically extract structured job information using AI:
- **Supported formats**: PDF, TXT files
- **AI extraction**: Uses Google Gemini to extract job details
- **Flexible structure**: Handles missing or incomplete information gracefully
- **Database integration**: Automatically creates job entries

## Quick Start

### LLM Job Upload Feature

1. **Setup Environment**:
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"
   export MONGODB_URL="mongodb://localhost:27017"
   ```

2. **Start the backend**:
   ```bash
   cd backend
   uvicorn src.api.main:app --reload
   ```

3. **Upload a job description**:
   ```bash
   curl -X POST "http://localhost:8000/api/jobs/upload_llm" \
     -F "file=@your_job_description.pdf"
   ```

For detailed setup and troubleshooting, see [specs/002-add-llm-based/quickstart.md](specs/002-add-llm-based/quickstart.md).

## API Endpoints

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create a new job
- `GET /api/jobs/{id}` - Get job by ID
- `PUT /api/jobs/{id}` - Update job
- `DELETE /api/jobs/{id}` - Delete job
- **`POST /api/jobs/upload_llm`** - 🆕 Upload job description document for AI extraction

### Candidates  
- `GET /api/candidates/` - List all candidates
- `POST /api/candidates/` - Create candidate profile
- `GET /api/candidates/{id}` - Get candidate by ID

### Matching
- `POST /api/matching/` - Find job matches for candidate
- `GET /api/matching/{job_id}/candidates` - Find candidates for job

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB
- **AI/ML**: Langchain + Google Gemini
- **File Processing**: PyPDF2
- **Testing**: pytest

### Frontend  
- **Framework**: React
- **Styling**: Tailwind CSS
- **Build Tool**: Craco

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Specific test suites
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests 
pytest tests/contract/      # Contract tests
```

### Project Structure
```
backend/
├── src/
│   ├── api/           # FastAPI routes
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── tests/             # Test suites
└── requirements.txt   # Dependencies

frontend/
├── src/
│   ├── components/    # React components
│   ├── hooks/         # Custom hooks
│   └── lib/          # Utilities
└── package.json      # Dependencies
```

## Contributing

1. Create a feature branch from `master`
2. Follow the specification-driven development process in `specs/`
3. Write tests before implementation (TDD)
4. Ensure all tests pass
5. Update documentation as needed

## License

[Add your license information here]
