# Tasks: LLM-based Job Upload Endpoint

**Input**: Design documents from `/specs/002-add-llm-based/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Load optional design documents: data-model.md, contracts/, research.md
3. Generate tasks by category: setup, tests, core, integration, polish
4. Apply task rules: [P] for parallel, sequential for same file
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
9. Return: SUCCESS (tasks ready for execution)
```

---

## Task List

### Setup
- **T001** [P] ✅ COMPLETED - Ensure Python 3.11, FastAPI, Langchain, Gemini, PyPDF2, and MongoDB are installed and configured (`requirements.txt`, backend Dockerfile)
- **T002** [P] ✅ COMPLETED - Set up test data files: `tests/data/sample_job.pdf`, `tests/data/sample_job.txt`, `tests/data/sample_job_missing_fields.txt`, `tests/data/unsupported_file.jpg`

### Contract & Integration Tests (TDD)
- **T003** [P] ✅ COMPLETED - Implement contract tests for `/api/jobs/upload_llm` endpoint (`specs/002-add-llm-based/contracts/test_jobs.py`)
- **T004** [P] ✅ COMPLETED - Implement integration test for end-to-end upload, extraction, and DB entry (`backend/src/tests/integration/test_upload_llm.py`)

### Core Models & Services
- **T005** [P] ✅ COMPLETED - Implement `JobPostingBase` and related models in `backend/src/models/job_posting.py` (ensure all fields are Optional)
- **T006** [P] ✅ COMPLETED - Implement LLM extraction service using Langchain + Gemini (`backend/src/services/llm_extraction_service.py`)
- **T007** [P] ✅ COMPLETED - Implement PDF/text parsing utility (`backend/src/services/file_parsing_service.py`)
- **T008** ✅ COMPLETED - Implement job creation logic in DB using extracted structure (`backend/src/services/job_service.py`)

### API Endpoint
- **T009** ✅ COMPLETED - Implement `/api/jobs/upload_llm` endpoint in FastAPI (`backend/src/api/jobs.py`)
- **T010** ✅ COMPLETED - Integrate file upload, parsing, LLM extraction, and DB entry in endpoint logic
- **T011** ✅ COMPLETED - Add error handling for unsupported file types and LLM service unavailability
- **T012** ✅ COMPLETED - Add logging for upload, extraction, and error events

### Polish & Documentation
- **T013** [P] ✅ COMPLETED - Add/Update OpenAPI schema for new endpoint (`specs/002-add-llm-based/contracts/openapi.yaml`)
- **T014** [P] ✅ COMPLETED - Update quickstart.md with usage and troubleshooting steps
- **T015** [P] ✅ COMPLETED - Add/Update README with new feature instructions
- **T016** [P] ✅ COMPLETED - Add unit tests for LLM extraction and parsing services (`backend/src/tests/unit/test_llm_extraction.py`, `test_file_parsing.py`)

---

## Parallel Execution Guidance
- Tasks marked [P] can be executed in parallel (different files, no dependencies)
- Example: T001, T002, T003, T004, T005, T006, T007, T013, T014, T015, T016 can all be started in parallel
- T008 depends on T005, T006, T007
- T009 depends on T008
- T010 depends on T009
- T011, T012 depend on T010

---

## Dependency Graph
- Setup → Tests → Models/Services → Endpoint → Integration → Polish
- T001, T002 → T003, T004 → T005, T006, T007 → T008 → T009 → T010 → T011, T012
- Polish tasks (T013-T016) can be done in parallel after core logic is in place

---

## Task Agent Commands Example
- To run all parallel tasks: `task-agent run T001 T002 T003 T004 T005 T006 T007 T013 T014 T015 T016`
- To run sequentially: `task-agent run T008 T009 T010 T011 T012`

---

# End of tasks.md
