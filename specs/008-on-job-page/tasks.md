# Tasks: Show Candidate Location and Experience on Job Match Card

**Input**: Design documents from `/specs/008-on-job-page/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Load optional design documents: data-model.md, contracts/, research.md
3. Generate tasks by category: Setup, Tests, Core, Integration, Polish
4. Apply task rules: [P] for parallel, TDD order
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
9. Return: SUCCESS (tasks ready for execution)
```

## Phase 3.1: Setup
- [x] T001 Ensure backend and frontend projects are up to date (no new dependencies)
- [x] T002 [P] Review and backup existing candidate model, API, and frontend card code

## Phase 3.2: Tests First (TDD)
- [x] T003 [P] Add contract test for candidate location and experience fields in `specs/008-on-job-page/contracts/test_candidate_fields.py`
- [x] T004 [P] Add integration test for candidate card display (location/experience) in `frontend/src/__tests__/candidateCard.integration.test.js`

## Phase 3.3: Core Implementation
- [x] T005 [P] Update backend candidate model to add `location` (string) and `experience` (float/string) fields in `backend/src/models/candidate.py`
- [x] T006 [P] Update backend candidate API to support new fields in `backend/src/api/candidates.py`
- [x] T007 [P] Update backend candidate service logic to handle new fields in `backend/src/services/candidate_service.py`
- [x] T008 [P] Update LLM extraction prompt/template to extract and populate location and experience in `backend/src/services/llm_extraction_service.py`
- [x] T009 [P] Update frontend candidate card UI to display location and experience in `frontend/src/components/CandidateCard.js`
- [x] T010 [P] Update frontend job matching view to ensure new fields are shown in `frontend/src/components/JobMatchView.js`

## Phase 3.4: Integration
- [x] T011 [P] Test end-to-end: create/update candidate with location/experience, verify display on job page
- [x] T012 [P] Handle missing/invalid data: show "Not provided" if fields are missing in backend and frontend

## Phase 3.5: Polish
- [x] T013 [P] Add/Update unit tests for backend model, service, and API (e.g., `backend/src/tests/unit/`)
- [x] T014 [P] Add/Update unit tests for frontend components (e.g., `frontend/src/__tests__/`)
- [x] T015 [P] Update documentation and quickstart in `specs/008-on-job-page/quickstart.md`

## Parallel Execution Guidance
- Tasks marked [P] can be executed in parallel (different files, no dependencies)
- Example: T003, T004, T005, T006, T007, T008, T009, T010 can be run in parallel after setup

## Dependency Notes
- T001, T002 must be completed before any other tasks
- Tests (T003, T004) must be written and fail before implementation (TDD)
- Model (T005) before service (T007) and API (T006)
- Backend must be ready before frontend (T009, T010)
- Integration and polish tasks depend on core implementation
