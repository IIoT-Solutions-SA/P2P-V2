"""User schemas for API requests and responses."""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=1000)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    organization_id: UUID
    role: UserRole = UserRole.MEMBER
    supertokens_user_id: str  # Will be set after SuperTokens registration


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_picture_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    email_notifications_enabled: Optional[bool] = None
    forum_notifications_enabled: Optional[bool] = None
    message_notifications_enabled: Optional[bool] = None


class UserUpdateAdmin(UserUpdate):
    """Schema for admin to update any user."""
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: UUID
    organization_id: UUID
    role: UserRole
    status: UserStatus
    profile_picture_url: Optional[str] = None
    supertokens_user_id: str
    email_notifications_enabled: bool
    forum_notifications_enabled: bool
    message_notifications_enabled: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """Schema for user response (excludes sensitive data)."""
    pass


class UserWithOrganization(User):
    """Schema for user with organization details."""
    organization_name: str
    organization_id: UUID


class UserProfile(User):
    """Schema for user profile (includes additional details)."""
    organization: "OrganizationBrief"
    total_posts: int = 0
    total_use_cases: int = 0


# Avoid circular imports
from app.schemas.organization import OrganizationBrief
UserProfile.model_rebuild()