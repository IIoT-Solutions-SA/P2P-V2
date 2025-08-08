"""Background task service for async processing."""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from enum import Enum
import json
from dataclasses import dataclass, asdict
from sqlmodel import Session
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logging import get_logger

logger = get_logger(__name__)
# from app.services.email import email_service
from app.services.notifications import NotificationService  
from app.models.notification import NotificationType, NotificationCreate


class TaskStatus(str, Enum):
    """Background task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class BackgroundTask:
    """Background task definition."""
    id: str
    name: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    delay_seconds: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class BackgroundTaskService:
    """Service for managing background tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
        self.register_default_handlers()
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type."""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    def register_default_handlers(self):
        """Register default task handlers."""
        self.register_task_handler("send_email", self._handle_send_email)
        self.register_task_handler("send_notification", self._handle_send_notification)
        self.register_task_handler("cleanup_expired_data", self._handle_cleanup_expired_data)
        self.register_task_handler("generate_digest", self._handle_generate_digest)
        self.register_task_handler("process_analytics", self._handle_process_analytics)
    
    async def enqueue_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
        max_retries: int = 3
    ) -> str:
        """Enqueue a background task."""
        task_id = str(uuid4())
        
        task = BackgroundTask(
            id=task_id,
            name=f"{task_type}_{task_id[:8]}",
            task_type=task_type,
            payload=payload,
            priority=priority,
            delay_seconds=delay_seconds,
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        logger.info(f"Enqueued task {task_id} of type {task_type}")
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status by ID."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "id": task.id,
                "name": task.name,
                "task_type": task.task_type,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error": task.error,
                "retry_count": task.retry_count,
                "max_retries": task.max_retries
            }
        return None
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        return [
            {
                "id": task.id,
                "name": task.name,
                "task_type": task.task_type,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "retry_count": task.retry_count
            }
            for task in self.tasks.values()
        ]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.FAILED
                task.error = "Cancelled by user"
                logger.info(f"Cancelled task {task_id}")
                return True
        return False
    
    async def start_worker(self):
        """Start the background task worker."""
        if self.running:
            return
        
        self.running = True
        self.worker_task = asyncio.create_task(self._worker_loop())
        logger.info("Background task worker started")
    
    async def stop_worker(self):
        """Stop the background task worker."""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Background task worker stopped")
    
    async def _worker_loop(self):
        """Main worker loop."""
        while self.running:
            try:
                # Get next task to process
                task = self._get_next_task()
                
                if task:
                    await self._process_task(task)
                else:
                    # No tasks, wait before checking again
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in background task worker: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    def _get_next_task(self) -> Optional[BackgroundTask]:
        """Get the next task to process (priority-based)."""
        pending_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.PENDING and self._should_process_task(task)
        ]
        
        if not pending_tasks:
            return None
        
        # Sort by priority and creation time
        priority_order = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3
        }
        
        pending_tasks.sort(
            key=lambda t: (priority_order[t.priority], t.created_at)
        )
        
        return pending_tasks[0]
    
    def _should_process_task(self, task: BackgroundTask) -> bool:
        """Check if task should be processed now."""
        if task.delay_seconds > 0:
            delay_until = task.created_at + timedelta(seconds=task.delay_seconds)
            return datetime.utcnow() >= delay_until
        return True
    
    async def _process_task(self, task: BackgroundTask):
        """Process a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            logger.info(f"Processing task {task.id} of type {task.task_type}")
            
            # Get handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task.task_type}")
            
            # Execute handler
            await handler(task.payload)
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Task {task.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Retry with exponential backoff
                task.status = TaskStatus.PENDING
                task.delay_seconds = min(300, 2 ** task.retry_count)  # Max 5 minutes
                logger.info(f"Task {task.id} will retry in {task.delay_seconds} seconds")
            else:
                task.status = TaskStatus.FAILED
                logger.error(f"Task {task.id} failed permanently after {task.retry_count} attempts")
    
    # Task Handlers
    
    async def _handle_send_email(self, payload: Dict[str, Any]):
        """Handle email sending task."""
        # TODO: Re-implement when email service is fixed
        logger.info(f"Email task simulated: {payload.get('subject', 'No subject')}")
        # to_email = payload["to_email"] 
        # subject = payload["subject"]
        # html_content = payload.get("html_content", "")
        # text_content = payload.get("text_content")
        
        # success = await email_service.send_email(
        #     to_email=to_email,
        #     subject=subject,
        #     html_content=html_content,
        #     text_content=text_content
        # )
        
        # if not success:
        #     raise Exception("Failed to send email")
    
    async def _handle_send_notification(self, payload: Dict[str, Any]):
        """Handle notification sending task."""
        from app.db.session import get_session_sync
        
        try:
            with get_session_sync() as db:
                notification_data = NotificationCreate(**payload)
                await NotificationService.create_notification(db, notification_data)
            logger.info(f"Notification sent successfully: {payload.get('title', 'No title')}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            # Fall back to simulation for now
            logger.info(f"Notification task simulated: {payload.get('title', 'No title')}")
    
    async def _handle_cleanup_expired_data(self, payload: Dict[str, Any]):
        """Handle expired data cleanup."""
        # TODO: Re-implement when notification service is fixed
        logger.info(f"Cleanup task simulated: {payload.get('days_to_keep', 30)} days")
        # from app.core.database import get_session_sync
        
        # with get_session_sync() as db:
        #     # Clean up old notifications
        #     await NotificationService.cleanup_old_notifications(
        #         db, days_to_keep=payload.get("days_to_keep", 30)
        #     )
        #     
        #     # Clean up other expired data as needed
        #     logger.info("Expired data cleanup completed")
    
    async def _handle_generate_digest(self, payload: Dict[str, Any]):
        """Handle digest generation task."""
        user_id = payload["user_id"]
        organization_id = payload["organization_id"]
        period = payload.get("period", "daily")
        
        # Mock digest generation
        logger.info(f"Generated {period} digest for user {user_id}")
        
        # In production, this would:
        # 1. Gather user's activity and notifications
        # 2. Generate digest email
        # 3. Send via email service
    
    async def _handle_process_analytics(self, payload: Dict[str, Any]):
        """Handle analytics processing task."""
        organization_id = payload["organization_id"]
        metric_type = payload.get("metric_type", "engagement")
        
        # Mock analytics processing
        logger.info(f"Processed {metric_type} analytics for organization {organization_id}")
        
        # In production, this would:
        # 1. Aggregate data from various sources
        # 2. Calculate metrics and trends
        # 3. Store results for reporting
    
    async def cleanup_old_tasks(self, days_to_keep: int = 7) -> int:
        """Clean up old completed/failed tasks."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        tasks_to_remove = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            and task.created_at < cutoff_date
        ]
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
        return len(tasks_to_remove)
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get task queue statistics."""
        total_tasks = len(self.tasks)
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for task in self.tasks.values()
                if task.status == status
            )
        
        priority_counts = {}
        for priority in TaskPriority:
            priority_counts[priority.value] = sum(
                1 for task in self.tasks.values()
                if task.priority == priority and task.status == TaskStatus.PENDING
            )
        
        # Average processing time for completed tasks
        completed_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at
        ]
        
        avg_processing_time = 0
        if completed_tasks:
            total_time = sum(
                (task.completed_at - task.started_at).total_seconds()
                for task in completed_tasks
            )
            avg_processing_time = total_time / len(completed_tasks)
        
        return {
            "total_tasks": total_tasks,
            "status_counts": status_counts,
            "pending_by_priority": priority_counts,
            "average_processing_time_seconds": round(avg_processing_time, 2),
            "worker_running": self.running,
            "registered_handlers": list(self.task_handlers.keys())
        }


# Global background task service instance
background_task_service = BackgroundTaskService()


# Convenience functions for common tasks

async def send_email_async(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    priority: TaskPriority = TaskPriority.NORMAL
) -> str:
    """Enqueue an email sending task."""
    return await background_task_service.enqueue_task(
        task_type="send_email",
        payload={
            "to_email": to_email,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content
        },
        priority=priority
    )


async def send_notification_async(
    notification_data: Dict[str, Any],  # Changed from NotificationCreate to Dict
    priority: TaskPriority = TaskPriority.NORMAL
) -> str:
    """Enqueue a notification sending task."""
    return await background_task_service.enqueue_task(
        task_type="send_notification",
        payload=notification_data,  # Already a dict
        priority=priority
    )


async def schedule_cleanup_task(
    days_to_keep: int = 30,
    delay_seconds: int = 0
) -> str:
    """Schedule a data cleanup task."""
    return await background_task_service.enqueue_task(
        task_type="cleanup_expired_data",
        payload={"days_to_keep": days_to_keep},
        priority=TaskPriority.LOW,
        delay_seconds=delay_seconds
    )


async def schedule_digest_generation(
    user_id: UUID,
    organization_id: UUID,
    period: str = "daily",
    delay_seconds: int = 0
) -> str:
    """Schedule a digest generation task."""
    return await background_task_service.enqueue_task(
        task_type="generate_digest",
        payload={
            "user_id": str(user_id),
            "organization_id": str(organization_id),
            "period": period
        },
        priority=TaskPriority.NORMAL,
        delay_seconds=delay_seconds
    )