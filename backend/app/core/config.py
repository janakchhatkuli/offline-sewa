"""Application configuration loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    APP_NAME: str = "offline-sewa"
    SECRET_KEY: str = "change_me"
    LOG_LEVEL: str = "DEBUG"

    DATABASE_URL: str = "postgresql+asyncpg://sewa:sewa@localhost:5432/offline_sewa"
    DATABASE_URL_SYNC: str = "postgresql://sewa:sewa@localhost:5432/offline_sewa"

    SMS_PROVIDER: str = "sparrow"
    SPARROW_API_KEY: str = ""
    SPARROW_SENDER_ID: str = "Demo"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
