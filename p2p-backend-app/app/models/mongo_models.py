from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict
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
    reply_count: int = 0
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

class UseCase(Document):
    submitted_by: str
    title: str
    problem_statement: str
    solution_description: str
    vendor_info: Optional[Dict[str, str]] = None
    cost_estimate: Optional[str] = None
    impact_metrics: Dict[str, str] = Field(default_factory=dict)
    industry_tags: List[str] = Field(default_factory=list)
    region: str
    location: Dict[str, float]  # {"lat": 24.7136, "lng": 46.6753}
    bookmarks: List[str] = Field(default_factory=list)
    published: bool = False
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "use_cases"
        indexes = [
            [("industry_tags", pymongo.ASCENDING)],
            [("region", pymongo.ASCENDING)],
            [("location", pymongo.GEO2D)]
        ]