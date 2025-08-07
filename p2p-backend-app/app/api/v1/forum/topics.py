"""Forum topic endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user as get_current_active_user, get_current_admin_user as require_admin
from app.core.rbac import require_organization_access
from app.db.session import get_db
from app.models.user import User
from app.services.forum import ForumService
from app.schemas.forum import (
    ForumTopicResponse,
    ForumTopicCreate,
    ForumTopicUpdate,
    ForumTopicListResponse,
    ForumTopicSearchQuery,
    ForumLikeResponse
)

router = APIRouter()


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request."""
    # Get real IP from headers if behind proxy
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
        request.headers.get("X-Real-IP") or
        request.client.host if request.client else None
    )
    user_agent = request.headers.get("User-Agent")
    return client_ip, user_agent


@router.get("/", response_model=ForumTopicListResponse)
async def list_topics(
    request: Request,
    search: Optional[str] = Query(None, max_length=200, description="Search in title and content"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    author_id: Optional[UUID] = Query(None, description="Filter by author"),
    is_pinned: Optional[bool] = Query(None, description="Filter pinned topics"),
    has_best_answer: Optional[bool] = Query(None, description="Filter topics with best answers"),
    sort_by: str = Query("last_activity_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get forum topics with search, filtering, and pagination.
    
    **Search and Filter Options:**
    - `search`: Search in topic title, content, and excerpt
    - `category_id`: Filter by specific category
    - `author_id`: Filter by specific author
    - `is_pinned`: Show only pinned topics (true) or non-pinned (false)
    - `has_best_answer`: Show only topics with best answers marked
    
    **Sorting:**
    - `sort_by`: Field to sort by (last_activity_at, created_at, title, views_count, likes_count)
    - `sort_order`: Sort direction (asc, desc)
    
    **Pagination:**
    - `page`: Page number (1-based)
    - `page_size`: Number of items per page (1-100)
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    search_params = ForumTopicSearchQuery(
        search=search,
        category_id=category_id,
        author_id=author_id,
        is_pinned=is_pinned,
        has_best_answer=has_best_answer,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    return await ForumService.get_topics(
        db,
        search_params=search_params,
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )


@router.post("/", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    *,
    db: AsyncSession = Depends(get_db),
    topic_data: ForumTopicCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new forum topic.
    
    **Required Fields:**
    - `title`: Topic title (1-200 characters)
    - `content`: Topic content (markdown supported)
    - `excerpt`: Brief description (1-300 characters)
    - `category_id`: Valid category ID
    
    **Optional Fields:**
    - `is_pinned`: Pin topic to top (admin only)
    
    The topic will be automatically assigned to your organization and marked as active.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # Only admins can create pinned topics
    if topic_data.is_pinned and not current_user.is_admin:
        topic_data.is_pinned = False
    
    return await ForumService.create_topic(
        db,
        topic_data=topic_data,
        author_id=current_user.id,
        organization_id=current_user.organization_id
    )


@router.get("/{topic_id}", response_model=ForumTopicResponse)
async def get_topic(
    topic_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific topic by ID with view tracking.
    
    This endpoint automatically tracks views for analytics.
    Multiple views by the same user within 1 hour are not counted.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # Get client information for view tracking
    client_ip, user_agent = get_client_info(request)
    
    return await ForumService.get_topic(
        db,
        topic_id=topic_id,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        ip_address=client_ip,
        user_agent=user_agent
    )


@router.put("/{topic_id}", response_model=ForumTopicResponse)
async def update_topic(
    topic_id: UUID,
    *,
    db: AsyncSession = Depends(get_db),
    topic_data: ForumTopicUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a forum topic.
    
    **Permissions:**
    - Topic author can edit their own topics
    - Admins can edit any topic
    - Only admins can pin/unpin or lock/unlock topics
    
    **Updatable Fields:**
    - `title`: Topic title (1-200 characters)
    - `content`: Topic content (markdown supported)  
    - `excerpt`: Brief description (1-300 characters)
    - `category_id`: Change category (if admin or author)
    - `is_pinned`: Pin/unpin topic (admin only)
    - `is_locked`: Lock/unlock topic (admin only)
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # Only admins can modify pinned status and locked status
    if not current_user.is_admin:
        topic_data.is_pinned = None
        topic_data.is_locked = None
    
    return await ForumService.update_topic(
        db,
        topic_id=topic_id,
        topic_data=topic_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=current_user.is_admin
    )


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a forum topic.
    
    **Permissions:**
    - Topic author can delete their own topics
    - Admins can delete any topic
    
    **Note:** This will also delete all posts/replies in the topic.
    This action cannot be undone.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    await ForumService.delete_topic(
        db,
        topic_id=topic_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=current_user.is_admin
    )


@router.post("/{topic_id}/like", response_model=ForumLikeResponse)
async def toggle_topic_like(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Like or unlike a topic.
    
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
    
    return await ForumService.toggle_topic_like(
        db,
        topic_id=topic_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )


# Admin-only endpoints for bulk operations
@router.post("/{topic_id}/pin", response_model=ForumTopicResponse)
async def pin_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Pin a topic to the top (admin only)."""
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    topic_data = ForumTopicUpdate(is_pinned=True)
    return await ForumService.update_topic(
        db,
        topic_id=topic_id,
        topic_data=topic_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=True
    )


@router.post("/{topic_id}/unpin", response_model=ForumTopicResponse)
async def unpin_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Unpin a topic (admin only)."""
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    topic_data = ForumTopicUpdate(is_pinned=False)
    return await ForumService.update_topic(
        db,
        topic_id=topic_id,
        topic_data=topic_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=True
    )


@router.post("/{topic_id}/lock", response_model=ForumTopicResponse)
async def lock_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Lock a topic to prevent new replies (admin only)."""
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    topic_data = ForumTopicUpdate(is_locked=True)
    return await ForumService.update_topic(
        db,
        topic_id=topic_id,
        topic_data=topic_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=True
    )


@router.post("/{topic_id}/unlock", response_model=ForumTopicResponse)
async def unlock_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Unlock a topic to allow new replies (admin only)."""
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    topic_data = ForumTopicUpdate(is_locked=False)
    return await ForumService.update_topic(
        db,
        topic_id=topic_id,
        topic_data=topic_data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        is_admin=True
    )