"""Background tasks API endpoints."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.rbac import get_current_user as get_current_active_user
from app.models.user import User
from app.services.background_tasks import (
    background_task_service, TaskPriority, send_email_async,
    send_notification_async, schedule_cleanup_task,
    schedule_digest_generation
)
from app.models.notification import NotificationCreate

router = APIRouter(prefix="/tasks", tags=["background-tasks"])


@router.get("/")
async def get_all_tasks(
    current_user: User = Depends(get_current_active_user)
):
    """Get all background tasks (admin only)."""
    # In production, add admin role check
    return await background_task_service.get_all_tasks()


@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get task status by ID."""
    task_status = await background_task_service.get_task_status(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task_status


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a pending task."""
    success = await background_task_service.cancel_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be cancelled (not pending or not found)"
        )
    return {"message": f"Task {task_id} cancelled successfully"}


@router.get("/stats/overview")
async def get_task_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get task queue statistics."""
    return await background_task_service.get_task_statistics()


@router.post("/email/send")
async def queue_email_task(
    to_email: str = Query(...),
    subject: str = Query(...),
    html_content: str = Query(...),
    text_content: Optional[str] = Query(None),
    priority: TaskPriority = Query(TaskPriority.NORMAL),
    current_user: User = Depends(get_current_active_user)
):
    """Queue an email sending task."""
    task_id = await send_email_async(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        priority=priority
    )
    return {"task_id": task_id, "message": "Email task queued successfully"}


@router.post("/notification/send")
async def queue_notification_task(
    notification: NotificationCreate,
    priority: TaskPriority = Query(TaskPriority.NORMAL),
    current_user: User = Depends(get_current_active_user)
):
    """Queue a notification sending task."""
    task_id = await send_notification_async(
        notification_data=notification,
        priority=priority
    )
    return {"task_id": task_id, "message": "Notification task queued successfully"}


@router.post("/cleanup/schedule")
async def schedule_cleanup(
    days_to_keep: int = Query(30, ge=1, le=365),
    delay_hours: int = Query(0, ge=0, le=24),
    current_user: User = Depends(get_current_active_user)
):
    """Schedule a data cleanup task."""
    task_id = await schedule_cleanup_task(
        days_to_keep=days_to_keep,
        delay_seconds=delay_hours * 3600
    )
    return {"task_id": task_id, "message": "Cleanup task scheduled successfully"}


@router.post("/digest/generate")
async def queue_digest_generation(
    user_id: Optional[UUID] = Query(None, description="User ID (defaults to current user)"),
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    delay_hours: int = Query(0, ge=0, le=24),
    current_user: User = Depends(get_current_active_user)
):
    """Queue a digest generation task."""
    target_user_id = user_id or current_user.id
    
    task_id = await schedule_digest_generation(
        user_id=target_user_id,
        organization_id=current_user.organization_id,
        period=period,
        delay_seconds=delay_hours * 3600
    )
    return {"task_id": task_id, "message": f"{period.title()} digest generation queued successfully"}


@router.post("/worker/start")
async def start_worker(
    current_user: User = Depends(get_current_active_user)
):
    """Start the background task worker (admin only)."""
    # In production, add admin role check
    await background_task_service.start_worker()
    return {"message": "Background task worker started"}


@router.post("/worker/stop")
async def stop_worker(
    current_user: User = Depends(get_current_active_user)
):
    """Stop the background task worker (admin only)."""
    # In production, add admin role check
    await background_task_service.stop_worker()
    return {"message": "Background task worker stopped"}


@router.post("/cleanup/old-tasks")
async def cleanup_old_tasks(
    days_to_keep: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_active_user)
):
    """Clean up old completed/failed tasks (admin only)."""
    # In production, add admin role check
    removed_count = await background_task_service.cleanup_old_tasks(days_to_keep)
    return {
        "message": f"Cleaned up {removed_count} old tasks",
        "removed_count": removed_count
    }


@router.post("/test/email")
async def test_email_task(
    current_user: User = Depends(get_current_active_user)
):
    """Queue a test email task."""
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user has no email address"
        )
    
    task_id = await send_email_async(
        to_email=current_user.email,
        subject="Background Task Test Email",
        html_content=f"""
        <html>
            <body>
                <h2>Background Task Test</h2>
                <p>Hello {current_user.first_name},</p>
                <p>This is a test email sent via the background task system.</p>
                <p>Task executed at: {__import__('datetime').datetime.utcnow().isoformat()}</p>
                <hr>
                <small>P2P Sandbox - Background Task System</small>
            </body>
        </html>
        """,
        text_content=f"Hello {current_user.first_name}, this is a test email from the background task system.",
        priority=TaskPriority.NORMAL
    )
    
    return {
        "task_id": task_id,
        "message": f"Test email task queued for {current_user.email}"
    }