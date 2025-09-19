# Quickstart: Candidate Management Feature

This guide helps you set up and test the candidate management feature, including CRUD operations, document upload, and navigation updates.

## Prerequisites
- Backend: Python 3.11, FastAPI, MongoDB
- Frontend: React, Node.js
- MongoDB running (local or Docker)

## 1. Database Initialization
- Add dummy candidate and document data using `init-mongo.js`.
- Example: `mongo <init-mongo.js>`

## 2. Backend Setup
- Install dependencies: `pip install -r backend/requirements.txt`
- Start backend: `uvicorn backend.src.api.main:app --reload`

## 3. Frontend Setup
- Install dependencies: `cd frontend && npm install`
- Start frontend: `npm start`

## 4. Feature Usage
- Access the app in your browser (default: http://localhost:3000)
- Use the navigation bar: Job and Candidate buttons are present
- Go to Candidate page:
  - Create candidate via form (name, email, skills required)
  - Upload candidate document (PDF, DOCX, TXT)
  - View, update, or delete candidates

## 5. Testing
- Backend: `pytest backend/tests/`
- Frontend: `npm test`

## 6. Notes
- Removing dummy data from matching service is required; ensure it reads from MongoDB
- Candidate and Document collections are related by ObjectId
- Indexes are set for efficient search and uniqueness

---

For more details, see data-model.md and contracts/.
