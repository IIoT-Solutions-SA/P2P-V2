"""Base models with common fields and functionality."""

from datetime import datetime
from typing import Optional
import uuid as uuid_lib
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(SQLModel):
    """Base model with UUID primary key and timestamps."""
    
    id: uuid_lib.UUID = Field(
        default_factory=uuid_lib.uuid4,
        primary_key=True,
        sa_column_kwargs={
            "default": uuid_lib.uuid4,
            "nullable": False,
        },
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
        },
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
            "nullable": False,
        },
    )
    
    class Config:
        # Allow population by field name (for Pydantic compatibility)
        populate_by_name = True
        # Use enum values instead of names
        use_enum_values = True
        # Allow arbitrary types (for UUID)
        arbitrary_types_allowed = True
        # JSON encoders for special types
        json_encoders = {
            uuid_lib.UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class BaseModelWithSoftDelete(BaseModel):
    """Base model with UUID, timestamps, and soft delete functionality."""
    
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )
    
    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None


# Keep these for backward compatibility
class TimestampMixin:
    """Deprecated: Use BaseModel instead."""
    pass


class SoftDeleteMixin:
    """Deprecated: Use BaseModelWithSoftDelete instead."""
    pass