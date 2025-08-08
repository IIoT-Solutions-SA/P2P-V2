"""Notification models for PostgreSQL."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications."""
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_READ = "message_read"
    FORUM_REPLY = "forum_reply"
    FORUM_MENTION = "forum_mention"
    USE_CASE_APPROVED = "use_case_approved"
    USE_CASE_FEATURED = "use_case_featured"
    ORGANIZATION_INVITE = "organization_invite"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationBase(SQLModel):
    """Base notification model."""
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    
    # Related entities
    related_entity_type: Optional[str] = None  # message, forum_post, use_case, etc.
    related_entity_id: Optional[UUID] = None
    
    # Sender info
    sender_id: Optional[UUID] = None
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type": "JSONB"})
    action_url: Optional[str] = None  # URL to navigate to when clicked


class Notification(NotificationBase, table=True):
    """Notification model for database."""
    __tablename__ = "notifications"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Delivery status
    delivered_channels: List[NotificationChannel] = Field(default=[], sa_column_kwargs={"type": "ARRAY"})
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    sms_sent: bool = False
    sms_sent_at: Optional[datetime] = None
    push_sent: bool = False
    push_sent_at: Optional[datetime] = None
    
    # Expiry
    expires_at: Optional[datetime] = None
    is_expired: bool = False


class NotificationPreferenceBase(SQLModel):
    """Base notification preference model."""
    user_id: UUID
    
    # Global settings
    enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = False
    
    # Type-specific preferences
    message_notifications: bool = True
    forum_notifications: bool = True
    use_case_notifications: bool = True
    system_notifications: bool = True
    
    # Frequency settings
    email_frequency: str = "instant"  # instant, daily, weekly
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None  # "08:00"
    
    # Email digest preferences
    daily_digest: bool = False
    weekly_digest: bool = False
    digest_time: Optional[str] = None  # "09:00"
    digest_day: Optional[int] = None  # 1=Monday, 7=Sunday


class NotificationPreference(NotificationPreferenceBase, table=True):
    """Notification preference model for database."""
    __tablename__ = "notification_preferences"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Unique constraint on user_id
    class Config:
        unique_together = [["user_id"]]


class NotificationTemplate(SQLModel, table=True):
    """Email/SMS notification templates."""
    __tablename__ = "notification_templates"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: NotificationType
    channel: NotificationChannel
    language: str = "en"
    
    # Template content
    subject_template: Optional[str] = None  # For emails
    body_template: str  # Supports variables like {{sender_name}}
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Unique constraint
    class Config:
        unique_together = [["type", "channel", "language"]]


# Request/Response schemas
class NotificationCreate(SQLModel):
    """Schema for creating a notification."""
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    sender_id: Optional[UUID] = None
    sender_name: Optional[str] = None
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase):
    """Response schema for notification."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    delivered_channels: List[NotificationChannel]


class NotificationListResponse(SQLModel):
    """Response for notification list."""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    has_more: bool


class NotificationMarkReadRequest(SQLModel):
    """Request to mark notifications as read."""
    notification_ids: List[UUID]


class NotificationPreferenceUpdate(SQLModel):
    """Schema for updating notification preferences."""
    enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    message_notifications: Optional[bool] = None
    forum_notifications: Optional[bool] = None
    use_case_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    email_frequency: Optional[str] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    daily_digest: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    digest_time: Optional[str] = None
    digest_day: Optional[int] = None


class NotificationStats(SQLModel):
    """Notification statistics."""
    total_notifications: int = 0
    unread_notifications: int = 0
    by_type: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    last_notification_at: Optional[datetime] = None