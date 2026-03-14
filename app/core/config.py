from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Production Ready"
    API_V1_STR: str = "/api/v1"
    # Add more configurations like Database URL here

settings = Settings()
