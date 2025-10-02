# backend/core/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    JWT_EXPIRATION_MINUTES: str
    REDIS_URL: str

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "no-reply@example.com"
    MAIL_PORT: int = 25
    MAIL_SERVER: str = "smtp4dev"
    MAIL_FROM_NAME: str = "Admin"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False

    CELERY_BROKER_URL: str = "redis://redis:6379/3"
    CELERY_BACKEND_URL: str = "redis://redis:6379/3"

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("ENV") == "test" else ".env"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
