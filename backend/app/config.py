from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PORT: int = 8000
    SECRET_KEY: str = "change_this_secret_to_something_very_secure_and_long_1234567890"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/nutriguide"
    AI_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "gemini"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
