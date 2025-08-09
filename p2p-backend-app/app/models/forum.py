from datetime import datetime
from typing import List, Optional
import uuid as uuid_lib
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, Text, ForeignKey
from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

from app.models.base import BaseModel
from app.models.user import User
from app.models.enums import ForumCategoryType


class ForumCategory(BaseModel, table=True):
    """Forum category for organizing topics."""
    
    __tablename__ = "forum_categories"
    
    name: str = Field(max_length=100, nullable=False, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    category_type: ForumCategoryType = Field(nullable=False)
    color_class: str = Field(max_length=50, default="bg-gray-100")
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    
    # Statistics (computed)
    topics_count: int = Field(default=0, description="Cached count of topics")
    posts_count: int = Field(default=0, description="Cached count of posts")
    
    # Relationships
    topics: List["ForumTopic"] = Relationship(back_populates="category")
    
    __table_args__ = (
        Index("ix_forum_categories_active_sort", "is_active", "sort_order"),
    )


class ForumTopic(BaseModel, table=True):
    """Forum topic (main discussion thread)."""
    
    __tablename__ = "forum_topics"
    
    title: str = Field(max_length=200, nullable=False, index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    excerpt: str = Field(max_length=300, nullable=False)
    
    # Foreign keys
    author_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    )
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    )
    category_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_categories.id"), nullable=False, index=True)
    )
    
    # Topic properties
    is_pinned: bool = Field(default=False)
    is_locked: bool = Field(default=False)
    has_best_answer: bool = Field(default=False)
    best_answer_post_id: Optional[uuid_lib.UUID] = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), default=None)
    )
    
    # Statistics (cached for performance)
    views_count: int = Field(default=0)
    posts_count: int = Field(default=0)
    likes_count: int = Field(default=0)
    
    # Activity tracking
    last_activity_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    last_post_id: Optional[uuid_lib.UUID] = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), default=None)
    )
    last_post_author_id: Optional[uuid_lib.UUID] = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("users.id"), default=None, index=True)
    )
    
    # Relationships
    author: User = Relationship(
        back_populates="forum_topics",
        sa_relationship_kwargs={"foreign_keys": "[ForumTopic.author_id]"}
    )
    category: ForumCategory = Relationship(back_populates="topics")
    posts: List["ForumPost"] = Relationship(
        back_populates="topic",
        sa_relationship_kwargs={
            "foreign_keys": "[ForumPost.topic_id]",
            "cascade": "all, delete-orphan"
        }
    )
    likes: List["ForumTopicLike"] = Relationship(
        back_populates="topic",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    views: List["ForumTopicView"] = Relationship(
        back_populates="topic",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    # Self-referential for best answer
    best_answer_post: Optional["ForumPost"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ForumTopic.best_answer_post_id]",
            "post_update": True
        }
    )
    last_post: Optional["ForumPost"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ForumTopic.last_post_id]",
            "post_update": True
        }
    )
    last_post_author: Optional[User] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ForumTopic.last_post_author_id]",
            "post_update": True
        }
    )
    
    __table_args__ = (
        Index("ix_forum_topics_org_category", "organization_id", "category_id"),
        Index("ix_forum_topics_activity", "last_activity_at"),
        Index("ix_forum_topics_pinned", "is_pinned", "last_activity_at"),
        Index("ix_forum_topics_author_org", "author_id", "organization_id"),
    )


class ForumPost(BaseModel, table=True):
    """Forum post (reply to a topic)."""
    
    __tablename__ = "forum_posts"
    
    content: str = Field(sa_column=Column(Text, nullable=False))
    
    # Foreign keys
    topic_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_topics.id"), nullable=False, index=True)
    )
    author_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    )
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    )
    parent_post_id: Optional[uuid_lib.UUID] = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), default=None, index=True)
    )
    
    # Post properties
    is_best_answer: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    edited_at: Optional[datetime] = Field(default=None)
    
    # Statistics
    likes_count: int = Field(default=0)
    replies_count: int = Field(default=0)
    
    # Relationships
    topic: ForumTopic = Relationship(
        back_populates="posts",
        sa_relationship_kwargs={"foreign_keys": "[ForumPost.topic_id]"}
    )
    author: User = Relationship(
        back_populates="forum_posts",
        sa_relationship_kwargs={"foreign_keys": "[ForumPost.author_id]"}
    )
    parent_post: Optional["ForumPost"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={
            "foreign_keys": "[ForumPost.parent_post_id]",
            "remote_side": "[ForumPost.id]"
        }
    )
    replies: List["ForumPost"] = Relationship(
        back_populates="parent_post",
        sa_relationship_kwargs={
            "foreign_keys": "[ForumPost.parent_post_id]",
            "cascade": "all, delete-orphan"
        }
    )
    likes: List["ForumPostLike"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    __table_args__ = (
        Index("ix_forum_posts_topic_parent", "topic_id", "parent_post_id"),
        Index("ix_forum_posts_author_org", "author_id", "organization_id"),
        Index("ix_forum_posts_best_answer", "topic_id", "is_best_answer"),
        Index("ix_forum_posts_created", "created_at"),
    )


class ForumTopicLike(BaseModel, table=True):
    """User likes for forum topics."""
    
    __tablename__ = "forum_topic_likes"
    
    # Foreign keys
    topic_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_topics.id"), nullable=False, index=True)
    )
    user_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    )
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    )
    
    # Relationships
    topic: ForumTopic = Relationship(back_populates="likes")
    user: User = Relationship()
    
    __table_args__ = (
        Index("ix_forum_topic_likes_unique", "topic_id", "user_id", unique=True),
        Index("ix_forum_topic_likes_user", "user_id"),
    )


class ForumPostLike(BaseModel, table=True):
    """User likes for forum posts."""
    
    __tablename__ = "forum_post_likes"
    
    # Foreign keys
    post_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_posts.id"), nullable=False, index=True)
    )
    user_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    )
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    )
    
    # Relationships
    post: ForumPost = Relationship(back_populates="likes")
    user: User = Relationship()
    
    __table_args__ = (
        Index("ix_forum_post_likes_unique", "post_id", "user_id", unique=True),
        Index("ix_forum_post_likes_user", "user_id"),
    )


class ForumTopicView(BaseModel, table=True):
    """Track topic views for analytics."""
    
    __tablename__ = "forum_topic_views"
    
    # Foreign keys
    topic_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("forum_topics.id"), nullable=False, index=True)
    )
    user_id: Optional[uuid_lib.UUID] = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("users.id"), default=None, index=True)
    )
    organization_id: uuid_lib.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    )
    
    # View tracking
    ip_address: Optional[str] = Field(max_length=45, default=None)
    user_agent: Optional[str] = Field(max_length=500, default=None)
    
    # Relationships
    topic: ForumTopic = Relationship(back_populates="views")
    user: Optional[User] = Relationship()
    
    __table_args__ = (
        Index("ix_forum_topic_views_topic_user", "topic_id", "user_id"),
        Index("ix_forum_topic_views_created", "created_at"),
    )