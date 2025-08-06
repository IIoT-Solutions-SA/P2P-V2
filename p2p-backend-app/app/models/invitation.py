"""Invitation model for user invitation system."""

from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib

from app.models.base import BaseModel
from app.models.enums import UserRole, InvitationStatus


class UserInvitation(BaseModel, table=True):
    """Model for tracking user invitations to organizations."""
    
    __tablename__ = "user_invitations"
    
    # Invitation details
    email: str = Field(
        sa_column=Column(String(255), nullable=False, index=True),
        description="Email address of invited user"
    )
    token: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True),
        description="Unique invitation token for verification"
    )
    
    # Organization and role
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        description="Organization the user is invited to join"
    )
    invited_role: UserRole = Field(
        default=UserRole.MEMBER,
        sa_column=Column(String(50), nullable=False),
        description="Role the user will have when they join"
    )
    
    # Invitation metadata
    invited_by: uuid_lib.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        description="User who sent the invitation"
    )
    status: InvitationStatus = Field(
        default=InvitationStatus.PENDING,
        sa_column=Column(String(50), nullable=False, index=True),
        description="Current status of the invitation"
    )
    
    # Personal details (optional, pre-filled)
    first_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
        description="Pre-filled first name for invited user"
    )
    last_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
        description="Pre-filled last name for invited user"
    )
    job_title: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
        description="Pre-filled job title for invited user"
    )
    department: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
        description="Pre-filled department for invited user"
    )
    
    # Timing
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="When the invitation expires"
    )
    accepted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="When the invitation was accepted"
    )
    
    # Message
    personal_message: Optional[str] = Field(
        default=None,
        sa_column=Column(String(1000), nullable=True),
        description="Optional personal message from inviter"
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if the invitation has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_pending(self) -> bool:
        """Check if the invitation is still pending."""
        return self.status == InvitationStatus.PENDING and not self.is_expired
    
    @property
    def days_until_expiry(self) -> int:
        """Get number of days until expiry."""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def mark_as_accepted(self, accepted_by_user_id: uuid_lib.UUID) -> None:
        """Mark invitation as accepted."""
        self.status = InvitationStatus.ACCEPTED
        self.accepted_at = datetime.utcnow()
    
    def mark_as_expired(self) -> None:
        """Mark invitation as expired."""
        if self.is_expired and self.status == InvitationStatus.PENDING:
            self.status = InvitationStatus.EXPIRED
    
    @classmethod
    def create_invitation(
        cls,
        email: str,
        organization_id: uuid_lib.UUID,
        invited_by: uuid_lib.UUID,
        token: str,
        invited_role: UserRole = UserRole.MEMBER,
        expires_in_days: int = 7,
        **optional_fields
    ) -> "UserInvitation":
        """Create a new invitation with proper expiry."""
        return cls(
            email=email,
            token=token,
            organization_id=organization_id,
            invited_by=invited_by,
            invited_role=invited_role,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            first_name=optional_fields.get('first_name'),
            last_name=optional_fields.get('last_name'),
            job_title=optional_fields.get('job_title'),
            department=optional_fields.get('department'),
            personal_message=optional_fields.get('personal_message'),
            status=InvitationStatus.PENDING
        )