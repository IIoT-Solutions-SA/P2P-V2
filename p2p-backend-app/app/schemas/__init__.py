"""API schemas package."""

from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserUpdateAdmin,
    UserProfile,
    UserWithOrganization,
)
from app.schemas.organization import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationUpdateAdmin,
    OrganizationBrief,
    OrganizationWithStats,
)

__all__ = [
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserUpdateAdmin",
    "UserProfile",
    "UserWithOrganization",
    # Organization schemas
    "Organization",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationUpdateAdmin",
    "OrganizationBrief",
    "OrganizationWithStats",
]