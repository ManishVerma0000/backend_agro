import os

STRUCTURE = {
    "app": {
        "__init__.py": "",
        "main.py": "from fastapi import FastAPI\nfrom app.api.main import api_router\nfrom app.core.config import settings\n\napp = FastAPI(\n    title=settings.PROJECT_NAME,\n    openapi_url=f\"{settings.API_V1_STR}/openapi.json\"\n)\n\napp.include_router(api_router, prefix=settings.API_V1_STR)\n\n@app.get(\"/health-check\")\ndef health_check():\n    return {\"status\": \"ok\"}\n",
        "core": {
            "__init__.py": "",
            "config.py": "from pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    PROJECT_NAME: str = \"FastAPI Production Ready\"\n    API_V1_STR: str = \"/api/v1\"\n    # Add more configurations like Database URL here\n\nsettings = Settings()\n",
            "security.py": "# Password hashing and JWT token functions go here\n",
            "exceptions.py": "# Custom application exceptions go here\n"
        },
        "api": {
            "__init__.py": "",
            "main.py": "from fastapi import APIRouter\nfrom app.api.routes import users\n\napi_router = APIRouter()\napi_router.include_router(users.router, prefix=\"/users\", tags=[\"users\"])\n",
            "deps.py": "# Shared dependencies like get_db, get_current_user\n",
            "routes": {
                "__init__.py": "",
                "users.py": "from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/\")\ndef read_users():\n    return [{\"username\": \"john\"}]\n"
            }
        },
        "models": {
            "__init__.py": "",
            "user.py": "# Database models (e.g., SQLAlchemy or SQLModel) representing tables\n"
        },
        "schemas": {
            "__init__.py": "",
            "user.py": "# Pydantic schemas (e.g., UserCreate, UserRead, etc.) for data validation & serialization\n"
        },
        "crud": {
            "__init__.py": "",
            "base.py": "# Base generic CRUD operations class\n",
            "user.py": "# User specific CRUD operations extending the Base class\n"
        },
        "services": {
            "__init__.py": "",
            "user_service.py": "# Complex business logic separated from the endpoint\n"
        },
        "db": {
            "__init__.py": "",
            "session.py": "# Database connection setup and sessionmaker\n",
            "init_db.py": "# Initial database seed data function\n"
        }
    },
    "tests": {
        "__init__.py": "",
        "conftest.py": "# Pytest fixtures, test database setup, and test client\n",
        "api": {
            "__init__.py": "",
            "test_users.py": "# Tests for user endpoints\n"
        },
        "crud": {
            "__init__.py": ""
        }
    },
    "scripts": {
        "__init__.py": "",
        "prestart.sh": "#!/bin/bash\n# Run required pre-start actions like running migrations\nalembic upgrade head\n"
    },
    ".env.example": "PROJECT_NAME=\"FastAPI Application\"\nAPI_V1_STR=\"/api/v1\"\nDATABASE_URL=\"postgresql://user:pass@localhost/dbname\"\n",
    "requirements.txt": "fastapi\nuvicorn[standard]\npydantic-settings\nsqlalchemy\nalembic\npytest\nhttpx\n",
    "alembic.ini": "# Alembic Configuration\n",
    ".gitignore": "__pycache__/\n*.py[cod]\n*$py.class\n.env\n.venv\nvenv/\nENV/\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n",
    "README.md": "# FastAPI Production Ready\n\nThis project provides an optimal production-ready starting structure for a FastAPI project.\n\n## Structure Overview\n- `app/api/`: All web-related elements like endpoints and dependencies.\n- `app/core/`: Configuration, security hashing logic, app configurations.\n- `app/crud/`: Functions that directly interact with the database.\n- `app/db/`: Database configuration and sessions.\n- `app/models/`: Database models, typically SQLAlchemy models.\n- `app/schemas/`: Pydantic models for data validation and schemas.\n- `app/services/`: Complex business logic layer.\n- `tests/`: Project unit & integration tests.\n\n## Quick Start\n1. Install dependencies: `pip install -r requirements.txt` \n2. Create `.env` from `.env.example`\n3. Start the server: `uvicorn app.main:app --reload`\n"
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)

if __name__ == "__main__":
    create_structure(".", STRUCTURE)
    print("Project scaffolded successfully.")
