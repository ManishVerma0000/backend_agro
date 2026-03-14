# FastAPI Production Ready

This project provides an optimal production-ready starting structure for a FastAPI project.

## Structure Overview
- `app/api/`: All web-related elements like endpoints and dependencies.
- `app/core/`: Configuration, security hashing logic, app configurations.
- `app/crud/`: Functions that directly interact with the database.
- `app/db/`: Database configuration and sessions.
- `app/models/`: Database models, typically SQLAlchemy models.
- `app/schemas/`: Pydantic models for data validation and schemas.
- `app/services/`: Complex business logic layer.
- `tests/`: Project unit & integration tests.

## Quick Start
1. Install dependencies: `pip install -r requirements.txt` 
2. Create `.env` from `.env.example`
3. Start the server: `uvicorn app.main:app --reload`
