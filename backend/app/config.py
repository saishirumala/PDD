from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    PORT: int = 8000
    SECRET_KEY: str = "change_this_secret_to_something_very_secure_and_long_1234567890"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./nutriguide.db"
    AI_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "gemini"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    # Supabase Configuration
    SUPABASE_URL: Optional[str] = "https://nnwovklgbgmdoemymkyy.supabase.co"
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = "sb_publishable_kJDTDsyMSbqvd1-uqAo8cQ_3n-qFzcs"
    SUPABASE_SECRET_KEY: Optional[str] = None
    SUPABASE_JWKS_URL: Optional[str] = None
    SUPABASE_DB_URL: Optional[str] = None

    @property
    def effective_db_url(self) -> str:
        """Returns SUPABASE_DB_URL if provided, else DATABASE_URL."""
        url = self.SUPABASE_DB_URL.strip() if (self.SUPABASE_DB_URL and self.SUPABASE_DB_URL.strip()) else self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
            ".env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
