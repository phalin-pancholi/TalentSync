# Tasks: Add More Candidate Detail Functionality

**Input**: Design documents from `/specs/005-add-more-candidate/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md and design docs
2. Generate setup, test, model, endpoint, integration, and polish tasks
3. Mark [P] for parallelizable tasks
4. Number tasks sequentially (T001, T002...)
5. Validate all contracts, models, and endpoints are covered
6. Provide parallel execution examples
7. Return: SUCCESS (tasks ready for execution)
```

## Tasks

### Setup
✅ T001  Setup test data files for contract tests in `backend/src/tests/data/` [P] - COMPLETED

### Contract Tests
✅ T002  [P] Implement contract test for uploading candidate extra details (`backend/tests/contract/test_candidate_extra_details.py`) - COMPLETED

### Models
✅ T003  [P] Add `CandidateExtraDetail` model to `backend/src/models/candidate.py` and update `Candidate` model to reference extra details - COMPLETED

### Services
✅ T004  [P] Implement service logic in `backend/src/services/candidate_service.py` to handle text extraction from .txt/.pdf and storing extra details in DB - COMPLETED

### API Endpoint
✅ T005  Implement `POST /api/candidates/{candidate_id}/extra-details` endpoint in `backend/src/api/candidates.py` to accept file upload, validate, extract text, and call service - COMPLETED

### Integration
✅ T006  Integrate new extra details logic with MongoDB in `backend/src/services/db_service.py` if needed - COMPLETED

### Frontend
✅ T007  Update `frontend/src/components/Candidates.js` to add "Upload Details" button on candidate card, file input, and upload logic (max 5MB, .txt/.pdf only) - COMPLETED
✅ T008  Show upload progress and result (success/error) in candidate card UI - COMPLETED
✅ T009  Display uploaded extra details for candidate in candidate card - COMPLETED

### Integration Tests
✅ T010  [P] Add integration test for uploading and displaying extra details in `backend/tests/integration/test_candidate_extra_details.py` - COMPLETED

### Polish
✅ T011  [P] Add unit tests for text extraction logic in `backend/tests/unit/test_candidate_extra_details.py` - COMPLETED
✅ T012  [P] Add error handling and user feedback for all upload failure cases (frontend/backend) - COMPLETED
✅ T013  [P] Update documentation in `specs/005-add-more-candidate/README.md` and `quickstart.md` - COMPLETED

## Parallel Execution Examples
- T002, T003, T004, T010, T011, T012, T013 can be run in parallel ([P])
- T005 depends on T003, T004
- T007, T008, T009 can be run in parallel after backend endpoint (T005) is ready

## Dependency Notes
- T001 must be done before T002
- T003, T004 before T005
- T005 before T007-T009
- T010 after T005, T007

---
*All tasks are actionable and dependency-ordered for immediate execution.*