"""Authentication and user profile schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr


class OrganizationInfo(BaseModel):
    """Organization information in user profile."""
    id: str
    name: str
    size: str
    industry: str
    country: str
    city: Optional[str] = None


class UserProfile(BaseModel):
    """User profile response model."""
    id: str
    email: EmailStr
    firstName: str
    lastName: str
    role: str
    organization: Optional[OrganizationInfo] = None
    isActive: bool
    createdAt: str
    
    class Config:
        from_attributes = True


class SignupRequest(BaseModel):
    """Signup request model."""
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    organizationName: str
    organizationSize: str = "small"
    industry: str = "Other"
    country: str = "Saudi Arabia"
    city: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class SessionInfo(BaseModel):
    """Session information model."""
    userId: str
    email: str
    sessionHandle: str
    accessTokenPayload: Dict[str, Any]