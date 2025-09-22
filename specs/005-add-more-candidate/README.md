# Add More Candidate Detail Functionality

## Overview
This feature allows users to upload additional details for candidates via document upload directly from the candidate card. The system extracts text from uploaded .txt or .pdf files and stores it as structured extra details in the database.

## Features
- **Upload Button**: Green file upload icon on each candidate card
- **File Support**: .txt and .pdf files up to 5MB
- **Text Extraction**: Automatic text extraction using existing file parsing service
- **Type Detection**: Automatic categorization based on filename (feedback, skills, summary)
- **Display**: Extra details shown in candidate card with timestamps and type badges
- **Error Handling**: Comprehensive validation and user feedback

## Technical Implementation

### Backend Changes
- **Models**: Added `CandidateExtraDetail` model and updated `CandidateResponse`
- **Service**: Extended `CandidateService` with upload and retrieval methods
- **API**: New endpoints for uploading and retrieving extra details
- **Database**: MongoDB collection `candidate_extra_details`

### Frontend Changes
- **UI**: Upload button and dialog for file selection
- **Display**: Extra details section in candidate cards
- **Progress**: Upload progress and result feedback via toast notifications

### File Processing
- Validates file type (.txt, .pdf only)
- Checks file size (5MB maximum)
- Extracts text content (doesn't store file)
- Detects content type from filename
- Stores only text content with metadata

## API Endpoints

### Upload Extra Details
```
POST /api/candidates/{candidate_id}/extra-details
Content-Type: multipart/form-data

Body: file (binary)
```

**Response**: CandidateExtraDetailResponse
```json
{
  "id": "string",
  "candidate_id": "string", 
  "text_content": "string",
  "type": "string|null",
  "created_at": "datetime"
}
```

### Get Extra Details
```
GET /api/candidates/{candidate_id}/extra-details
```

**Response**: Array of CandidateExtraDetailResponse

## Testing
- **Contract Tests**: File upload validation and response format
- **Integration Tests**: End-to-end workflow testing
- **Unit Tests**: Text extraction and service logic testing

## Error Handling
- File validation (type, size, content)
- User feedback via toast notifications
- Graceful degradation for parsing failures
- HTTP status codes for API errors

---
*Feature complete and ready for use.*