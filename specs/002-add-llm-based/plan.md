

# Implementation Plan: LLM-based Job Upload Endpoint

**Branch**: `002-add-llm-based` | **Date**: September 19, 2025 | **Spec**: [/home/adarsh/hackathon/TalentSync/specs/002-add-llm-based/spec.md]
**Input**: Feature specification from `/specs/002-add-llm-based/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)


## Summary
This feature enables users to upload job description documents (PDF or text) via the frontend. The backend will use Langchain (as the LLM framework) and Gemini (as the LLM model) to extract job information from the document, populate a `JobPostingBase` structure, and create a job entry in the database. Missing fields will be set to `None` and will not block job creation. The process must be robust to incomplete or ambiguous documents and provide clear feedback to users.


## Technical Context
**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Langchain, Gemini, Pydantic, PyPDF2 (for PDF parsing), MongoDB (existing)  
**Storage**: MongoDB  
**Testing**: pytest  
**Target Platform**: Linux server  
**Project Type**: web (frontend + backend)  
**Performance Goals**: NEEDS CLARIFICATION (e.g., expected throughput, latency)  
**Constraints**: Allow missing fields as None, robust to incomplete documents, handle LLM/model errors gracefully  
**Scale/Scope**: NEEDS CLARIFICATION (e.g., expected number of uploads/users)


## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Test-First: All endpoints and extraction logic must be covered by contract and integration tests before implementation.
- Library-First: Extraction logic should be modular and independently testable.
- CLI Interface: Not directly applicable, but endpoints should have clear input/output schemas.
- Integration Testing: End-to-end tests for upload, extraction, and DB entry required.
- Observability: Log all upload, extraction, and error events.
- Simplicity: Use existing frameworks and keep the flow as simple as possible.


## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (web application: backend + frontend)

## Phase 0: Outline & Research
1. **Unknowns/Clarifications**
   - What is the expected behavior for unsupported file types? (FR-007)
   - What should happen if the LLM service is unavailable? (Edge case)
   - What level of feedback is required to the user? (FR-008)
   - Performance and scale expectations?
2. **Research Tasks**
   - Research best practices for using Langchain with Gemini for document extraction.
   - Research robust PDF/text parsing for job descriptions.
   - Research error handling and user feedback patterns for LLM-based extraction services.
   - Research best practices for mapping LLM output to Pydantic models with optional fields.
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Entities**
   - Job Description Document: file type, content, upload timestamp, uploader
   - JobPostingBase: title, description, skills, experience_level, department, location (all fields may be None)
   - Job Entry: DB record based on JobPostingBase
2. **API Contracts**
   - Endpoint: POST `/api/jobs/upload_llm` (accepts file upload, returns job entry or error)
   - OpenAPI schema for request/response
   - Contract tests for upload, extraction, and DB entry
3. **Contract Tests**
   - Test valid PDF upload → job entry created
   - Test valid text upload → job entry created
   - Test upload with missing fields → job entry with None fields
   - Test unsupported file type → error/feedback
   - Test LLM service unavailable → error/feedback
4. **Integration Tests**
   - End-to-end: upload → extraction → DB
5. **Quickstart**
   - Steps to run backend, upload a document, and verify DB entry
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
