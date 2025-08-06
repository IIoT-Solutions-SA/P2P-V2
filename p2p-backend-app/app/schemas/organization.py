"""Organization schemas for API requests and responses."""

from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict

from app.models.enums import OrganizationStatus, IndustryType


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    name_arabic: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    website: Optional[HttpUrl] = None
    industry_type: IndustryType


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="SA", max_length=2)
    company_size: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=100)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_arabic: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    website: Optional[HttpUrl] = None
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    logo_url: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = Field(None, max_length=500)
    allow_public_use_cases: Optional[bool] = None
    require_use_case_approval: Optional[bool] = None


class OrganizationUpdateAdmin(OrganizationUpdate):
    """Schema for admin to update any organization."""
    status: Optional[OrganizationStatus] = None
    subscription_tier: Optional[str] = None
    max_users: Optional[int] = None
    max_use_cases: Optional[int] = None
    max_storage_gb: Optional[int] = None
    trial_ends_at: Optional[datetime] = None


class OrganizationInDBBase(OrganizationBase):
    """Base schema for organization in database."""
    id: UUID
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    company_size: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    status: OrganizationStatus
    trial_ends_at: Optional[datetime] = None
    subscription_tier: str
    max_users: int
    max_use_cases: int
    max_storage_gb: int
    allow_public_use_cases: bool
    require_use_case_approval: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Organization(OrganizationInDBBase):
    """Schema for organization response."""
    pass


class OrganizationBrief(BaseModel):
    """Brief organization info for nested responses."""
    id: UUID
    name: str
    name_arabic: Optional[str] = None
    logo_url: Optional[str] = None
    industry_type: IndustryType
    
    model_config = ConfigDict(from_attributes=True)


class OrganizationStats(BaseModel):
    """Organization statistics response."""
    # User Statistics
    total_users: int = 0
    active_users: int = 0
    admin_users: int = 0
    member_users: int = 0
    pending_users: int = 0
    inactive_users: int = 0
    
    # Activity Statistics  
    forum_topics: int = 0
    forum_posts: int = 0
    use_cases_submitted: int = 0
    use_cases_published: int = 0
    messages_sent: int = 0
    
    # Storage Statistics
    total_files: int = 0
    storage_used_bytes: int = 0
    storage_used_mb: float = 0.0
    storage_used_gb: float = 0.0
    storage_limit_gb: int = 0
    storage_percentage_used: float = 0.0
    
    # Subscription Information
    subscription_tier: str = "free"
    max_users: int = 0
    max_use_cases: int = 0
    trial_ends_at: Optional[datetime] = None
    
    # Timestamps
    calculated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OrganizationWithStats(Organization):
    """Organization with usage statistics."""
    user_count: int = 0
    active_user_count: int = 0
    use_case_count: int = 0
    forum_topic_count: int = 0
    storage_used_gb: float = 0.0