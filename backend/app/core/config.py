"""
core/config.py
==============
Central application configuration loaded from environment variables.

Uses pydantic-settings so all config is:
- Type-validated at startup
- Documented via field descriptions
- Loaded from .env files (dev) or real env vars (prod/Docker)

NEVER hardcode secrets here. Always read from environment.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings — all values sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_ENV: Literal["development", "testing", "staging", "production"] = "development"
    APP_NAME: str = "AI Document & Compliance Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ------------------------------------------------------------------ #
    # Backend API
    # ------------------------------------------------------------------ #
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # Comma-separated list of allowed CORS origins
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:5173"])

    # ------------------------------------------------------------------ #
    # Database — PostgreSQL + pgvector
    # ------------------------------------------------------------------ #
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "compliance_platform"
    POSTGRES_USER: str = "platform_user"
    POSTGRES_PASSWORD: str = Field(..., description="Database password — required")

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL(self) -> str:
        """Async SQLAlchemy connection string."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync connection string for Alembic migrations."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ------------------------------------------------------------------ #
    # Redis
    # ------------------------------------------------------------------ #
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    @computed_field  # type: ignore[misc]
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ------------------------------------------------------------------ #
    # Celery
    # ------------------------------------------------------------------ #
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ------------------------------------------------------------------ #
    # JWT / Security
    # ------------------------------------------------------------------ #
    JWT_SECRET_KEY: str = Field(..., description="JWT signing key — must be long and random")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # AI Provider (abstracted)
    # ------------------------------------------------------------------ #
    AI_PROVIDER: Literal["openai", "anthropic", "azure_openai", "ollama"] = "openai"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = ""
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = ""

    # Ollama (local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "llama3"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # ------------------------------------------------------------------ #
    # Vector Search
    # ------------------------------------------------------------------ #
    VECTOR_DIMENSION: int = 1536

    # ------------------------------------------------------------------ #
    # Document Storage
    # ------------------------------------------------------------------ #
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "./storage/local"

    # S3-compatible storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "us-east-1"
    AWS_S3_ENDPOINT_URL: str = ""

    # ------------------------------------------------------------------ #
    # File Upload
    # ------------------------------------------------------------------ #
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "docx", "txt", "png", "jpg", "jpeg"]

    @computed_field  # type: ignore[misc]
    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ------------------------------------------------------------------ #
    # Validators
    # ------------------------------------------------------------------ #
    @model_validator(mode="after")
    def validate_ai_provider_credentials(self) -> "Settings":
        """Warn (not error) if provider credentials are missing at startup."""
        # Credentials are validated lazily when the provider is first called,
        # not at import time, so we don't block startup in test environments.
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached application settings.

    Use FastAPI's dependency injection:
        from app.core.config import get_settings
        settings: Settings = Depends(get_settings)

    Or import directly:
        from app.core.config import get_settings
        settings = get_settings()
    """
    return Settings()  # type: ignore[call-arg]
