"""Notification service for handling in-app and email notifications."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import json
from sqlmodel import Session, select, and_, or_, func, desc
from sqlalchemy import text

from app.models.notification import (
    Notification, NotificationCreate, NotificationResponse,
    NotificationPreference, NotificationPreferenceUpdate,
    NotificationTemplate, NotificationListResponse,
    NotificationType, NotificationChannel, NotificationPriority,
    NotificationStats, NotificationMarkReadRequest
)
from app.models.user import User
from app.models.message import Message
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.services.email import email_service

logger = get_logger(__name__)


class NotificationService:
    """Service for handling notifications."""
    
    @staticmethod
    async def create_notification(
        db: Session,
        notification_data: NotificationCreate,
        send_email: bool = True
    ) -> Notification:
        """Create a new notification."""
        # Get user preferences
        preferences = await NotificationService.get_user_preferences(
            db, notification_data.user_id
        )
        
        # Check if notifications are enabled
        if not preferences or not preferences.enabled:
            logger.info(f"Notifications disabled for user {notification_data.user_id}")
            return None
        
        # Create notification
        notification = Notification(**notification_data.dict())
        notification.delivered_channels = [NotificationChannel.IN_APP]
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send email if enabled and requested
        if send_email and preferences.email_enabled:
            if await NotificationService._should_send_email(preferences, notification):
                await NotificationService._send_email_notification(
                    db, notification, preferences
                )
        
        logger.info(f"Created notification {notification.id} for user {notification.user_id}")
        return notification
    
    @staticmethod
    async def create_message_notification(
        db: Session,
        message: Message,
        sender: User
    ) -> Optional[Notification]:
        """Create notification for new message."""
        notification_data = NotificationCreate(
            user_id=message.recipient_id,
            type=NotificationType.MESSAGE_RECEIVED,
            title="New Message",
            message=f"{sender.first_name} {sender.last_name} sent you a message",
            priority=NotificationPriority.MEDIUM,
            related_entity_type="message",
            related_entity_id=message.id,
            sender_id=sender.id,
            sender_name=f"{sender.first_name} {sender.last_name}",
            action_url=f"/messages/conversations/{message.conversation_id}",
            metadata={
                "conversation_id": str(message.conversation_id),
                "message_preview": message.content[:100]
            }
        )
        
        return await NotificationService.create_notification(db, notification_data)
    
    @staticmethod
    async def get_notifications(
        db: Session,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None
    ) -> NotificationListResponse:
        """Get user's notifications."""
        offset = (page - 1) * page_size
        
        # Build query
        statement = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                or_(
                    Notification.expires_at == None,
                    Notification.expires_at > datetime.utcnow()
                )
            )
        )
        
        # Filter by unread
        if unread_only:
            statement = statement.where(Notification.is_read == False)
        
        # Filter by type
        if notification_type:
            statement = statement.where(Notification.type == notification_type)
        
        # Order by created_at
        statement = statement.order_by(desc(Notification.created_at))
        
        # Get total and unread counts
        total_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(total_statement).one()
        
        unread_statement = select(func.count()).select_from(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).subquery()
        )
        unread_count = db.exec(unread_statement).one()
        
        # Get paginated results
        statement = statement.offset(offset).limit(page_size)
        notifications = db.exec(statement).all()
        
        # Build response
        notification_responses = [
            NotificationResponse(**notif.dict())
            for notif in notifications
        ]
        
        return NotificationListResponse(
            notifications=notification_responses,
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size,
            has_more=(offset + page_size) < total
        )
    
    @staticmethod
    async def mark_as_read(
        db: Session,
        user_id: UUID,
        notification_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Mark notifications as read."""
        # Get notifications
        statement = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.id.in_(notification_ids),
                Notification.is_read == False
            )
        )
        notifications = db.exec(statement).all()
        
        # Mark as read
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Marked {len(notifications)} notifications as read",
            "marked_count": len(notifications)
        }
    
    @staticmethod
    async def mark_all_as_read(
        db: Session,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Mark all notifications as read."""
        statement = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        notifications = db.exec(statement).all()
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Marked all {len(notifications)} notifications as read",
            "marked_count": len(notifications)
        }
    
    @staticmethod
    async def delete_notification(
        db: Session,
        user_id: UUID,
        notification_id: UUID
    ) -> Dict[str, Any]:
        """Delete a notification."""
        notification = db.get(Notification, notification_id)
        
        if not notification:
            raise NotFoundException(f"Notification {notification_id} not found")
        
        if notification.user_id != user_id:
            raise NotFoundException(f"Notification {notification_id} not found")
        
        db.delete(notification)
        db.commit()
        
        return {"message": "Notification deleted successfully"}
    
    @staticmethod
    async def get_user_preferences(
        db: Session,
        user_id: UUID
    ) -> Optional[NotificationPreference]:
        """Get user's notification preferences."""
        statement = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )
        preferences = db.exec(statement).first()
        
        # Create default preferences if not exists
        if not preferences:
            preferences = NotificationPreference(user_id=user_id)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
        
        return preferences
    
    @staticmethod
    async def update_preferences(
        db: Session,
        user_id: UUID,
        update_data: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        """Update user's notification preferences."""
        preferences = await NotificationService.get_user_preferences(db, user_id)
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(preferences, field, value)
        
        preferences.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(preferences)
        
        return preferences
    
    @staticmethod
    async def get_notification_stats(
        db: Session,
        user_id: UUID
    ) -> NotificationStats:
        """Get notification statistics for user."""
        # Total notifications
        total_statement = select(func.count()).select_from(
            select(Notification).where(
                Notification.user_id == user_id
            ).subquery()
        )
        total = db.exec(total_statement).one()
        
        # Unread notifications
        unread_statement = select(func.count()).select_from(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).subquery()
        )
        unread = db.exec(unread_statement).one()
        
        # By type
        type_stats = db.exec(
            select(Notification.type, func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .group_by(Notification.type)
        ).all()
        by_type = {str(t): c for t, c in type_stats}
        
        # By priority
        priority_stats = db.exec(
            select(Notification.priority, func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .group_by(Notification.priority)
        ).all()
        by_priority = {str(p): c for p, c in priority_stats}
        
        # Last notification
        last_notification = db.exec(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(1)
        ).first()
        
        return NotificationStats(
            total_notifications=total,
            unread_notifications=unread,
            by_type=by_type,
            by_priority=by_priority,
            last_notification_at=last_notification.created_at if last_notification else None
        )
    
    @staticmethod
    async def _should_send_email(
        preferences: NotificationPreference,
        notification: Notification
    ) -> bool:
        """Check if email should be sent based on preferences."""
        # Check type-specific preferences
        if notification.type.startswith("message_") and not preferences.message_notifications:
            return False
        if notification.type.startswith("forum_") and not preferences.forum_notifications:
            return False
        if notification.type.startswith("use_case_") and not preferences.use_case_notifications:
            return False
        if notification.type.startswith("system_") and not preferences.system_notifications:
            return False
        
        # Check quiet hours
        if preferences.quiet_hours_enabled:
            current_time = datetime.utcnow().strftime("%H:%M")
            if preferences.quiet_hours_start and preferences.quiet_hours_end:
                if preferences.quiet_hours_start <= current_time <= preferences.quiet_hours_end:
                    return False
        
        # Check frequency
        if preferences.email_frequency != "instant":
            return False  # Will be sent in digest
        
        return True
    
    @staticmethod
    async def _send_email_notification(
        db: Session,
        notification: Notification,
        preferences: NotificationPreference
    ) -> bool:
        """Send email notification."""
        try:
            # Get user
            user = db.get(User, notification.user_id)
            if not user or not user.email:
                return False
            
            # Get template
            template = db.exec(
                select(NotificationTemplate).where(
                    and_(
                        NotificationTemplate.type == notification.type,
                        NotificationTemplate.channel == NotificationChannel.EMAIL,
                        NotificationTemplate.is_active == True
                    )
                )
            ).first()
            
            if not template:
                # Use default template
                subject = notification.title
                body = notification.message
            else:
                # Process template
                subject = NotificationService._process_template(
                    template.subject_template or notification.title,
                    notification
                )
                body = NotificationService._process_template(
                    template.body_template,
                    notification
                )
            
            # Send email
            email_sent = await email_service.send_notification_email(
                to_email=user.email,
                subject=subject,
                body=body,
                notification_id=str(notification.id)
            )
            
            if email_sent:
                notification.email_sent = True
                notification.email_sent_at = datetime.utcnow()
                notification.delivered_channels.append(NotificationChannel.EMAIL)
                db.commit()
            
            return email_sent
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def _process_template(template: str, notification: Notification) -> str:
        """Process template variables."""
        result = template
        
        # Replace variables
        replacements = {
            "{{sender_name}}": notification.sender_name or "",
            "{{title}}": notification.title,
            "{{message}}": notification.message,
            "{{action_url}}": notification.action_url or "",
            "{{created_at}}": notification.created_at.strftime("%Y-%m-%d %H:%M")
        }
        
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        # Process metadata
        if notification.metadata:
            for key, value in notification.metadata.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
        
        return result
    
    @staticmethod
    async def cleanup_old_notifications(
        db: Session,
        days_to_keep: int = 30
    ) -> Dict[str, Any]:
        """Clean up old read notifications."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old read notifications
        statement = select(Notification).where(
            and_(
                Notification.is_read == True,
                Notification.created_at < cutoff_date
            )
        )
        old_notifications = db.exec(statement).all()
        
        for notification in old_notifications:
            db.delete(notification)
        
        db.commit()
        
        return {
            "message": f"Cleaned up {len(old_notifications)} old notifications",
            "deleted_count": len(old_notifications)
        }