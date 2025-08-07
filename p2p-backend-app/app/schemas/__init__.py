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
from app.schemas.forum import (
    ForumCategoryResponse,
    ForumCategoryCreate,
    ForumCategoryUpdate,
    ForumTopicResponse,
    ForumTopicCreate,
    ForumTopicUpdate,
    ForumTopicListResponse,
    ForumTopicSearchQuery,
    ForumPostResponse,
    ForumPostCreate,
    ForumPostUpdate,
    ForumStatsResponse,
    ForumLikeResponse,
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
    # Forum schemas
    "ForumCategoryResponse",
    "ForumCategoryCreate", 
    "ForumCategoryUpdate",
    "ForumTopicResponse",
    "ForumTopicCreate",
    "ForumTopicUpdate",
    "ForumTopicListResponse",
    "ForumTopicSearchQuery",
    "ForumPostResponse",
    "ForumPostCreate",
    "ForumPostUpdate",
    "ForumStatsResponse",
    "ForumLikeResponse",
]