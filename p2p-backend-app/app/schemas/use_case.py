"""Pydantic schemas for Use Case API requests and responses."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from app.models.use_case import (
    UseCaseCategory,
    UseCaseStatus,
    UseCaseVisibility,
    MediaType,
    Metric,
    ROI,
    Results,
    Implementation,
    Vendor,
    Media,
    Location,
    PublishedBy,
    Metrics as UseCaseMetrics,
    Verification,
    Featured
)


# Request Schemas

class MetricCreate(BaseModel):
    """Create a new metric."""
    name: str
    value: str
    baseline: Optional[str] = None
    current: Optional[str] = None
    improvement_percentage: Optional[float] = None
    period: Optional[str] = None
    details: Optional[str] = None


class ROICreate(BaseModel):
    """Create ROI details."""
    percentage: Optional[float] = None
    payback_period: Optional[str] = None
    total_investment: Optional[str] = None
    annual_return: Optional[str] = None


class ResultsCreate(BaseModel):
    """Create results section."""
    metrics: List[MetricCreate] = []
    roi: Optional[ROICreate] = None
    timeframe: Optional[str] = None


class ImplementationPhaseCreate(BaseModel):
    """Create implementation phase."""
    phase: int
    title: str
    duration: str
    description: Optional[str] = None


class ImplementationCreate(BaseModel):
    """Create implementation details."""
    timeline: Optional[str] = None
    phases: List[ImplementationPhaseCreate] = []
    team_size: Optional[int] = None
    budget_range: Optional[str] = None


class VendorCreate(BaseModel):
    """Create vendor information."""
    name: str
    product: Optional[str] = None
    category: Optional[str] = None


class LocationCreate(BaseModel):
    """Create location information."""
    city: Optional[str] = None
    region: Optional[str] = None
    country: str = "Saudi Arabia"
    coordinates: Optional[Dict[str, float]] = None


class UseCaseCreate(BaseModel):
    """Create a new use case."""
    # Basic Information
    title: str = Field(..., min_length=10, max_length=200)
    company: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=100)
    category: UseCaseCategory
    
    # Detailed Content
    description: str = Field(..., min_length=50, max_length=5000)
    challenge: Optional[str] = Field(None, max_length=3000)
    solution: Optional[str] = Field(None, max_length=5000)
    implementation: Optional[ImplementationCreate] = None
    
    # Results & Metrics
    results: ResultsCreate
    
    # Technologies & Tools
    technologies: List[str] = Field(default=[], max_length=20)
    vendors: List[VendorCreate] = []
    
    # Location
    location: Optional[LocationCreate] = None
    
    # Publishing & Status
    status: UseCaseStatus = UseCaseStatus.DRAFT
    visibility: UseCaseVisibility = UseCaseVisibility.ORGANIZATION
    
    # Tags
    tags: List[str] = Field(default=[], max_length=20)
    
    @field_validator('tags', 'technologies')
    def validate_list_items(cls, v):
        """Validate list items are not empty."""
        if v:
            return [item.strip() for item in v if item.strip()]
        return v


class UseCaseUpdate(BaseModel):
    """Update an existing use case."""
    # Basic Information
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    industry: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[UseCaseCategory] = None
    
    # Detailed Content
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    challenge: Optional[str] = Field(None, max_length=3000)
    solution: Optional[str] = Field(None, max_length=5000)
    implementation: Optional[ImplementationCreate] = None
    
    # Results & Metrics
    results: Optional[ResultsCreate] = None
    
    # Technologies & Tools
    technologies: Optional[List[str]] = Field(None, max_length=20)
    vendors: Optional[List[VendorCreate]] = None
    
    # Location
    location: Optional[LocationCreate] = None
    
    # Publishing & Status
    status: Optional[UseCaseStatus] = None
    visibility: Optional[UseCaseVisibility] = None
    
    # Tags
    tags: Optional[List[str]] = Field(None, max_length=20)


class DraftSave(BaseModel):
    """Save a draft use case."""
    use_case_id: Optional[str] = None
    draft_data: Dict[str, Any]
    current_step: int = Field(..., ge=1, le=5)


class MediaUpload(BaseModel):
    """Media upload response."""
    media_id: str
    url: str
    thumbnail_url: Optional[str] = None
    type: MediaType
    size: int
    filename: str


# Response Schemas

class UseCaseBrief(BaseModel):
    """Brief use case for list views."""
    id: str
    title: str
    company: str
    industry: str
    category: UseCaseCategory
    description: str
    results: Dict[str, Any]  # Simplified results
    thumbnail: Optional[str] = None
    tags: List[str]
    verified: bool
    featured: bool
    views: int
    likes: int
    published_by: Dict[str, str]  # Simplified publisher
    published_at: Optional[datetime]


class UseCaseDetail(BaseModel):
    """Detailed use case for full view."""
    id: str
    title: str
    company: str
    industry: str
    category: UseCaseCategory
    description: str
    challenge: Optional[str]
    solution: Optional[str]
    implementation: Optional[Implementation]
    results: Results
    technologies: List[str]
    vendors: List[Vendor]
    media: List[Media]
    location: Optional[Location]
    status: UseCaseStatus
    visibility: UseCaseVisibility
    published_by: Dict[str, str]  # Email excluded
    metrics: UseCaseMetrics
    verification: Verification
    featured: Featured
    tags: List[str]
    related_use_cases: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]


class UseCaseResponse(BaseModel):
    """Standard use case response."""
    id: str
    title: str
    status: UseCaseStatus
    created_at: datetime
    message: Optional[str] = None


class UseCaseListResponse(BaseModel):
    """Paginated use case list response."""
    data: List[UseCaseBrief]
    pagination: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


class UseCaseSearchResponse(BaseModel):
    """Search results response."""
    data: List[UseCaseBrief]
    search_metadata: Dict[str, Any]
    pagination: Dict[str, Any]


class DraftResponse(BaseModel):
    """Draft save response."""
    draft_id: str
    use_case_id: Optional[str]
    saved_at: datetime
    expires_at: datetime


class LikeResponse(BaseModel):
    """Like/unlike response."""
    liked: bool
    total_likes: int


class SaveResponse(BaseModel):
    """Save/unsave response."""
    saved: bool
    total_saves: int


class ExportResponse(BaseModel):
    """Export response."""
    export_url: str
    expires_at: datetime
    format: str
    total_items: int


class SuggestionsResponse(BaseModel):
    """Search suggestions response."""
    suggestions: List[str]
    query: str


class TrendingResponse(BaseModel):
    """Trending use cases response."""
    trending: List[Dict[str, Any]]
    period: str


# Query Parameters

class UseCaseFilters(BaseModel):
    """Filters for browsing use cases."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    category: Optional[UseCaseCategory] = None
    industry: Optional[str] = None
    technologies: Optional[List[str]] = None
    verified: Optional[bool] = None
    featured: Optional[bool] = None
    sort_by: Optional[str] = Field(
        default="date",
        pattern="^(date|views|likes|roi)$"
    )
    order: Optional[str] = Field(
        default="desc",
        pattern="^(asc|desc)$"
    )
    search: Optional[str] = Field(None, min_length=2, max_length=200)


class UseCaseSearch(BaseModel):
    """Search parameters."""
    q: str = Field(..., min_length=2, max_length=200)
    fields: Optional[List[str]] = Field(
        default=["title", "description", "solution", "tags"]
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ExportRequest(BaseModel):
    """Export request parameters."""
    format: str = Field(..., pattern="^(pdf|excel|csv)$")
    ids: Optional[List[str]] = None
    filters: Optional[UseCaseFilters] = None