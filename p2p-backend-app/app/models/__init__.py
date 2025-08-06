"""Database models package."""

from app.models.base import (
    BaseModel,
    BaseModelWithSoftDelete,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.models.enums import (
    ForumCategory,
    IndustryType,
    MessageStatus,
    NotificationType,
    OrganizationStatus,
    TechnologyCategory,
    UserRole,
    UserStatus,
)
from app.models.organization import Organization
from app.models.user import User
from app.models.file import FileMetadata

__all__ = [
    # Base models
    "BaseModel",
    "BaseModelWithSoftDelete",
    "SoftDeleteMixin",
    "TimestampMixin",
    # Domain models
    "Organization",
    "User",
    "FileMetadata",
    # Enums
    "ForumCategory",
    "IndustryType",
    "MessageStatus",
    "NotificationType",
    "OrganizationStatus",
    "TechnologyCategory",
    "UserRole",
    "UserStatus",
]