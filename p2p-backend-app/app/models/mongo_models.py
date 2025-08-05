from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
import pymongo

class User(Document):
    email: Indexed(EmailStr, unique=True)
    name: str
    role: str = "user"
    industry_sector: Optional[str] = None
    location: Optional[str] = None
    expertise_tags: List[str] = Field(default_factory=list)
    verified: bool = False
    language_preference: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            [("email", pymongo.ASCENDING)],
            [("expertise_tags", pymongo.ASCENDING)]
        ]

class ForumPost(Document):
    author_id: str
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    best_answer_id: Optional[str] = None
    status: str = "open"  # open, resolved, closed
    view_count: int = 0
    views: int = 0  # Alternative name for view_count
    reply_count: int = 0
    upvotes: int = 0  # Likes/upvotes for the post
    is_pinned: bool = False  # Whether post is pinned
    has_best_answer: bool = False  # Whether post has a best answer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
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
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    upvotes: int = 0
    is_best_answer: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_replies"
        indexes = [
            [("post_id", pymongo.ASCENDING)],
            [("created_at", pymongo.ASCENDING)]
        ]

# User Activity and Stats Models
class UserActivity(Document):
    """Track user activities for dashboard feed and stats"""
    user_id: str
    activity_type: str  # "question", "answer", "usecase", "bookmark", "like", "comment"
    target_id: str  # ID of the target (post, reply, usecase)
    target_title: Optional[str] = None  # Title for display
    target_category: Optional[str] = None  # Category for display
    description: Optional[str] = None  # Activity description
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_activities"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("activity_type", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]

class UserStats(Document):
    """Aggregate user statistics for dashboard"""
    user_id: Indexed(str, unique=True)
    questions_asked: int = 0
    answers_given: int = 0
    best_answers: int = 0
    use_cases_submitted: int = 0
    bookmarks_saved: int = 0
    total_upvotes_received: int = 0
    reputation_score: int = 0
    activity_level: float = 0.0  # 0-100 percentage
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
    """Track user bookmarks/saved items"""
    user_id: str
    target_type: str  # "forum_post", "forum_reply", "use_case"
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
    """Store user draft posts/content"""
    user_id: str
    title: str
    content: str
    post_type: str  # "forum_post", "use_case"
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
    # Basic Information (Required - from JSON)
    submitted_by: str
    title: str
    problem_statement: str  # Maps to "description" in JSON
    solution_description: str  # Maps to first "benefit" in JSON
    vendor_info: Optional[Dict[str, str]] = None
    cost_estimate: Optional[str] = None
    impact_metrics: Dict[str, str] = Field(default_factory=dict)
    industry_tags: List[str] = Field(default_factory=list)
    region: str
    location: Dict[str, float]  # {"lat": 24.7136, "lng": 46.6753}
    bookmarks: List[str] = Field(default_factory=list)
    published: bool = False
    featured: bool = False
    
    # Detailed Information (Optional - for enterprise use cases)
    subtitle: Optional[str] = None
    description_long: Optional[str] = None  # Extended description
    category: Optional[str] = None
    factory_name: Optional[str] = None
    implementation_time: Optional[str] = None
    roi_percentage: Optional[str] = None
    
    # Contact & Metadata
    contact_person: Optional[str] = None
    contact_title: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    
    # Executive Summary
    executive_summary: Optional[str] = None
    
    # Business Challenge & Context
    business_challenge: Optional[Dict[str, Any]] = None
    # Structure: {
    #   "industry_context": str,
    #   "specific_problems": List[str],
    #   "business_impact": Dict[str, str],
    #   "strategic_drivers": List[str]
    # }
    
    # Solution Overview  
    solution_details: Optional[Dict[str, Any]] = None
    # Structure: {
    #   "selection_criteria": List[str],
    #   "vendor_evaluation": Dict[str, Any],
    #   "technology_components": List[Dict[str, str]]
    # }
    
    # Implementation Journey
    implementation_details: Optional[Dict[str, Any]] = None
    # Structure: {
    #   "methodology": str,
    #   "project_team": Dict[str, List],
    #   "phases": List[Dict],
    #   "total_budget": str,
    #   "total_duration": str
    # }
    
    # Challenges & Solutions
    challenges_and_solutions: List[Dict[str, str]] = Field(default_factory=list)
    # Structure: [{"challenge": str, "description": str, "impact": str, "solution": str, "outcome": str}]
    
    # Results & Impact Analysis
    results: Optional[Dict[str, Any]] = None
    # Structure: {
    #   "quantitative_metrics": List[Dict],
    #   "qualitative_impacts": List[str],
    #   "roi_analysis": Dict[str, str]
    # }
    
    # Technical Architecture
    technical_architecture: Optional[Dict[str, Any]] = None
    # Structure: {
    #   "system_overview": str,
    #   "components": List[Dict],
    #   "security_measures": List[str],
    #   "scalability_design": List[str]
    # }
    
    # Future Roadmap
    future_roadmap: List[Dict[str, str]] = Field(default_factory=list)
    # Structure: [{"timeline": str, "initiative": str, "description": str, "expected_benefit": str}]
    
    # Lessons Learned
    lessons_learned: List[Dict[str, str]] = Field(default_factory=list)
    # Structure: [{"category": str, "lesson": str, "description": str, "recommendation": str}]
    
    # Additional Metadata
    published_date: Optional[str] = None
    last_updated: Optional[str] = None
    read_time: Optional[str] = None
    views: int = 0
    downloads: int = 0
    status: str = "draft"  # draft, published, verified
    verified_by: Optional[str] = None
    technology_tags: List[str] = Field(default_factory=list)
    
    # Linking Fields for Basic <-> Detailed Use Cases
    detailed_version_id: Optional[str] = None  # Points to detailed version
    basic_version_id: Optional[str] = None     # Points to basic version
    has_detailed_view: bool = False            # Flag for basic use cases
    is_detailed_version: bool = False          # Flag for detailed use cases
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "use_cases"
        indexes = [
            [("industry_tags", pymongo.ASCENDING)],
            [("region", pymongo.ASCENDING)],
            [("location", pymongo.GEO2D)]
        ]