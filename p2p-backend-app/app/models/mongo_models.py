# File: app/models/mongo_models.py

from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
import pymongo

class User(Document):
    email: EmailStr
    name: str
    organization_id: Optional[str] = None
    industry_sector: Optional[str] = None
    location: Optional[str] = None
    expertise_tags: List[str] = Field(default_factory=list)
    verified: bool = False
    company: Optional[str] = None
    title: Optional[str] = None
    role: str = "user"
    language_preference: str = "en"
    profile_picture_url: Optional[str] = None  # S3 URL for profile picture
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "users"
        indexes = [
            [("email", pymongo.ASCENDING)],
        ]

class Organization(Document):
    name: str
    domain: Optional[str] = None
    industry_sector: Optional[str] = None
    size: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "organizations"
        indexes = [
            [("domain", pymongo.ASCENDING)],
            [("name", pymongo.ASCENDING)],
        ]

class ForumPost(Document):
    author_id: str
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    attachments: List[Dict] = Field(default_factory=list)  # [{"url": "...", "filename": "...", "type": "image/jpeg", "size": 123456}]
    best_answer_id: Optional[str] = None
    status: str = "open"
    view_count: int = 0
    views: int = 0
    reply_count: int = 0
    upvotes: int = 0
    liked_by: List[str] = Field(default_factory=list)
    is_pinned: bool = False
    has_best_answer: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    class Settings:
        name = "forum_posts"
        indexes = [
            [("category", pymongo.ASCENDING)],
            [("tags", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]

class ForumReply(Document):
    post_id: str
    author_id: str
    content: str
    parent_reply_id: Optional[str] = None
    attachments: List[Dict] = Field(default_factory=list)  # [{"url": "...", "filename": "...", "type": "image/jpeg", "size": 123456}]
    upvotes: int = 0
    liked_by: List[str] = Field(default_factory=list)
    is_best_answer: bool = False
    status: str = "published"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    class Settings:
        name = "forum_replies"
        indexes = [
            [("post_id", pymongo.ASCENDING)],
            [("parent_reply_id", pymongo.ASCENDING)],
            [("created_at", pymongo.ASCENDING)]
        ]

class UserActivity(Document):
    user_id: str
    activity_type: str
    target_id: str
    target_title: Optional[str] = None
    target_category: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "user_activities"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("activity_type", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]

class UserStats(Document):
    user_id: Indexed(str, unique=True)
    questions_asked: int = 0
    answers_given: int = 0
    best_answers: int = 0
    use_cases_submitted: int = 0
    bookmarks_saved: int = 0
    total_upvotes_received: int = 0
    reputation_score: int = 0
    activity_level: float = 0.0
    connections_count: int = 0
    draft_posts: int = 0
    last_calculated: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "user_stats"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("reputation_score", pymongo.DESCENDING)]
        ]

class UserBookmark(Document):
    user_id: str
    target_type: str
    target_id: str
    target_title: str
    target_category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "user_bookmarks"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("target_type", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]

class DraftPost(Document):
    user_id: str
    title: str
    content: str
    post_type: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "draft_posts"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("post_type", pymongo.ASCENDING)],
            [("updated_at", pymongo.DESCENDING)]
        ]

class UseCase(Document):
    # Basic Information
    submitted_by: str
    title: str
    problem_statement: str
    solution_description: str
    vendor_info: Optional[Dict[str, str]] = None
    cost_estimate: Optional[str] = None
    impact_metrics: Dict[str, str] = Field(default_factory=dict)
    industry_tags: List[str] = Field(default_factory=list)
    region: Optional[str] = None
    location: Dict[str, float]
    bookmarks: List[str] = Field(default_factory=list)
    published: bool = False
    featured: bool = False
    title_slug: Optional[str] = Field(default=None, index=True)
    company_slug: Optional[str] = Field(default=None, index=True)
    organization_name: Optional[str] = None  # Canonical display name; slugs remain lowercase identifiers only

    # Simplified submission fields (canonical contributor answers)
    problem: Optional[str] = None
    technology: Optional[str] = None
    budget: Optional[str] = None
    outcomes: Optional[str] = None
    challenges: Optional[str] = None

    # Detailed Information
    subtitle: Optional[str] = None
    description_long: Optional[str] = None
    category: Optional[str] = None
    factory_name: Optional[str] = None
    implementation_time: Optional[str] = None
    roi_percentage: Optional[str] = None

    # Contact & Metadata
    contact_person: Optional[str] = None
    contact_title: Optional[str] = None
    images: List[str] = Field(default_factory=list)  # S3 URLs for images
    videos: List[Dict[str, str]] = Field(default_factory=list)  # [{"url": "...", "thumbnail": "...", "filename": "..."}]

    # Rich Content Sections
    executive_summary: Optional[str] = None
    business_challenge: Optional[Dict[str, Any]] = None
    solution_details: Optional[Dict[str, Any]] = None
    implementation_details: Optional[Dict[str, Any]] = None
    challenges_and_solutions: List[Dict[str, str]] = Field(default_factory=list)
    results: Optional[Dict[str, Any]] = None
    technical_architecture: Optional[Dict[str, Any]] = None
    future_roadmap: List[Dict[str, str]] = Field(default_factory=list)
    lessons_learned: List[Dict[str, str]] = Field(default_factory=list)

    # Additional Metadata
    published_date: Optional[str] = None
    last_updated: Optional[str] = None
    read_time: Optional[str] = None
    views: int = 0
    downloads: int = 0
    status: str = "draft"
    verified_by: Optional[str] = None
    technology_tags: List[str] = Field(default_factory=list)

    # Linking Fields
    detailed_version_id: Optional[str] = None
    basic_version_id: Optional[str] = None
    has_detailed_view: bool = False
    is_detailed_version: bool = False

    # Timestamps & Interaction
    view_count: int = 0
    like_count: int = 0
    bookmark_count: int = 0
    liked_by: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None

    class Settings:
        name = "use_cases"
        indexes = [
            [("industry_tags", pymongo.ASCENDING)],
            [("region", pymongo.ASCENDING)],
            [("location", pymongo.GEO2D)],
            [("title", pymongo.TEXT)]
        ]

class UseCaseDraft(Document):
    """Model for Use Case drafts - mirrors UseCase model with all Optional fields"""
    # Draft Ownership & Metadata
    user_id: str  # MongoDB ObjectId of the user who created the draft
    current_step: int = 1  # Current wizard step (1-7)

    # Basic Information (all Optional for partial saves)
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    vendor_info: Optional[Dict[str, Any]] = None
    cost_estimate: Optional[str] = None
    impact_metrics: Optional[Dict[str, Any]] = None
    industry_tags: Optional[List[str]] = None
    region: Optional[str] = None
    location: Optional[Dict[str, float]] = None

    # Detailed Information
    subtitle: Optional[str] = None
    description_long: Optional[str] = None
    category: Optional[str] = None
    factory_name: Optional[str] = None
    implementation_time: Optional[str] = None
    roi_percentage: Optional[str] = None

    # Contact & Metadata
    contact_person: Optional[str] = None
    contact_title: Optional[str] = None
    images: Optional[List[str]] = None  # S3 URLs for images
    videos: Optional[List[Dict[str, str]]] = None  # [{"url": "...", "thumbnail": "...", "filename": "..."}]

    # Rich Content Sections
    executive_summary: Optional[str] = None
    business_challenge: Optional[Dict[str, Any]] = None
    solution_details: Optional[Dict[str, Any]] = None
    implementation_details: Optional[Dict[str, Any]] = None
    challenges_and_solutions: Optional[List[Dict[str, str]]] = None
    results: Optional[Dict[str, Any]] = None
    technical_architecture: Optional[Dict[str, Any]] = None
    future_roadmap: Optional[List[Dict[str, str]]] = None
    lessons_learned: Optional[List[Dict[str, str]]] = None

    # Additional Metadata
    read_time: Optional[str] = None
    technology_tags: Optional[List[str]] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "use_case_drafts"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("updated_at", pymongo.DESCENDING)],
            [("user_id", pymongo.ASCENDING), ("updated_at", pymongo.DESCENDING)]
        ]

class Invitation(Document):
    """Model for user invitations"""
    email: EmailStr
    token: str = Field(..., unique=True)
    invited_by_id: str
    invited_by_email: str
    invited_by_name: str
    expires_at: datetime
    used: bool = False
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "invitations"
        indexes = [
            [("token", pymongo.ASCENDING)],
            [("email", pymongo.ASCENDING)],
            [("invited_by_id", pymongo.ASCENDING)],
            [("expires_at", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]