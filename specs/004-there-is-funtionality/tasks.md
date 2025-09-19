# Tasks: Candidate Document LLM Extraction and Storage

**Input**: Design documents from `/specs/004-there-is-funtionality/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Load optional design documents: data-model.md, contracts/, research.md
3. Generate tasks by category: setup, core, integration, polish
4. Apply task rules: parallelize where possible, order by dependencies
5. Number tasks sequentially (T001, T002...)
6. Validate task completeness
7. Return: SUCCESS (tasks ready for execution)
```

## Phase 3.1: Setup
- [x] T001 Ensure backend and frontend project structure is present (backend/src/, frontend/src/)
- [x] T002 Ensure MongoDB is running and accessible
- [x] T003 [P] Verify LLM integration is available (reuse job page logic)

## Phase 3.2: Core Implementation
- [x] T004 [P] Create CandidateDocument model in backend/src/models/candidate.py
- [x] T005 [P] Create RawTextData model in backend/src/models/document.py
- [x] T006 [P] Update CandidateProfile model to allow optional fields in backend/src/models/candidate.py
- [x] T007 Implement document upload endpoint `/candidates/upload` in backend/src/api/candidates.py
- [x] T008 Implement logic to extract text from uploaded document in backend/src/services/document_service.py
- [x] T009 Send extracted text to LLM and parse response in backend/src/services/llm_extraction_service.py
- [x] T010 Store structured candidate profile and raw text in MongoDB in backend/src/services/candidate_service.py
- [x] T011 [P] Update frontend Candidate page UI to allow document upload and display extracted candidate profile in frontend/src/components/Candidates.js
- [x] T012 [P] Ensure frontend handles incomplete candidate profiles gracefully (fields may be missing) in frontend/src/components/Candidates.js

## Phase 3.3: Integration
- [x] T013 Integrate backend and frontend for candidate document upload and profile creation
- [x] T014 [P] Ensure error handling for unreadable/corrupt documents and LLM failures (notify user, allow manual entry)
- [x] T015 [P] Implement duplicate document detection or allow user override

## Phase 3.4: Polish
- [x] T016 [P] Update documentation to reflect new candidate upload flow in README.md and quickstart.md
- [x] T017 [P] Review and refactor code for consistency with job page logic

## Parallel Execution Guidance
- Tasks marked [P] can be executed in parallel (different files, no dependencies)
- Example: T004, T005, T006 can be done together; T011 and T012 can be done together after backend endpoints are ready

---

*All tasks completed successfully. The candidate document upload feature is now fully implemented with LLM extraction, error handling, and graceful fallbacks for missing data.*
