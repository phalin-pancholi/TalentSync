# Tasks: Cleaner Candidate Card UI

**Input**: Design documents from `/specs/007-candidate-card-should/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
2. Load optional design documents: data-model.md, contracts/, research.md, quickstart.md
3. Generate tasks by category: setup, tests, core, integration, polish
4. Apply task rules: [P] for parallel, tests before implementation
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness
9. Return: SUCCESS (tasks ready for execution)
```

## Phase 3.1: Setup
- [x] T001 Ensure project structure matches plan (frontend/src/components, backend/src/models, etc.)
- [x] T002 Initialize/verify React and Tailwind CSS in frontend (package.json, tailwind.config.js)
- [x] T003 [P] Configure linting and formatting tools in frontend (eslint, prettier)

## Phase 3.2: Tests First (TDD)
- [x] T004 [P] Add contract test for CandidateCard minimal details in `specs/007-candidate-card-should/contracts/candidate-card.test.js`
- [x] T005 [P] Add quickstart integration test scenarios in `specs/007-candidate-card-should/contracts/quickstart.test.md`

## Phase 3.3: Core Implementation
- [x] T006 [P] Implement Candidate model in `frontend/src/lib/models/candidate.js` (id, name, skills, experience, otherDetails)
- [x] T007 [P] Implement CandidateCard component in `frontend/src/components/CandidateCard.js` (minimal details, modal popup for all details)
- [x] T008 Implement logic for handling missing/long data in `frontend/src/components/CandidateCard.js`
- [x] T009 Implement accessibility for "Show all details" button in `frontend/src/components/CandidateCard.js`

## Phase 3.4: Integration
- [x] T010 Integrate CandidateCard into candidate list view in `frontend/src/components/CandidateList.js`
- [x] T011 Ensure data flows from backend or mock data to CandidateCard in `frontend/src/components/CandidateList.js`

## Phase 3.5: Polish
- [x] T012 [P] Add unit tests for CandidateCard in `frontend/src/__tests__/CandidateCard.test.js`
- [ ] T013 [P] Add documentation for usage and props in `frontend/components/README.md`
- [ ] T014 [P] Run performance and accessibility checks on CandidateCard UI
- [ ] T015 [P] Manual validation using quickstart.md scenarios

## Dependencies
- T004, T005 before T006-T009
- T006 before T007
- T007 before T008, T009
- T007 before T010
- T010 before T011
- Implementation before polish (T012-T015)

## Parallel Example
```
# Launch T004 and T005 together:
Task: "Add contract test for CandidateCard minimal details in specs/007-candidate-card-should/contracts/candidate-card.test.js"
Task: "Add quickstart integration test scenarios in specs/007-candidate-card-should/contracts/quickstart.test.md"

# Launch T012-T015 together after implementation:
Task: "Add unit tests for CandidateCard in frontend/src/__tests__/CandidateCard.test.js"
Task: "Add documentation for usage and props in frontend/components/README.md"
Task: "Run performance and accessibility checks on CandidateCard UI"
Task: "Manual validation using quickstart.md scenarios"
```

## Validation Checklist
- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
