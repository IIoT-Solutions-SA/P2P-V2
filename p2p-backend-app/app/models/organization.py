"""Organization model definitions."""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib

from app.models.enums import OrganizationStatus, IndustryType

if TYPE_CHECKING:
    from app.models.user import User


class Organization(SQLModel, table=True):
    """Organization model representing companies/entities on the platform."""
    
    __tablename__ = "organizations"
    
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
    name: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )
    name_arabic: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(String(2000), nullable=True)
    )
    
    # Contact Information
    email: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
    phone_number: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True)
    )
    website: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )
    
    # Address
    address_line_1: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )
    address_line_2: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )
    city: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True)
    )
    state_province: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True)
    )
    postal_code: Optional[str] = Field(
        default=None,
        sa_column=Column(String(20), nullable=True)
    )
    country: str = Field(
        default="SA",  # Saudi Arabia
        sa_column=Column(String(2), nullable=False)
    )
    
    # Business Information
    industry_type: IndustryType = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )
    company_size: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True)  # e.g., "1-10", "11-50", "51-200", etc.
    )
    registration_number: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), unique=True, nullable=True)
    )
    tax_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), unique=True, nullable=True)
    )
    
    # Branding
    logo_url: Optional[str] = Field(
        default=None,
        sa_column=Column(String(500), nullable=True)
    )
    banner_url: Optional[str] = Field(
        default=None,
        sa_column=Column(String(500), nullable=True)
    )
    
    # Status and Subscription
    status: OrganizationStatus = Field(
        default=OrganizationStatus.TRIAL,
        sa_column=Column(String(50), nullable=False, index=True)
    )
    trial_ends_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    subscription_tier: str = Field(
        default="basic",
        sa_column=Column(String(50), nullable=False)
    )
    
    # Usage Limits
    max_users: int = Field(default=10)
    max_use_cases: int = Field(default=50)
    max_storage_gb: int = Field(default=10)
    
    # Settings
    allow_public_use_cases: bool = Field(default=True)
    require_use_case_approval: bool = Field(default=False)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    
    @property
    def is_active(self) -> bool:
        """Check if organization is active."""
        return self.status in [OrganizationStatus.ACTIVE, OrganizationStatus.TRIAL] and not self.is_deleted
    
    @property
    def is_trial(self) -> bool:
        """Check if organization is in trial period."""
        return self.status == OrganizationStatus.TRIAL
    
    @property
    def has_trial_expired(self) -> bool:
        """Check if trial period has expired."""
        if self.trial_ends_at:
            trial_end = datetime.fromisoformat(self.trial_ends_at.replace('Z', '+00:00'))
            return datetime.utcnow() > trial_end
        return False
    
    def can_add_users(self, current_user_count: int) -> bool:
        """Check if organization can add more users."""
        return current_user_count < self.max_users and self.is_active
    
    def can_add_use_cases(self, current_use_case_count: int) -> bool:
        """Check if organization can add more use cases."""
        return current_use_case_count < self.max_use_cases and self.is_active
    
    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None