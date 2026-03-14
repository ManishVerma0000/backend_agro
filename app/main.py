from dotenv import load_dotenv
# Load all environment variables from the .env file FIRST
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.main import api_router
from app.core.config import settings
from app.db.session import connect_to_mongo, close_mongo_connection

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health-check")
def health_check():
    return {"status": "ok"}
