from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Where Is My Proud API"
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "proud_db"
    
    # Allows loading from .env file if present
    class Config:
        env_file = ".env"

settings = Settings()
