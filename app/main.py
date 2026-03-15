from dotenv import load_dotenv
# Load all environment variables from the .env file FIRST
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.main import api_router
from app.core.config import settings
from app.db.session import connect_to_mongo, close_mongo_connection
from fastapi.middleware.cors import CORSMiddleware

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

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://agro-hub-dun.vercel.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health-check")
def health_check():
    return {"status": "ok"}
