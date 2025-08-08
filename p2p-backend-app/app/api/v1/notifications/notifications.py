"""Notification API endpoints."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.rbac import get_current_user as get_current_active_user
from app.models.user import User
from app.models.notification import (
    NotificationResponse, NotificationListResponse,
    NotificationPreference, NotificationPreferenceUpdate,
    NotificationType, NotificationStats,
    NotificationMarkReadRequest
)
from app.services.notifications import NotificationService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: Optional[NotificationType] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's notifications."""
    return await NotificationService.get_notifications(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
        notification_type=notification_type
    )


@router.post("/mark-read")
async def mark_notifications_as_read(
    request: NotificationMarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark specific notifications as read."""
    return await NotificationService.mark_as_read(
        db=db,
        user_id=current_user.id,
        notification_ids=request.notification_ids
    )


@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read."""
    return await NotificationService.mark_all_as_read(
        db=db,
        user_id=current_user.id
    )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a notification."""
    try:
        return await NotificationService.delete_notification(
            db=db,
            user_id=current_user.id,
            notification_id=notification_id
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/preferences", response_model=NotificationPreference)
async def get_notification_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's notification preferences."""
    return await NotificationService.get_user_preferences(
        db=db,
        user_id=current_user.id
    )


@router.put("/preferences", response_model=NotificationPreference)
async def update_notification_preferences(
    update_data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user's notification preferences."""
    return await NotificationService.update_preferences(
        db=db,
        user_id=current_user.id,
        update_data=update_data
    )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification statistics."""
    return await NotificationService.get_notification_stats(
        db=db,
        user_id=current_user.id
    )


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get unread notification count (for polling)."""
    stats = await NotificationService.get_notification_stats(
        db=db,
        user_id=current_user.id
    )
    return {
        "unread_count": stats.unread_notifications,
        "last_notification_at": stats.last_notification_at
    }