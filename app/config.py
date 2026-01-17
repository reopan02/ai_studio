from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"

    LLM_API_BASE_URL: str = "https://api.gpt-best.com"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "openai/gpt-4o-mini"

    IMAGE_GEN_API_BASE_URL: str = ""
    IMAGE_GEN_API_KEY: str = ""

    IMAGE_EDIT_API_BASE_URL: str = ""
    IMAGE_EDIT_API_KEY: str = ""

    VIDEO_GEN_API_BASE_URL: str = ""
    VIDEO_GEN_API_KEY: str = ""

    UPLOAD_URL: Optional[str] = None
    UPLOAD_APIKEY: Optional[str] = None

    SUPABASE_URL: str = "http://localhost:8000"
    SUPABASE_JWT_SECRET: Optional[str] = None

    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    JWT_SESSION_EXPIRE_DAYS: int = 7

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    STATIC_CACHE_CONTROL: Optional[str] = None

    STORAGE_MASTER_KEY: Optional[str] = None
    DEFAULT_STORAGE_QUOTA_BYTES: int = 1_073_741_824  # 1 GiB

    BACKUP_ENABLED: bool = False
    BACKUP_DIR: str = "backups"
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 7

    REQUEST_LOG_MAX_BODY_BYTES: int = 50_000

    POLLING_INTERVAL: int = 5
    POLLING_MAX_ATTEMPTS: int = 360

    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0

    MAX_CONCURRENT_TASKS: int = 10

    REQUEST_TIMEOUT: int = 60

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
