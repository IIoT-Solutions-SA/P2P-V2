"""Forum schemas for API requests and responses."""

from typing import List, Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import ForumCategoryType


# Forum Category Schemas

class ForumCategoryBase(BaseModel):
    """Base forum category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category_type: ForumCategoryType
    color_class: str = Field(default="bg-gray-100", max_length=50)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)


class ForumCategoryCreate(ForumCategoryBase):
    """Schema for creating a forum category."""
    pass


class ForumCategoryUpdate(BaseModel):
    """Schema for updating a forum category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color_class: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ForumCategoryResponse(ForumCategoryBase):
    """Schema for forum category responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    topics_count: int
    posts_count: int
    created_at: datetime
    updated_at: datetime


# Forum Topic Schemas

class ForumTopicBase(BaseModel):
    """Base forum topic schema."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: str = Field(..., min_length=1, max_length=300)
    category_id: UUID
    is_pinned: bool = Field(default=False)


class ForumTopicCreate(ForumTopicBase):
    """Schema for creating a forum topic."""
    pass


class ForumTopicUpdate(BaseModel):
    """Schema for updating a forum topic."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, min_length=1, max_length=300)
    category_id: Optional[UUID] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class ForumTopicAuthor(BaseModel):
    """Schema for topic author information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    first_name: str
    last_name: str
    email: str
    job_title: Optional[str]
    is_verified: bool = Field(default=True)  # Based on email_verified
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
        
    @property 
    def author_title(self) -> str:
        """Get formatted author title for frontend."""
        if self.job_title:
            return f"{self.job_title}"
        return "Member"


class ForumTopicResponse(ForumTopicBase):
    """Schema for forum topic responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    author_id: UUID
    organization_id: UUID
    
    # Topic properties
    is_locked: bool
    has_best_answer: bool
    best_answer_post_id: Optional[UUID]
    
    # Statistics
    views_count: int
    posts_count: int  # This is replies count in frontend
    likes_count: int
    
    # Activity tracking
    last_activity_at: datetime
    last_post_id: Optional[UUID]
    last_post_author_id: Optional[UUID]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Related data (populated by service layer)
    author: Optional[ForumTopicAuthor] = None
    category: Optional[ForumCategoryResponse] = None
    
    @property
    def time_ago(self) -> str:
        """Get human-readable time ago for frontend compatibility."""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} days ago" if diff.days > 1 else "1 day ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago" if hours > 1 else "1 hour ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago" if minutes > 1 else "1 minute ago"
        else:
            return "Just now"


class ForumTopicListResponse(BaseModel):
    """Schema for paginated forum topic list responses."""
    topics: List[ForumTopicResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# Forum Topic Search and Filter Schemas

class ForumTopicFilters(BaseModel):
    """Schema for forum topic filtering."""
    category_id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    is_pinned: Optional[bool] = None
    has_best_answer: Optional[bool] = None
    search_query: Optional[str] = Field(None, max_length=200)


class ForumTopicSearchQuery(BaseModel):
    """Schema for forum topic search parameters."""
    # Search and filters
    search: Optional[str] = Field(None, max_length=200, description="Search in title, content, and excerpt")
    category_id: Optional[UUID] = Field(None, description="Filter by category")
    author_id: Optional[UUID] = Field(None, description="Filter by author")
    is_pinned: Optional[bool] = Field(None, description="Filter pinned topics")
    has_best_answer: Optional[bool] = Field(None, description="Filter topics with best answers")
    
    # Sorting
    sort_by: str = Field(default="last_activity_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


# Forum Post Schemas (for basic replies)

class ForumPostBase(BaseModel):
    """Base forum post schema."""
    content: str = Field(..., min_length=1)
    topic_id: UUID
    parent_post_id: Optional[UUID] = None


class ForumPostCreate(ForumPostBase):
    """Schema for creating a forum post."""
    pass


class ForumPostUpdate(BaseModel):
    """Schema for updating a forum post."""
    content: Optional[str] = Field(None, min_length=1)


class ForumPostResponse(ForumPostBase):
    """Schema for forum post responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    author_id: UUID
    organization_id: UUID
    
    # Post properties
    is_best_answer: bool
    is_deleted: bool
    edited_at: Optional[datetime]
    
    # Statistics
    likes_count: int
    replies_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Related data (populated by service layer)
    author: Optional[ForumTopicAuthor] = None
    replies: Optional[List["ForumPostResponse"]] = None


# Statistics and Analytics Schemas

class ForumStatsResponse(BaseModel):
    """Schema for forum statistics."""
    total_topics: int
    total_posts: int
    active_members: int
    helpful_answers: int
    categories: List[ForumCategoryResponse]


class TopContributorResponse(BaseModel):
    """Schema for top contributor information."""
    user_id: UUID
    name: str
    points: int
    topics_count: int
    posts_count: int
    best_answers_count: int


# Like/Unlike Schemas

class ForumLikeResponse(BaseModel):
    """Schema for like/unlike responses."""
    success: bool
    liked: bool
    likes_count: int
    message: str


# Search Schemas

class ForumSearchQuery(BaseModel):
    """Schema for comprehensive forum search."""
    q: str = Field(..., min_length=2, max_length=200, description="Search query")
    search_in: Optional[str] = Field("all", pattern="^(all|topics|posts)$", description="Search scope")
    category_id: Optional[UUID] = Field(None, description="Filter by category")
    author_id: Optional[UUID] = Field(None, description="Filter by author")
    date_from: Optional[datetime] = Field(None, description="Filter by date from")
    date_to: Optional[datetime] = Field(None, description="Filter by date to")
    sort_by: Optional[str] = Field("relevance", pattern="^(relevance|date|likes)$")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class ForumSearchResult(BaseModel):
    """Schema for individual search result."""
    id: UUID
    type: str = Field(..., pattern="^(topic|post)$")
    title: Optional[str] = None  # For topics
    content: str
    excerpt: str
    author: ForumTopicAuthor
    category: Optional[ForumCategoryResponse] = None
    topic_id: Optional[UUID] = None  # For posts
    topic_title: Optional[str] = None  # For posts
    likes_count: int = 0
    replies_count: int = 0
    created_at: datetime
    highlight: Optional[str] = None  # Highlighted search match


class ForumSearchResponse(BaseModel):
    """Schema for forum search response."""
    results: List[ForumSearchResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    search_query: str
    search_time_ms: Optional[int] = None


# Bulk Operations

class ForumTopicBulkUpdate(BaseModel):
    """Schema for bulk topic operations."""
    topic_ids: List[UUID] = Field(..., min_items=1, max_items=50)
    action: str = Field(..., pattern="^(pin|unpin|lock|unlock|delete)$")


class ForumTopicBulkResponse(BaseModel):
    """Schema for bulk operation responses."""
    success: bool
    updated_count: int
    failed_ids: List[UUID] = []
    message: str