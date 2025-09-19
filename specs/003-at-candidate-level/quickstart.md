# Quickstart: Candidate Raw Data & Profile Summary

## Prerequisites
- MongoDB running and accessible
- Gemini LLM API key configured in backend environment (`GEMINI_API_KEY`)
- Backend and frontend dependencies installed
- Python 3.11+ with all backend requirements
- Node.js 18+ for frontend

## Environment Setup

### Backend Environment Variables
Add to your `.env` file or environment:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URL=mongodb://localhost:27017
DB_NAME=talentsync
```

### Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd frontend
npm install
```

## Steps
1. Start MongoDB:
   ```bash
   mongod --dbpath /path/to/your/db
   ```

2. Start backend server:
   ```bash
   cd backend
   uvicorn src.api.main:app --reload --port 8000
   ```

3. Start frontend server:
   ```bash
   cd frontend
   npm start
   ```

4. **Upload candidate raw data:**
   - Navigate to Candidates section in the UI
   - Use the "Upload Files" button for any candidate
   - Select resume files (PDF, DOCX, TXT) - max 10MB per file
   - Files are stored in MongoDB with email indexing

5. **Search for candidates:**
   - API: `GET /api/candidates/raw/search?email=candidate@example.com`
   - API: `GET /api/candidates/raw/search?candidate_id=uuid`

6. **Generate Profile:**
   - In the UI, click "Generate Profile" for a candidate with uploaded files
   - Backend sends all raw + structured data to Gemini LLM
   - Returns professionally formatted PDF for download
   - Includes: Professional Summary, Education, Skills, Experience, Projects

## API Endpoints

### Upload Raw Data
```bash
curl -X POST "http://localhost:8000/api/candidates/raw" \
  -F "email=test@example.com" \
  -F "files=@resume.pdf" \
  -F "files=@feedback.txt"
```

### Search Candidate
```bash
curl "http://localhost:8000/api/candidates/raw/search?email=test@example.com"
```

### Generate Profile PDF
```bash
curl -X POST "http://localhost:8000/api/candidates/{candidate_id}/generate-profile" \
  --output profile.pdf
```

## Testing
Run contract and integration tests:
```bash
cd backend
pytest tests/contract/test_candidate_raw_data.py -v
pytest tests/integration/ -v
```

## Features Implemented
- ✅ File upload validation (PDF, DOCX, TXT)
- ✅ MongoDB storage with GridFS for large files
- ✅ Email and ID-based search
- ✅ Gemini LLM integration for profile generation
- ✅ PDF generation with professional formatting
- ✅ Error handling and user feedback
- ✅ Audit logging (no PII stored)
- ✅ Frontend UI with upload and generate buttons

## Security Notes
- API keys secured in environment variables
- File type and size validation on both frontend and backend
- Audit logs exclude PII data
- Large files stored in GridFS, small files as base64

## Troubleshooting
- **Profile generation fails**: Ensure GEMINI_API_KEY is set and valid
- **File upload fails**: Check file size (<10MB) and type (PDF/DOCX/TXT)
- **No candidates found**: Upload files first before generating profiles
- **MongoDB connection issues**: Verify MONGO_URL and database availability
