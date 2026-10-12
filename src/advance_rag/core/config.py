"""Application settings, loaded from environment variables (prefix `RAG_`) and `.env`.

Real environment variables always win over `.env`, so Codespaces/CI/Cloud Run can override
anything without editing files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

type Environment = Literal["dev", "test", "staging", "prod"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RAG_",
        extra="ignore",
    )

    # --- app
    env: Environment = "dev"
    app_name: str = "advance-rag"
    log_level: str = "INFO"
    log_json: bool = True

    # --- infrastructure
    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None

    # --- object storage
    storage_backend: Literal["local", "gcs"] = "local"
    storage_local_root: str = "./data/storage"
    gcs_bucket: str | None = None

    # --- AI providers (accepts the Google-standard GEMINI_API_KEY too)
    gemini_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("RAG_GEMINI_API_KEY", "GEMINI_API_KEY"),
    )

    # --- operational
    health_check_timeout_s: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
