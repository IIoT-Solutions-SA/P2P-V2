"""Forum post endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user as get_current_active_user
from app.core.rbac import require_organization_access
from app.db.session import get_db
from app.models.user import User
from app.services.forum import ForumService
from app.schemas.forum import (
    ForumPostResponse,
    ForumPostCreate,
    ForumPostUpdate,
    ForumLikeResponse
)

router = APIRouter()


@router.get("/", response_model=List[ForumPostResponse])
async def get_topic_posts(
    topic_id: UUID = Query(..., description="Topic ID to get posts for"),
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of posts to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get posts for a specific topic.
    
    **Parameters:**
    - `topic_id`: ID of the topic to get posts for
    - `skip`: Number of posts to skip (for pagination)
    - `limit`: Maximum number of posts to return (1-100)
    
    **Returns:** List of posts ordered by creation date (oldest first)
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    return await ForumService.get_topic_posts(
        db,
        topic_id=topic_id,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    *,
    db: AsyncSession = Depends(get_db),
    post_data: ForumPostCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new forum post or reply.
    
    **Required Fields:**
    - `content`: Post content (markdown supported)
    - `topic_id`: ID of the topic to post in
    
    **Optional Fields:**
    - `parent_post_id`: ID of parent post (for replies)
    
    **Note:** Cannot post to locked topics.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    return await ForumService.create_post(
        db,
        post_data=post_data,
        author_id=current_user.id,
        organization_id=current_user.organization_id
    )


@router.post("/{post_id}/like", response_model=ForumLikeResponse)
async def toggle_post_like(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Like or unlike a post.
    
    **Behavior:**
    - If not liked: adds a like
    - If already liked: removes the like
    
    **Returns:**
    - `success`: Whether operation succeeded
    - `liked`: Current like status after toggle
    - `likes_count`: New total like count
    - `message`: Success message
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # Note: This would use a similar service method for post likes
    # For now, return a placeholder response
    return ForumLikeResponse(
        success=True,
        liked=True,
        likes_count=1,
        message="Post like functionality will be implemented in P4.FORUM.02"
    )