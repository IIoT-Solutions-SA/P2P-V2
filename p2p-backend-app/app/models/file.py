"""File storage models for tracking uploaded files."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, String, DateTime, Integer
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class FileMetadata(BaseModel, table=True):
    """Model for tracking uploaded files and their metadata.
    
    This model stores information about all files uploaded to the system,
    including their storage location, user ownership, and metadata.
    """
    __tablename__ = "file_metadata_new"
    
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
    
    # Timestamps inherited from BaseModel:
    # id: uuid.UUID (primary key)
    # created_at: datetime
    # updated_at: datetime


class FileUploadRequest(SQLModel):
    """Request model for file upload operations."""
    category: str = Field(
        default="general",
        max_length=64,
        description="File category"
    )
    is_public: bool = Field(
        default=False,
        description="Whether file should be publicly accessible"
    )


class FileUploadResponse(SQLModel):
    """Response model for successful file uploads."""
    file_id: str = Field(description="Unique file identifier")
    original_filename: str = Field(description="Original filename")
    content_type: str = Field(description="MIME type")
    file_size: int = Field(description="File size in bytes")
    category: str = Field(description="File category")
    file_url: str = Field(description="URL to access the file")
    uploaded_at: datetime = Field(description="Upload timestamp")


class FileInfoResponse(SQLModel):
    """Response model for file information queries."""
    file_id: str = Field(description="Unique file identifier")
    original_filename: str = Field(description="Original filename")
    content_type: str = Field(description="MIME type")
    file_size: int = Field(description="File size in bytes")
    category: str = Field(description="File category")
    file_url: str = Field(description="URL to access the file")
    storage_type: str = Field(description="Storage backend type")
    is_public: bool = Field(description="Whether file is publicly accessible")
    uploaded_at: datetime = Field(description="Upload timestamp")
    user_id: Optional[uuid.UUID] = Field(description="Uploader user ID")
    organization_id: Optional[uuid.UUID] = Field(description="Organization ID")


class FileListResponse(SQLModel):
    """Response model for file listing operations."""
    files: list[FileInfoResponse] = Field(description="List of files")
    total: int = Field(description="Total number of files")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of files per page")
    total_pages: int = Field(description="Total number of pages")