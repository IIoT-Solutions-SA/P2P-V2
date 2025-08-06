"""Invitation schemas for API requests and responses."""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import UserRole, InvitationStatus


class InvitationBase(BaseModel):
    """Base invitation schema with common fields."""
    email: EmailStr = Field(..., description="Email address of the person to invite")
    invited_role: UserRole = Field(default=UserRole.MEMBER, description="Role to assign to the invited user")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Pre-filled first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Pre-filled last name")
    job_title: Optional[str] = Field(None, max_length=100, description="Pre-filled job title")
    department: Optional[str] = Field(None, max_length=100, description="Pre-filled department")
    personal_message: Optional[str] = Field(None, max_length=1000, description="Optional personal message")


class InvitationCreate(InvitationBase):
    """Schema for creating a new invitation."""
    expires_in_days: int = Field(default=7, ge=1, le=30, description="Days until invitation expires")


class InvitationSend(InvitationCreate):
    """Schema for sending invitation (includes email template options)."""
    send_welcome_email: bool = Field(default=True, description="Whether to send welcome email")
    email_template: Optional[str] = Field(default="default", description="Email template to use")


class InvitationResponse(BaseModel):
    """Response schema for invitation operations."""
    id: UUID = Field(..., description="Invitation ID")
    email: EmailStr = Field(..., description="Invited email address")
    token: str = Field(..., description="Invitation token")
    organization_id: UUID = Field(..., description="Organization ID")
    invited_role: UserRole = Field(..., description="Invited role")
    invited_by: UUID = Field(..., description="User who sent the invitation")
    status: InvitationStatus = Field(..., description="Invitation status")
    first_name: Optional[str] = Field(None, description="Pre-filled first name")
    last_name: Optional[str] = Field(None, description="Pre-filled last name")
    job_title: Optional[str] = Field(None, description="Job title")
    department: Optional[str] = Field(None, description="Department")
    personal_message: Optional[str] = Field(None, description="Personal message")
    expires_at: datetime = Field(..., description="When invitation expires")
    accepted_at: Optional[datetime] = Field(None, description="When invitation was accepted")
    created_at: datetime = Field(..., description="When invitation was created")
    updated_at: datetime = Field(..., description="When invitation was last updated")
    
    # Computed properties
    is_expired: bool = Field(..., description="Whether invitation has expired")
    is_pending: bool = Field(..., description="Whether invitation is still pending")
    days_until_expiry: int = Field(..., description="Days until expiry (0 if expired)")
    
    model_config = ConfigDict(from_attributes=True)


class InvitationAccept(BaseModel):
    """Schema for accepting an invitation."""
    token: str = Field(..., min_length=1, description="Invitation token")
    password: str = Field(..., min_length=8, description="Password for new account")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name (if not pre-filled)")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name (if not pre-filled)")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    bio: Optional[str] = Field(None, max_length=1000, description="User bio")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title (override pre-filled)")
    department: Optional[str] = Field(None, max_length=100, description="Department (override pre-filled)")


class InvitationListResponse(BaseModel):
    """Response schema for listing invitations."""
    invitations: List[InvitationResponse] = Field(..., description="List of invitations")
    total: int = Field(..., description="Total number of invitations")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class InvitationStats(BaseModel):
    """Statistics about invitations for an organization."""
    total_sent: int = Field(..., description="Total invitations sent")
    pending: int = Field(..., description="Pending invitations")
    accepted: int = Field(..., description="Accepted invitations")
    expired: int = Field(..., description="Expired invitations")
    cancelled: int = Field(..., description="Cancelled invitations")
    acceptance_rate: float = Field(..., description="Acceptance rate as percentage")
    recent_invitations: List[InvitationResponse] = Field(..., description="Recent invitations (last 10)")


class InvitationToken(BaseModel):
    """Schema for invitation token validation."""
    token: str = Field(..., description="Invitation token")
    is_valid: bool = Field(..., description="Whether token is valid")
    invitation: Optional[InvitationResponse] = Field(None, description="Invitation details if valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid")


class BulkInvitationCreate(BaseModel):
    """Schema for creating multiple invitations."""
    invitations: List[InvitationCreate] = Field(..., min_items=1, max_items=50, description="List of invitations to create")
    default_role: UserRole = Field(default=UserRole.MEMBER, description="Default role for all invitations")
    default_expires_in_days: int = Field(default=7, ge=1, le=30, description="Default expiry days")
    send_welcome_emails: bool = Field(default=True, description="Whether to send welcome emails")


class BulkInvitationResponse(BaseModel):
    """Response schema for bulk invitation creation."""
    successful_invitations: List[InvitationResponse] = Field(..., description="Successfully created invitations")
    failed_invitations: List[dict] = Field(..., description="Failed invitations with error details")
    total_sent: int = Field(..., description="Total invitations sent")
    total_failed: int = Field(..., description="Total invitations failed")
    success_rate: float = Field(..., description="Success rate as percentage")