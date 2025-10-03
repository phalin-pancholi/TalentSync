# TalentSync

A comprehensive talent matching platform that connects job seekers with opportunities using AI-powered job description processing and candidate resume extraction.

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

### 🆕 NEW: LLM-based Candidate Upload
Upload candidate resumes/CVs and automatically extract structured candidate information using AI:
- **Supported formats**: PDF, DOCX, TXT files
- **AI extraction**: Uses Google Gemini to extract candidate details (name, email, skills, experience, education)
- **Flexible structure**: Allows saving candidates with missing fields
- **Raw text storage**: Stores original text for future reference
- **Duplicate detection**: Prevents duplicate candidates based on file hash
- **Error handling**: Graceful fallback for parsing or LLM failures

### 🆕 NEW: Profile Summary Generation
Generate professional PDF profile summaries for candidates using AI:
- **One-click generation**: Purple download button on candidate cards
- **Comprehensive data**: Combines structured data, resume text, and feedback
- **AI-powered**: Uses Google Gemini to create compelling profile summaries
- **Professional format**: Includes summary, education, skills, experience sections
- **Instant download**: PDF automatically downloads when ready
- **Error handling**: Graceful handling of LLM service issues

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

### LLM Candidate Upload Feature

1. **Upload a candidate resume**:
   ```bash
   curl -X POST "http://localhost:8000/api/candidates/upload" \
     -F "file=@candidate_resume.pdf"
   ```

### Profile Summary Generation Feature

1. **Generate profile summary for a candidate**:
   ```bash
   curl -X POST "http://localhost:8000/api/candidates/{candidate_id}/profile-summary" \
     -H "Accept: application/pdf" \
     --output "profile_summary.pdf"
   ```

2. **Via Frontend**: 
   - Navigate to Candidates page
   - Click the purple download button on any candidate card
   - PDF automatically downloads

For detailed setup and troubleshooting, see [specs/002-add-llm-based/quickstart.md](specs/002-add-llm-based/quickstart.md), [specs/004-there-is-funtionality/quickstart.md](specs/004-there-is-funtionality/quickstart.md), and [specs/006-profile-summary-functionality/quickstart.md](specs/006-profile-summary-functionality/quickstart.md).

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
- **`POST /api/candidates/upload`** - 🆕 Upload resume/CV document for AI extraction
- **`POST /api/candidates/{id}/profile-summary`** - 🆕 Generate PDF profile summary using AI

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

## zap scan
```
docker run   --network talentsync_talentsync-network   -v $(pwd):/zap/wrk/:rw   -t zaproxy/zap-stable:latest   zap-full-scan.py   -t http://backend:8001   -g gen.conf   -r testreport.html
```

```
docker run   --network talentsync_talentsync-network   -v $(pwd):/zap/wrk/:rw   -t zaproxy/zap-stable:latest   zap-full-scan.py   -t http://frontend:3000   -g gen.conf   -r testreport.html
```



## Contributing

1. Create a feature branch from `master`
2. Follow the specification-driven development process in `specs/`
3. Write tests before implementation (TDD)
4. Ensure all tests pass
5. Update documentation as needed

## License

[Add your license information here]
