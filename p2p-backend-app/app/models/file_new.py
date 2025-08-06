"""File storage models - new version to resolve conflicts."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, DateTime, Integer
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class FileMetadataNew(BaseModel, table=True):
    """Model for tracking uploaded files and their metadata."""
    __tablename__ = "file_metadata_v2"
    
    # File identification
    file_id: str = Field(
        unique=True,
        index=True,
        description="Unique file identifier used in storage path"
    )
    original_filename: str = Field(
        max_length=255,
        description="Original filename as uploaded by user"
    )
    
    # File metadata
    content_type: str = Field(
        max_length=128,
        description="MIME type of the file"
    )
    file_size: int = Field(
        description="File size in bytes"
    )
    content_hash: str = Field(
        max_length=64,
        description="SHA-256 hash of file content for integrity verification"
    )
    
    # Storage information
    storage_type: str = Field(
        max_length=32,
        default="local",
        description="Type of storage backend (local, s3, etc.)"
    )
    storage_path: str = Field(
        max_length=512,
        description="Path to file in storage backend"
    )
    
    # Organization and access
    category: str = Field(
        max_length=64,
        default="general",
        description="File category (profile_pictures, documents, etc.)"
    )
    user_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id",
        index=True,
        description="ID of user who uploaded the file"
    )
    organization_id: Optional[uuid.UUID] = Field(
        foreign_key="organizations.id", 
        index=True,
        description="Organization the file belongs to"
    )
    
    # Access control
    is_public: bool = Field(
        default=False,
        description="Whether file can be accessed without authentication"
    )
    is_active: bool = Field(
        default=True,
        description="Whether file is active (false means soft-deleted)"
    )
    
    # Additional metadata (JSON field for extensibility)
    extra_metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column("extra_metadata", String, nullable=True),
        description="Additional file metadata as JSON"
    )