"""Message and conversation models for PostgreSQL."""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from enum import Enum


class MessageType(str, Enum):
    """Message content types."""
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    VIDEO = "video"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Message delivery status."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class ConversationBase(SQLModel):
    """Base conversation model."""
    organization_id: UUID
    participant1_id: UUID
    participant2_id: UUID
    
    # Last message cache (denormalized for performance)
    last_message_id: Optional[UUID] = None
    last_message_content: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_sender_id: Optional[UUID] = None
    
    # Unread counts (denormalized)
    participant1_unread_count: int = 0
    participant2_unread_count: int = 0
    
    # Status
    is_active: bool = True
    archived_by_participant1: bool = False
    archived_by_participant2: bool = False


class Conversation(ConversationBase, table=True):
    """Conversation model for database."""
    __tablename__ = "conversations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
    participant1: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Conversation.participant1_id==User.id",
            "foreign_keys": "[Conversation.participant1_id]"
        }
    )
    participant2: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Conversation.participant2_id==User.id",
            "foreign_keys": "[Conversation.participant2_id]"
        }
    )


class MessageBase(SQLModel):
    """Base message model."""
    conversation_id: UUID
    sender_id: UUID
    recipient_id: UUID
    organization_id: UUID
    
    # Content
    content: str
    content_type: MessageType = MessageType.TEXT
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None
    
    # Metadata for attachments, reactions, etc.
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type": "JSONB"})


class Message(MessageBase, table=True):
    """Message model for database."""
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Thread support
    parent_message_id: Optional[UUID] = None
    thread_count: int = 0
    
    # Delivery status
    status: MessageStatus = MessageStatus.SENT
    delivered_at: Optional[datetime] = None
    
    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
    attachments: list["MessageAttachment"] = Relationship(back_populates="message")
    sender: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Message.sender_id==User.id",
            "foreign_keys": "[Message.sender_id]"
        }
    )
    recipient: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Message.recipient_id==User.id",
            "foreign_keys": "[Message.recipient_id]"
        }
    )
    parent_message: Optional["Message"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Message.parent_message_id==Message.id",
            "remote_side": "[Message.id]",
            "foreign_keys": "[Message.parent_message_id]"
        }
    )
    replies: list["Message"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Message.id==Message.parent_message_id",
            "remote_side": "[Message.parent_message_id]"
        }
    )


class MessageAttachmentBase(SQLModel):
    """Base message attachment model."""
    message_id: UUID
    filename: str
    file_path: str
    file_url: Optional[str] = None
    file_size: int
    mime_type: str
    thumbnail_url: Optional[str] = None


class MessageAttachment(MessageAttachmentBase, table=True):
    """Message attachment model for database."""
    __tablename__ = "message_attachments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    message: Optional[Message] = Relationship(back_populates="attachments")


class MessageRead(SQLModel, table=True):
    """Track message read receipts."""
    __tablename__ = "message_reads"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID = Field(foreign_key="messages.id")
    user_id: UUID = Field(foreign_key="users.id")
    read_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Unique constraint
    class Config:
        unique_together = [["message_id", "user_id"]]


class MessageReaction(SQLModel, table=True):
    """Message reactions."""
    __tablename__ = "message_reactions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID = Field(foreign_key="messages.id")
    user_id: UUID = Field(foreign_key="users.id")
    reaction: str  # emoji or reaction type
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Unique constraint
    class Config:
        unique_together = [["message_id", "user_id", "reaction"]]


# Request/Response schemas
class MessageCreate(SQLModel):
    """Schema for creating a message."""
    recipient_id: UUID
    content: str
    content_type: MessageType = MessageType.TEXT
    parent_message_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageUpdate(SQLModel):
    """Schema for updating a message."""
    content: Optional[str] = None
    is_edited: bool = True


class MessageResponse(MessageBase):
    """Response schema for message."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: MessageStatus
    delivered_at: Optional[datetime]
    parent_message_id: Optional[UUID]
    thread_count: int
    sender_name: Optional[str] = None
    sender_title: Optional[str] = None
    sender_avatar: Optional[str] = None
    attachments: list[MessageAttachmentBase] = []
    reactions: list[Dict[str, Any]] = []


class ConversationCreate(SQLModel):
    """Schema for creating a conversation."""
    participant_id: UUID  # The other participant


class ConversationResponse(ConversationBase):
    """Response schema for conversation."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    participant_name: Optional[str] = None
    participant_title: Optional[str] = None
    participant_avatar: Optional[str] = None
    unread_count: int = 0
    last_message: Optional[MessageResponse] = None


class ConversationListResponse(SQLModel):
    """Response for conversation list."""
    conversations: list[ConversationResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class MessageListResponse(SQLModel):
    """Response for message list."""
    messages: list[MessageResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class UnreadCountResponse(SQLModel):
    """Response for unread message count."""
    total_unread: int
    conversations_with_unread: int
    by_conversation: Dict[str, int] = {}


class MessageSearchRequest(SQLModel):
    """Request for searching messages."""
    query: str
    conversation_id: Optional[UUID] = None
    sender_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    content_type: Optional[MessageType] = None
    limit: int = 20