from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supertokens_id = Column(String(255), unique=True, nullable=True, index=True)  # Link to SuperTokens user
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_picture_url = Column(String(500), nullable=True)  # S3 URL for profile picture

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    media_files = relationship("UserMedia", back_populates="user", cascade="all, delete-orphan")

class UserSession(Base, TimestampMixin):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class UserMedia(Base, TimestampMixin):
    __tablename__ = "user_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_type = Column(String(50), nullable=False)  # profile_picture, forum_attachment, usecase_media
    original_filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)
    s3_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=False)
    context_id = Column(String(255), nullable=True)  # post_id, usecase_id, etc.

    # Relationships
    user = relationship("User", back_populates="media_files")

class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)


class LoginAttempt(Base):
    """Shared failed-login counter keyed by a non-plaintext account identifier."""
    __tablename__ = "login_attempts"

    identity_key = Column(String(64), primary_key=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True, index=True)
    last_failed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OtpCode(Base):
    """
    Stores hashed 6-digit OTP codes for:
    - signup_verify: email verification after admin signup
    - login_mfa: MFA challenge on first login from a new device
    """
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    purpose = Column(String(50), nullable=False)  # 'signup_verify' | 'login_mfa'
    code_hash = Column(String(64), nullable=False)  # SHA-256 hex digest
    challenge_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True)
    attempts = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TrustedDevice(Base):
    """
    Tracks devices/browsers that have completed MFA.
    A long-lived HttpOnly cookie ('trusted_device') stores the device_token.
    If the token is present and unexpired, login skips the OTP step.
    """
    __tablename__ = "trusted_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String(255), nullable=False, index=True)
    device_token = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)