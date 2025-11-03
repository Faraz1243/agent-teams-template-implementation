# config/config.py
import secrets
from typing import Literal
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from .environments.development import DevelopmentConfig
from .environments.production import ProductionConfig
from pathlib import Path
from .logging import logger
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    # Core Settings (Required)
    PROJECT_NAME: str = "rawaa-backend"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # API Settings (Optional with defaults)
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Database configurations (Required) 

    # PostgreSQL
    POSTGRES_DB: str = "rawaa_data"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_INSTANCE_CONNECTION_NAME: str = "rawaa-442816:us-central1:rawaa-prod"
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432" 

    # LLM API
    GROQ_API_KEY: str 
    
    @property
    def is_appengine(self) -> bool:
        return self.GAE_ENV is not None

    # # SSO configurations (Optional)
    # GOOGLE_CLIENT_ID: str | None = None
    # GOOGLE_CLIENT_SECRET: str | None = None
    # SSO_CALLBACK_HOSTNAME: str | None = None
    # SSO_LOGIN_CALLBACK_URL: str | None = None
    
    # # Email Settings (Optional with defaults)
    # MAIL_USERNAME: str | None = None  # Make it optional
    # MAIL_PASSWORD: str | None = None  # Make it optional
    # MAIL_FROM: str = "admin@rawaa.com"
    # MAIL_PORT: int = 587 | 587
    # MAIL_SERVER: str = "smtp.gmail.com"
    # FRONTEND_URL: str = "http://localhost:3000"
    # SUPPORT_EMAIL: str = "support@rawaa.com"

    @property
    def env_config(self):
        
        logger.info(f"Postgres password: {os.getenv('POSTGRES_PASSWORD', 'no value')}")
        if self.ENVIRONMENT == "production":
            return ProductionConfig()
        return DevelopmentConfig()

settings = Settings()
 