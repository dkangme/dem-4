from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    FIRESTORE_PROJECT_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    BASE_URL: str
    SHORT_CODE_LENGTH: int = 8
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
