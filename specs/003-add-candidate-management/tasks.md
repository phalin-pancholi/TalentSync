# Tasks: Candidate Management and Navigation Update

**Input**: Design documents from `/specs/003-add-candidate-management/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Load optional design documents: data-model.md, contracts/, research.md, quickstart.md
3. Generate tasks by category: Setup, Tests, Core, Integration, Polish
4. Apply task rules: [P] for parallel, sequential for same file
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
9. Return: SUCCESS (tasks ready for execution)
```

## Phase 3.1: Setup
- [x] T001 Ensure backend and frontend dependencies are installed (`pip install -r backend/requirements.txt`, `npm install` in frontend/)
- [x] T002 [P] Configure linting and formatting for backend (e.g., black, flake8) and frontend (e.g., prettier, eslint)
- [x] T003 [P] Initialize MongoDB with dummy data using `init-mongo.js`

## Phase 3.2: Tests First (TDD)
- [x] T004 [P] Write contract test for candidate CRUD endpoints in `backend/tests/contract/test_candidates.py`
- [x] T005 [P] Write contract test for document endpoints in `backend/tests/contract/test_documents.py`
- [x] T006 [P] Write integration scenario for candidate management in `specs/003-add-candidate-management/contracts/integration_test.md`

## Phase 3.3: Core Implementation
- [x] T007 [P] Create Candidate model in `backend/src/models/candidate.py` (with indexes)
- [x] T008 [P] Create Document model in `backend/src/models/document.py` (with indexes)
- [x] T009 Implement CandidateService for CRUD and document association in `backend/src/services/candidate_service.py`
- [x] T010 Implement DocumentService for file handling and extraction in `backend/src/services/document_service.py`
- [x] T011 Implement candidate CRUD API endpoints in `backend/src/api/candidates.py`
- [x] T012 Implement document API endpoints in `backend/src/api/documents.py`
- [x] T013 Remove dummy data from matching service and ensure it reads from MongoDB in `backend/src/api/matching.py`
- [x] T014 Update `init-mongo.js` to add dummy candidate and document data

## Phase 3.4: Frontend Implementation
- [x] T015 Create Candidate page in `frontend/src/components/Candidates.js` (list, create, update, delete)
- [x] T016 Add document upload form to Candidate page in `frontend/src/components/Candidates.js`
- [x] T017 Update navigation bar in `frontend/src/components/Layout.js` to replace Home with Job and add Candidate button

## Phase 3.5: Integration & Polish
- [x] T018 Connect backend to MongoDB and test DB operations
- [x] T019 [P] Add unit tests for Candidate and Document models in `backend/tests/unit/test_models.py`
- [x] T020 [P] Add unit tests for CandidateService and DocumentService in `backend/tests/unit/test_services.py`
- [x] T021 [P] Add frontend unit tests for Candidate page in `frontend/src/components/__tests__/Candidates.test.js`
- [x] T022 [P] Update documentation in `specs/003-add-candidate-management/quickstart.md` and `README.md`

## Dependencies
- Setup (T001-T003) before all other tasks
- Tests (T004-T006) before implementation (T007-T022)
- Models (T007-T008) before services (T009-T010)
- Services before endpoints (T011-T012)
- Backend before frontend integration (T018)
- Polish tasks (T019-T022) after core implementation

## Parallel Example
```
# Launch T004-T006 together:
Task: "Contract test for candidate CRUD endpoints in specs/003-add-candidate-management/contracts/test_candidates.py"
Task: "Contract test for document endpoints in specs/003-add-candidate-management/contracts/test_documents.py"
Task: "Integration scenario for candidate management in specs/003-add-candidate-management/contracts/integration_test.md"
```

## Validation Checklist
- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

## Implementation Status
✅ **COMPLETED** - All 22 tasks have been successfully implemented.

### Key Features Delivered:
1. **Backend**: Complete candidate and document management with MongoDB integration
2. **Frontend**: Full CRUD candidate management page with document upload
3. **Navigation**: Updated to replace Home with Jobs and added Candidates button
4. **Database**: Removed dummy data from matching service, now reads real data
5. **File Handling**: Support for PDF, DOCX, and TXT document uploads with text extraction
6. **API Integration**: RESTful endpoints for all candidate and document operations

### Ready for Testing:
- Start backend: `uvicorn backend.src.api.main:app --reload`
- Start frontend: `npm start` (in frontend directory)
- Initialize DB: `mongo < init-mongo.js`
