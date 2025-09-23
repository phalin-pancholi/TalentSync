# Quickstart: Cleaner Candidate Card UI

## Prerequisites
- Frontend: Node.js, npm, React, Tailwind CSS
- Backend: Python, FastAPI (if API changes needed)

## Steps
1. Checkout branch `007-candidate-card-should`
2. Install frontend dependencies: `cd frontend && npm install`
3. Start frontend: `npm start`
4. View candidate cards: Only minimal details (name, skills, experience) should be visible by default
5. Click "Show all details" on a card to expand and view all candidate information
6. Test edge cases: missing data, long lists, no candidates
7. Run frontend tests: `npm test`

## Validation
- All acceptance scenarios from the spec are met
- UI is clean, minimal, and accessible
- "Show all details" button works for each card
- No errors for missing or long data
