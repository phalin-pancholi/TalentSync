# Quickstart: LLM-based Job Upload Endpoint

## Prerequisites
- Python 3.11
- FastAPI
- Langchain
- Gemini
- PyPDF2
- MongoDB running
- Google API Key for Gemini

## Setup
1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   export MONGODB_URL="mongodb://localhost:27017"
   export DATABASE_NAME="talentsync"
   ```

3. Start MongoDB (if not running):
   ```bash
   mongod
   ```

## Running the Service
1. Start backend server:
   ```bash
   cd backend
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Verify the endpoint is available:
   ```bash
   curl http://localhost:8000/docs
   ```

## Testing the LLM Job Upload Feature

### Upload a job description document
```bash
# Upload a text file
curl -X POST "http://localhost:8000/api/jobs/upload_llm" \
  -F "file=@/path/to/job_description.txt" \
  -H "Content-Type: multipart/form-data"

# Upload a PDF file  
curl -X POST "http://localhost:8000/api/jobs/upload_llm" \
  -F "file=@/path/to/job_description.pdf" \
  -H "Content-Type: multipart/form-data"
```

### Expected Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Software Engineer",
  "description": "We are seeking a talented software engineer...",
  "skills": ["Python", "JavaScript", "React"],
  "experience_level": "3+ years",
  "department": "Engineering", 
  "location": "San Francisco, CA",
  "created_at": "2025-09-19T10:30:00Z",
  "updated_at": "2025-09-19T10:30:00Z"
}
```

### Verify in Database
```bash
# Connect to MongoDB
mongo
use talentsync
db.job_postings.find({"id": "550e8400-e29b-41d4-a716-446655440000"})
```

## Troubleshooting

### Common Issues

1. **"LLM service is currently unavailable"**
   - Check that `GOOGLE_API_KEY` environment variable is set
   - Verify the API key is valid and has Gemini access
   - Check internet connectivity

2. **"Unsupported file type"**
   - Ensure file has .pdf, .txt, or .text extension
   - Supported MIME types: application/pdf, text/plain

3. **"No text content found in file"**
   - Check that the uploaded file contains readable text
   - For PDFs, ensure they contain text (not just images)

4. **Database connection errors**
   - Verify MongoDB is running: `mongod --version`
   - Check MONGODB_URL environment variable
   - Ensure database permissions are correct

5. **Import errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.11+)

### Testing with Sample Files
```bash
# Create a sample job description
echo "Software Engineer - Full Stack

Job Description:
We are seeking a talented Full Stack Software Engineer.

Requirements:
- 3+ years experience
- Python, JavaScript skills
- Bachelor's degree

Location: San Francisco, CA
Department: Engineering" > sample_job.txt

# Upload it
curl -X POST "http://localhost:8000/api/jobs/upload_llm" \
  -F "file=@sample_job.txt"
```

### Development Tips
- Use the FastAPI docs at `http://localhost:8000/docs` for interactive testing
- Check logs for detailed error information
- All job fields are optional - missing information will be set to `null`
- The endpoint is idempotent - multiple uploads create separate job entries
