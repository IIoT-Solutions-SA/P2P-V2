from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator, Field
import secrets
import os

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "P2P Sandbox API"
    API_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "P2P Sandbox for SMEs"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", secrets.token_urlsafe(32)))

    # CORS - Allow multiple common localhost variations for Docker compatibility
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173", "http://127.0.0.1:5173", "http://0.0.0.0:5173"])
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database URLs
    DATABASE_URL: str = "postgresql+asyncpg://p2p_user:iiot123@localhost:5432/p2p_sandbox"
    MONGODB_URL: str = "mongodb://p2p_user:iiot123@localhost:27017/"

    # SuperTokens Configuration
    SUPERTOKENS_CONNECTION_URI: str = "http://localhost:3567"
    API_DOMAIN: str = "http://localhost:8000"
    WEBSITE_DOMAIN: str = "http://localhost:5173"
    COOKIE_DOMAIN: Optional[str] = None  # None = same domain as API
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # OCI Object Storage (S3-compatible) Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None  # OCI Customer Secret Key Access Key
    AWS_SECRET_ACCESS_KEY: Optional[str] = None  # OCI Customer Secret Key Secret
    AWS_REGION: str = "me-riyadh-1"
    S3_ENDPOINT_URL: str = "https://axps0kpwrxvp.compat.objectstorage.me-riyadh-1.oraclecloud.com"
    OCI_NAMESPACE: str = "axps0kpwrxvp"

    # S3 Bucket Names (OCI Object Storage)
    S3_PROFILE_PICTURES_BUCKET: str = "p2p-profile-images"
    S3_FORUM_MEDIA_BUCKET: str = "p2p-forum-media"
    S3_USECASE_MEDIA_BUCKET: str = "p2p-usecase-media"

    # CloudFront CDN (not used with OCI - kept for compatibility)
    CLOUDFRONT_DOMAIN: Optional[str] = None

    # Email Configuration (single source of truth for all email services)
    MAIL_USERNAME: str = "uxmr28@gmail.com"#"coding@iiotsolutions.sa"
    MAIL_PASSWORD: str = ""  # Gmail App Password - set in .env
    MAIL_FROM: str = "P2P <uxmr28@gmail.com>"#"P2P <coding@iiotsolutions.sa>"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # Production URL base (used in email links - verification, password reset, invitations)
    PRODUCTION_URL: str = "http://localhost:5173"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()