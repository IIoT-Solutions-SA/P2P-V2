"""
Pydantic schemas for invitation system
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class InvitationCreate(BaseModel):
    """Schema for creating an invitation"""
    email: EmailStr

class InvitationResponse(BaseModel):
    """Schema for invitation response"""
    id: str
    email: EmailStr
    token: str
    invited_by_id: str
    invited_by_email: str
    invited_by_name: str
    expires_at: datetime
    used: bool
    used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvitationValidation(BaseModel):
    """Schema for invitation validation response"""
    valid: bool
    email: Optional[EmailStr] = None
    invited_by_name: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None
    # Organization data from inviter
    organization_name: Optional[str] = None
    industry: Optional[str] = None
    organization_size: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class InvitationList(BaseModel):
    """Schema for list of invitations"""
    invitations: list[InvitationResponse]
    total: int