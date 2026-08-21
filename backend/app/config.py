import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application & Environment
    ENVIRONMENT: str = Field(default="dev", description="Environment: dev, stage, prod")
    DEBUG: bool = Field(default=True, description="Debug mode")
    PORT: int = Field(default=8000, description="FastAPI listening port")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cybershakti_user:dev_password@localhost:5432/cybershakti_db",
        description="Async PostgreSQL connection string"
    )
    
    # Redis & Celery
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1", description="Celery result backend URL")
    
    # Security & Auth
    JWT_SECRET_KEY: str = Field(
        default="dev_secret_key_change_in_production_0123456789abcdef0123456789abcdef",
        description="Secret key for signing JWT tokens"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")

    # Interim rate-limit and upload bounds (ADR-026 — env-overridable, not production-locked)
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_AUTH_PER_MINUTE: int = Field(default=10)
    MAX_UPLOAD_BYTES: int = Field(default=10 * 1024 * 1024)
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # External Services
    THREAT_INTEL_API_KEY: Optional[str] = Field(default=None, description="Threat Intelligence API key")
    LLM_API_KEY: Optional[str] = Field(default=None, description="LLM provider API key")
    
    # Storage
    S3_BUCKET_NAME: str = Field(default="cybershakti-storage-dev", description="S3 storage bucket name")
    S3_ENDPOINT_URL: Optional[str] = Field(default=None, description="S3 endpoint URL")
    S3_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="S3 access key ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="S3 secret access key")
    
    # SMTP / Email configuration (REM-05 & REM-06)
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host name")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_FROM_EMAIL: str = Field(default="no-reply@cybershakti.in", description="SMTP sender address")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()


def validate_runtime_security() -> None:
    """Refuse insecure stage/production configuration (CSHAKTI-CONST-001 §8.10, ADR-026)."""
    env = settings.ENVIRONMENT.lower()
    if env not in ("stage", "staging", "prod", "production"):
        return
    if settings.DEBUG:
        raise RuntimeError("DEBUG must be false outside development.")
    secret = settings.JWT_SECRET_KEY or ""
    if secret.startswith("dev_secret") or len(secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY is not suitable for stage/production.")
    if any(origin.strip() == "*" for origin in settings.cors_origins):
        raise RuntimeError("Wildcard CORS origins are not permitted in stage/production.")
    if "change_in_production" in settings.DATABASE_URL or "dev_password" in settings.DATABASE_URL:
        raise RuntimeError("Default database credentials are not permitted in stage/production.")
