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
    
    return await ForumService.toggle_post_like(
        db,
        post_id=post_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )


@router.put("/{post_id}", response_model=ForumPostResponse)
async def update_post(
    post_id: UUID,
    *,
    db: AsyncSession = Depends(get_db),
    post_data: ForumPostUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a forum post.
    
    **Permissions:**
    - Post author can edit their own posts
    - Admins can edit any post
    
    **Updatable Fields:**
    - `content`: Post content (markdown supported)
    
    **Note:** Cannot edit posts in locked topics.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    return await ForumService.update_post(
        db,
        post_id=post_id,
        post_data=post_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=current_user.is_admin
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a forum post.
    
    **Permissions:**
    - Post author can delete their own posts
    - Admins can delete any post
    
    **Note:** Deleting a parent post will also delete all replies.
    This action cannot be undone.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    await ForumService.delete_post(
        db,
        post_id=post_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=current_user.is_admin
    )


@router.post("/{post_id}/best-answer", response_model=ForumPostResponse)
async def mark_as_best_answer(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark a post as the best answer for its topic.
    
    **Permissions:**
    - Topic author can mark any post as best answer
    - Admins can mark any post as best answer
    
    **Note:** Only one post can be marked as best answer per topic.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    return await ForumService.mark_best_answer(
        db,
        post_id=post_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=current_user.is_admin
    )