"""Configuration settings for the P2P Sandbox backend."""

from typing import List, Optional, Union, Annotated
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


def parse_cors(v: Union[str, List[str]]) -> List[str]:
    """Parse CORS origins from string or list."""
    if isinstance(v, str):
        if not v:
            return []
        if not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        try:
            import json
            return json.loads(v)
        except:
            return []
    elif isinstance(v, list):
        return v
    return []


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "P2P Sandbox"
    VERSION: str = "0.1.0"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: str = ""
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        return parse_cors(self.BACKEND_CORS_ORIGINS)
    
    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "p2p_user"
    POSTGRES_PASSWORD: str = "p2p_password"
    POSTGRES_DB: str = "p2p_sandbox"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.data.get('POSTGRES_USER')}:{values.data.get('POSTGRES_PASSWORD')}@{values.data.get('POSTGRES_SERVER')}:{values.data.get('POSTGRES_PORT')}/{values.data.get('POSTGRES_DB')}"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB_NAME: str = "p2p_sandbox"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # SuperTokens
    SUPERTOKENS_CONNECTION_URI: str = "http://supertokens:3567"
    SUPERTOKENS_API_KEY: str = "your-supertokens-api-key"
    SUPERTOKENS_APP_NAME: str = "P2P Sandbox"
    SUPERTOKENS_API_DOMAIN: str = "http://localhost:8000"
    SUPERTOKENS_WEBSITE_DOMAIN: str = "http://localhost:5173"
    
    # AWS S3 (for file storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env file
    )


settings = Settings()