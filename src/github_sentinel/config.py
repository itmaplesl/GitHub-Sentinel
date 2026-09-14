from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SENTINEL_",
        extra="ignore",
    )

    app_name: str = "GitHub Sentinel"
    environment: str = "development"
    log_level: str = "INFO"
    api_key: str | None = None
    database_url: str = "sqlite:///./github_sentinel.db"
    redis_url: str = "redis://localhost:6379/0"
    github_token: str | None = None
    ai_api_key: str | None = None
    ai_base_url: str | None = None
    ai_model: str | None = None
    request_timeout_seconds: float = Field(default=20.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
