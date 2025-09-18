# Quickstart: Modular Python Backend

## Prerequisites
- Python 3.11+
- MongoDB instance (local or cloud)
- Install dependencies: FastAPI, Motor, Pydantic, python-dotenv

## Project Structure
backend/
├── src/
│   ├── api/         # API route definitions
│   ├── models/      # Pydantic models
│   ├── services/    # Business logic and DB access
│   └── utils/       # Shared utilities
└── tests/           # Unit and integration tests

## Setup
1. Clone the repository and checkout the feature branch:
   ```bash
   git clone <repo-url>
   cd TalentSync
   git checkout 001-update-an-backend
   ```
2. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` (see `.env.example`).
4. Start MongoDB (if not running):
   ```bash
   docker-compose up -d
   ```
5. Run the FastAPI server:
   ```bash
   uvicorn src.api.main:app --reload
   ```
6. Access API docs at `http://localhost:8001/docs`

## Adding a New Module
- Add new models to `src/models/`
- Add new business logic to `src/services/`
- Add new API routes to `src/api/`
- Place shared code in `src/utils/`

## Running Tests
- Place tests in `tests/`
- Run with:
   ```bash
   pytest
   ```

---

For more details, see the documentation in each module.
