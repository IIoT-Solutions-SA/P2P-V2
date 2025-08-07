"""Database models package."""

from app.models.base import (
    BaseModel,
    BaseModelWithSoftDelete,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.models.enums import (
    ForumCategoryType,
    IndustryType,
    InvitationStatus,
    MessageStatus,
    NotificationType,
    OrganizationStatus,
    TechnologyCategory,
    UserRole,
    UserStatus,
)
from app.models.organization import Organization
from app.models.user import User
from app.models.file_new import FileMetadataNew as FileMetadata
from app.models.invitation import UserInvitation
from app.models.forum import (
    ForumCategory,
    ForumTopic,
    ForumPost,
    ForumTopicLike,
    ForumPostLike,
    ForumTopicView,
)

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
    "UserInvitation",
    # Forum models
    "ForumCategory",
    "ForumTopic",
    "ForumPost",
    "ForumTopicLike",
    "ForumPostLike",
    "ForumTopicView",
    # Enums
    "ForumCategoryType",
    "IndustryType",
    "InvitationStatus",
    "MessageStatus",
    "NotificationType",
    "OrganizationStatus",
    "TechnologyCategory",
    "UserRole",
    "UserStatus",
]