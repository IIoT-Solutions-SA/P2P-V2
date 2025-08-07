"""MongoDB document models for Use Cases."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum


class UseCaseCategory(str, Enum):
    """Use case categories matching frontend."""
    AUTOMATION = "automation"
    QUALITY = "quality"
    MAINTENANCE = "maintenance"
    EFFICIENCY = "efficiency"
    INNOVATION = "innovation"
    SUSTAINABILITY = "sustainability"


class UseCaseStatus(str, Enum):
    """Use case status states."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"


class UseCaseVisibility(str, Enum):
    """Use case visibility levels."""
    PUBLIC = "public"
    ORGANIZATION = "organization"
    PRIVATE = "private"


class MediaType(str, Enum):
    """Media file types."""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    PRESENTATION = "presentation"


class Metric(BaseModel):
    """Individual metric within results."""
    name: str
    value: str
    baseline: Optional[str] = None
    current: Optional[str] = None
    improvement_percentage: Optional[float] = None
    period: Optional[str] = None
    details: Optional[str] = None


class ROI(BaseModel):
    """Return on investment details."""
    percentage: Optional[float] = None
    payback_period: Optional[str] = None
    total_investment: Optional[str] = None
    annual_return: Optional[str] = None


class Results(BaseModel):
    """Use case results and metrics."""
    metrics: List[Metric] = []
    roi: Optional[ROI] = None
    timeframe: Optional[str] = None
    key_metric: Optional[str] = None  # For list display


class ImplementationPhase(BaseModel):
    """Implementation phase details."""
    phase: int
    title: str
    duration: str
    description: Optional[str] = None


class Implementation(BaseModel):
    """Implementation details."""
    timeline: Optional[str] = None
    phases: List[ImplementationPhase] = []
    team_size: Optional[int] = None
    budget_range: Optional[str] = None


class Vendor(BaseModel):
    """Vendor/supplier information."""
    name: str
    product: Optional[str] = None
    category: Optional[str] = None


class Media(BaseModel):
    """Media attachment details."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MediaType
    filename: str
    path: str
    thumbnail_path: Optional[str] = None
    size: int
    mime_type: str
    caption: Optional[str] = None
    order: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Location(BaseModel):
    """Location information."""
    city: Optional[str] = None
    region: Optional[str] = None
    country: str = "Saudi Arabia"
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 24.7136, "lng": 46.6753}


class PublishedBy(BaseModel):
    """Publisher information."""
    user_id: str
    name: str
    title: Optional[str] = None
    email: Optional[str] = None  # Hidden in public API


class Metrics(BaseModel):
    """Engagement metrics."""
    views: int = 0
    unique_views: int = 0
    likes: int = 0
    saves: int = 0
    shares: int = 0
    inquiries: int = 0
    avg_time_on_page: Optional[int] = None  # seconds


class Verification(BaseModel):
    """Verification details."""
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None


class Featured(BaseModel):
    """Featured status details."""
    is_featured: bool = False
    featured_until: Optional[datetime] = None
    featured_by: Optional[str] = None


class UseCase(BaseModel):
    """Main Use Case document model for MongoDB."""
    
    # Identifiers
    id: str = Field(default_factory=lambda: str(uuid4()))
    organization_id: str
    
    # Basic Information
    title: str
    company: str
    industry: str
    category: UseCaseCategory
    
    # Detailed Content
    description: str
    challenge: Optional[str] = None
    solution: Optional[str] = None
    implementation: Optional[Implementation] = None
    
    # Results & Metrics
    results: Results
    
    # Technologies & Tools
    technologies: List[str] = []
    vendors: List[Vendor] = []
    
    # Media & Attachments
    media: List[Media] = []
    
    # Location
    location: Optional[Location] = None
    
    # Publishing & Status
    status: UseCaseStatus = UseCaseStatus.DRAFT
    visibility: UseCaseVisibility = UseCaseVisibility.ORGANIZATION
    published_by: PublishedBy
    
    # Engagement Metrics
    metrics: Metrics = Field(default_factory=Metrics)
    
    # Verification & Features
    verification: Verification = Field(default_factory=Verification)
    featured: Featured = Field(default_factory=Featured)
    
    # Tags & Categorization
    tags: List[str] = []
    
    # Related Content
    related_use_cases: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None  # Soft delete
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UseCaseDraft(BaseModel):
    """Draft use case for multi-step form."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    use_case_id: Optional[str] = None
    user_id: str
    organization_id: str
    draft_data: Dict[str, Any]  # Partial UseCase data
    current_step: int = 1
    total_steps: int = 5
    last_saved: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # Auto-cleanup after 30 days
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UseCaseView(BaseModel):
    """Track use case views for analytics."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    use_case_id: str
    viewer_id: Optional[str] = None  # None for anonymous
    organization_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    time_on_page: Optional[int] = None  # seconds
    actions: List[str] = []  # ["viewed", "liked", "saved"]
    viewed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UseCaseLike(BaseModel):
    """Track use case likes."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    use_case_id: str
    user_id: str
    organization_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UseCaseSave(BaseModel):
    """Track use case saves/bookmarks."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    use_case_id: str
    user_id: str
    organization_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }