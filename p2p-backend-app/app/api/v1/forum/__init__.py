"""Forum API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user as get_current_active_user
from app.core.rbac import require_organization_access
from app.db.session import get_db
from app.models.user import User
from app.services.forum import ForumService
from app.schemas.forum import ForumStatsResponse

from . import categories, topics, posts

# Main forum router
forum_router = APIRouter()

# Include sub-routers
forum_router.include_router(categories.router, prefix="/categories", tags=["Forum Categories"])
forum_router.include_router(topics.router, prefix="/topics", tags=["Forum Topics"])
forum_router.include_router(posts.router, prefix="/posts", tags=["Forum Posts"])


@forum_router.get("/stats", response_model=ForumStatsResponse, tags=["Forum"])
async def get_forum_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get forum statistics for the current organization.
    
    **Returns:**
    - `total_topics`: Total number of topics
    - `total_posts`: Total number of posts/replies
    - `active_members`: Number of users who have posted
    - `helpful_answers`: Number of posts marked as best answers
    - `categories`: List of all active categories with counts
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    return await ForumService.get_forum_stats(
        db,
        organization_id=current_user.organization_id
    )