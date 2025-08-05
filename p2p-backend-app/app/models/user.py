"""User model definitions."""

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib

from app.models.enums import UserRole, UserStatus

if TYPE_CHECKING:
    from app.models.organization import Organization


class User(SQLModel, table=True):
    """User model representing platform users."""
    
    __tablename__ = "users"
    
    # Primary key
    id: uuid_lib.UUID = Field(
        default_factory=uuid_lib.uuid4,
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid_lib.uuid4,
            nullable=False,
        ),
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    
    # Basic Information
    email: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )
    first_name: str = Field(
        sa_column=Column(String(100), nullable=False)
    )
    last_name: str = Field(
        sa_column=Column(String(100), nullable=False)
    )
    phone_number: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True)
    )
    profile_picture_url: Optional[str] = Field(
        default=None,
        sa_column=Column(String(500), nullable=True)
    )
    
    # Role and Status
    role: UserRole = Field(
        default=UserRole.MEMBER,
        sa_column=Column(String(50), nullable=False)
    )
    status: UserStatus = Field(
        default=UserStatus.PENDING,
        sa_column=Column(String(50), nullable=False, index=True)
    )
    
    # Organization relationship
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    
    # SuperTokens user ID (from authentication service)
    supertokens_user_id: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )
    
    # Additional fields
    bio: Optional[str] = Field(
        default=None,
        sa_column=Column(String(1000), nullable=True)
    )
    job_title: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True)
    )
    department: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True)
    )
    
    # Settings
    email_notifications_enabled: bool = Field(default=True)
    forum_notifications_enabled: bool = Field(default=True)
    message_notifications_enabled: bool = Field(default=True)
    
    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="users")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users in the organization."""
        return self.is_admin and self.is_active
    
    def can_create_content(self) -> bool:
        """Check if user can create forum posts and use cases."""
        return self.is_active
    
    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None