"""Dashboard models and statistics schemas."""

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field
from uuid import UUID
from enum import Enum


class TimeRange(str, Enum):
    """Time range options for statistics."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class MetricType(str, Enum):
    """Types of metrics."""
    COUNT = "count"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    TOTAL = "total"
    GROWTH = "growth"


class EntityCount(SQLModel):
    """Count statistics for entities."""
    total: int = 0
    active: int = 0
    new_today: int = 0
    new_this_week: int = 0
    new_this_month: int = 0
    growth_rate: Optional[float] = None  # percentage change from previous period


class UserStatistics(SQLModel):
    """User-related statistics."""
    total_users: EntityCount = Field(default_factory=EntityCount)
    online_users: int = 0
    top_contributors: List[Dict[str, Any]] = []
    user_engagement: Dict[str, float] = {}  # activity metrics
    role_distribution: Dict[str, int] = {}


class ContentStatistics(SQLModel):
    """Content-related statistics."""
    forum_posts: EntityCount = Field(default_factory=EntityCount)
    forum_topics: EntityCount = Field(default_factory=EntityCount)
    use_cases: EntityCount = Field(default_factory=EntityCount)
    messages: EntityCount = Field(default_factory=EntityCount)
    popular_categories: List[Dict[str, Any]] = []
    content_engagement: Dict[str, float] = {}


class OrganizationStatistics(SQLModel):
    """Organization-specific statistics."""
    organization_id: UUID
    organization_name: str
    member_count: int = 0
    admin_count: int = 0
    activity_score: float = 0.0
    content_created: int = 0
    engagement_metrics: Dict[str, float] = {}


class SystemMetrics(SQLModel):
    """System performance metrics."""
    total_requests: int = 0
    api_response_time: float = 0.0  # milliseconds
    database_query_time: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    uptime_percentage: float = 100.0


class ActivityMetric(SQLModel):
    """Individual activity metric."""
    date: date
    metric_type: str
    value: float
    previous_value: Optional[float] = None
    change_percentage: Optional[float] = None


class TrendData(SQLModel):
    """Trend data over time."""
    period: TimeRange
    data_points: List[ActivityMetric] = []
    summary: Dict[str, Any] = {}


class DashboardStatistics(SQLModel):
    """Main dashboard statistics response."""
    organization_id: UUID
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_range: TimeRange = TimeRange.MONTH
    
    # Core statistics
    users: UserStatistics = Field(default_factory=UserStatistics)
    content: ContentStatistics = Field(default_factory=ContentStatistics)
    system: SystemMetrics = Field(default_factory=SystemMetrics)
    
    # Recent activity
    recent_activities: List[Dict[str, Any]] = []
    
    # Trending content
    trending_posts: List[Dict[str, Any]] = []
    trending_use_cases: List[Dict[str, Any]] = []
    
    # Performance indicators
    key_metrics: Dict[str, float] = {}


class ActivityFeedItem(SQLModel):
    """Activity feed item."""
    id: UUID
    type: str  # post_created, use_case_published, user_joined, etc.
    title: str
    description: str
    actor_name: str
    actor_id: UUID
    target_name: Optional[str] = None
    target_id: Optional[UUID] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ActivityFeedResponse(SQLModel):
    """Activity feed response."""
    activities: List[ActivityFeedItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class TrendingContent(SQLModel):
    """Trending content item."""
    id: UUID
    type: str  # forum_post, use_case, etc.
    title: str
    author_name: str
    author_id: UUID
    score: float  # trending score
    views: int = 0
    likes: int = 0
    comments: int = 0
    created_at: datetime
    trending_since: datetime


class TrendingContentResponse(SQLModel):
    """Trending content response."""
    content: List[TrendingContent]
    algorithm_info: Dict[str, Any] = {}
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_window: TimeRange = TimeRange.WEEK


class PerformanceMetrics(SQLModel):
    """Performance metrics."""
    api_metrics: Dict[str, float] = {}
    database_metrics: Dict[str, float] = {}
    cache_metrics: Dict[str, float] = {}
    error_metrics: Dict[str, float] = {}
    resource_usage: Dict[str, float] = {}


class AnalyticsQuery(SQLModel):
    """Query parameters for analytics."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    time_range: TimeRange = TimeRange.MONTH
    metrics: List[str] = []
    group_by: Optional[str] = None
    filter_by: Optional[Dict[str, Any]] = None


class AnalyticsResponse(SQLModel):
    """Analytics query response."""
    query: AnalyticsQuery
    data: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardConfig(SQLModel):
    """Dashboard configuration."""
    user_id: UUID
    organization_id: UUID
    default_time_range: TimeRange = TimeRange.MONTH
    visible_widgets: List[str] = []
    widget_positions: Dict[str, Dict[str, int]] = {}  # widget_id -> {x, y, w, h}
    refresh_interval: int = 300  # seconds
    notification_preferences: Dict[str, bool] = {}


class QuickStats(SQLModel):
    """Quick statistics for dashboard summary."""
    total_posts: int = 0
    total_users: int = 0
    total_use_cases: int = 0
    unread_messages: int = 0
    pending_tasks: int = 0
    recent_activity_count: int = 0