from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Production Ready"
    API_V1_STR: str = "/api/v1"
    # MongoDB configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fastapi_db"
    
    # JWT configuration
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE_CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION_NAME: str = "us-east-1"
    AWS_BUCKET_NAME: str = ""

settings = Settings()
