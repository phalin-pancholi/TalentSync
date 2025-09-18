# Tasks: Modular Python Backend Architecture

**Input**: Design documents from `/specs/001-update-an-backend/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Load optional design documents: data-model.md, contracts/, research.md
3. Generate tasks by category: setup, tests, core, integration, polish
4. Apply task rules: [P] for parallel, TDD order, models before services, services before endpoints
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
9. Return: SUCCESS (tasks ready for execution)
```

## Phase 3.1: Setup
- [x] T001 Create backend/src/ folder structure: api/, models/, services/, utils/, tests/
- [x] T002 Initialize Python project with FastAPI, Pydantic, Motor, python-dotenv in backend/requirements.txt
- [x] T003 [P] Configure linting and formatting tools (e.g., flake8, black) in backend/
- [x] T004 [P] Set up .env and configuration management in backend/

## Phase 3.2: Tests First (TDD)
- [x] T005 [P] Add contract tests for all job endpoints in backend/tests/contract/test_jobs.py (see contracts/test_jobs.py)
- [x] T006 [P] Add integration test for job-candidate matching in backend/tests/integration/test_matching.py
- [x] T007 [P] Add integration test for file upload and job creation in backend/tests/integration/test_upload.py

## Phase 3.3: Core Implementation
- [x] T008 [P] Implement JobPosting model in backend/src/models/job_posting.py
- [x] T009 [P] Implement Candidate model in backend/src/models/candidate.py
- [x] T010 Implement database service for MongoDB in backend/src/services/db_service.py
- [x] T011 Implement job service logic in backend/src/services/job_service.py
- [x] T012 Implement candidate matching logic in backend/src/services/matching_service.py
- [x] T013 Implement API routes for jobs in backend/src/api/jobs.py
- [x] T014 Implement API route for file upload in backend/src/api/upload.py
- [x] T015 Implement API route for candidate matching in backend/src/api/matching.py
- [x] T016 [P] Implement shared utilities in backend/src/utils/

## Phase 3.4: Integration
- [x] T017 Integrate logging and error handling in backend/src/utils/logging.py
- [x] T018 Integrate CORS and middleware in backend/src/api/main.py
- [x] T019 Integrate environment and config loading in backend/src/utils/config.py

## Phase 3.5: Polish
- [x] T020 [P] Add unit tests for all models in backend/tests/unit/test_models.py
- [x] T021 [P] Add unit tests for all services in backend/tests/unit/test_services.py
- [x] T022 [P] Add API documentation using FastAPI docs in backend/src/api/main.py
- [x] T023 [P] Add developer onboarding docs in backend/README.md

## Parallel Execution Examples
- T003, T004, T005, T006, T007, T008, T009, T016, T020, T021, T022, T023 can be run in parallel ([P])
- T010, T011, T012, T013, T014, T015, T017, T018, T019 are sequential due to dependencies

## Dependency Notes
- Setup (T001-T004) must be completed before tests and implementation
- Contract and integration tests (T005-T007) must be written before core implementation (T008+)
- Models (T008, T009) before services (T010-T012)
- Services before API routes (T013-T015)
- Utilities (T016) can be developed in parallel
- Integration and polish tasks follow core implementation

---

All tasks are actionable and dependency-ordered for modularizing the backend Python API service.
