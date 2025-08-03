# Story 2: Topic-Based Forum System

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 6  
**Priority**: High  
**Dependencies**: Story 1 (User Profile Management)

## User Story
**As a** platform user (Factory Owner, Plant Engineer, Operations Manager)  
**I want** to browse and navigate industry-specific forum topics and categories  
**So that** I can find relevant discussions in my area of expertise and discover solutions to similar challenges

## Acceptance Criteria
- [x] Forum organized by 4 main categories: Technical, Business, Training, General
- [x] Each category displays subcategories relevant to industrial SMEs
- [x] Category pages show post previews with metadata (title, author, replies, views, last activity)
- [x] Forum supports industry-specific tags for cross-category topics
- [x] Arabic and English content display properly with RTL support for Arabic
- [x] Category descriptions help users understand appropriate content
- [x] Responsive design works seamlessly on mobile and desktop
- [x] Category-based filtering and sorting options available
- [x] Post count and activity statistics visible for each category
- [x] Breadcrumb navigation shows current location in forum hierarchy

## Technical Specifications

### 1. Database Schema for Forum Structure

#### Update app/models/mongo_models.py
```python
from beanie import Document, Indexed, before_event, Replace, Insert
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List, Dict
import pymongo

class ForumCategory(Document):
    name: str
    slug: Indexed(str, unique=True)  # URL-friendly identifier
    description: str
    description_ar: Optional[str] = None  # Arabic description
    icon: str  # Icon class or emoji
    color: str  # Hex color for category badge
    sort_order: int = 0
    
    # Category settings
    is_active: bool = True
    requires_verification: bool = False  # Some categories may require verified users
    moderator_ids: List[str] = Field(default_factory=list)
    
    # Statistics
    post_count: int = 0
    reply_count: int = 0
    last_post_id: Optional[str] = None
    last_activity_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_categories"
        indexes = [
            [("slug", pymongo.ASCENDING)],
            [("sort_order", pymongo.ASCENDING)],
            [("is_active", pymongo.ASCENDING)]
        ]

class ForumTag(Document):
    name: str
    slug: Indexed(str, unique=True)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    category: str  # Category this tag belongs to
    color: str = "#6B7280"  # Default gray
    
    # Usage statistics
    usage_count: int = 0
    created_by: str  # User ID who created the tag
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_tags"
        indexes = [
            [("slug", pymongo.ASCENDING)],
            [("category", pymongo.ASCENDING)],
            [("usage_count", pymongo.DESCENDING)]
        ]

# Update ForumPost model with category integration
class ForumPost(Document):
    # Basic Information
    title: str
    slug: Indexed(str)  # Auto-generated from title
    content: str  # Rich text content
    author_id: str
    author_name: str  # Denormalized for performance
    author_avatar: Optional[str] = None
    author_verification_status: str = "pending"
    
    # Categorization
    category_id: str
    category_name: str  # Denormalized
    tags: List[str] = Field(default_factory=list, max_items=5)
    
    # Content metadata
    language: str = "en"  # en, ar
    content_type: str = "discussion"  # discussion, question, tutorial, announcement
    
    # Attachments
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    # [{"type": "image", "url": "...", "name": "...", "size": 123456}]
    
    # Engagement
    view_count: int = 0
    reply_count: int = 0
    upvote_count: int = 0
    bookmark_count: int = 0
    
    # Status and Moderation
    status: str = "published"  # draft, published, locked, archived, deleted
    is_pinned: bool = False
    is_featured: bool = False
    has_best_answer: bool = False
    best_answer_id: Optional[str] = None
    
    # Activity tracking
    last_reply_at: Optional[datetime] = None
    last_reply_author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @before_event([Replace, Insert])
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        import re
        if not self.slug:
            # Simple slug generation (implement proper Arabic support later)
            slug = re.sub(r'[^\w\s-]', '', self.title.lower())
            slug = re.sub(r'[-\s]+', '-', slug)
            self.slug = slug[:50]  # Limit length
    
    class Settings:
        name = "forum_posts"
        indexes = [
            [("category_id", pymongo.ASCENDING)],
            [("tags", pymongo.ASCENDING)],
            [("status", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)],
            [("last_reply_at", pymongo.DESCENDING)],
            [("view_count", pymongo.DESCENDING)],
            [("is_pinned", pymongo.DESCENDING), ("created_at", pymongo.DESCENDING)],
            [("slug", pymongo.ASCENDING)]
        ]
```

### 2. API Endpoints for Forum Navigation

#### app/api/v1/endpoints/forum.py
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from typing import Optional, List
from app.schemas.forum import (
    ForumCategoryResponse, ForumPostSummary, ForumOverviewResponse,
    CategoryPostsResponse, ForumTagResponse
)
from app.services.forum_service import ForumService
from app.core.logging import logger

router = APIRouter()

@router.get("/", response_model=ForumOverviewResponse)
async def get_forum_overview(
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    """Get forum overview with categories and statistics"""
    try:
        user_id = session.get_user_id() if session else None
        overview = await ForumService.get_forum_overview(user_id)
        return overview
    except Exception as e:
        logger.error(f"Forum overview fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load forum")

@router.get("/categories", response_model=List[ForumCategoryResponse])
async def get_categories(
    include_stats: bool = Query(True, description="Include post counts and activity stats")
):
    """Get all forum categories"""
    try:
        categories = await ForumService.get_categories(include_stats=include_stats)
        return categories
    except Exception as e:
        logger.error(f"Categories fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load categories")

@router.get("/categories/{category_slug}", response_model=CategoryPostsResponse)
async def get_category_posts(
    category_slug: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Posts per page"),
    sort_by: str = Query("latest", description="Sort by: latest, popular, trending"),
    tag_filter: Optional[str] = Query(None, description="Filter by tag"),
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    """Get posts for a specific category"""
    try:
        user_id = session.get_user_id() if session else None
        posts = await ForumService.get_category_posts(
            category_slug=category_slug,
            page=page,
            limit=limit,
            sort_by=sort_by,
            tag_filter=tag_filter,
            user_id=user_id
        )
        return posts
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Category posts fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load posts")

@router.get("/categories/{category_slug}/tags", response_model=List[ForumTagResponse])
async def get_category_tags(category_slug: str):
    """Get tags available in a specific category"""
    try:
        tags = await ForumService.get_category_tags(category_slug)
        return tags
    except Exception as e:
        logger.error(f"Category tags fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load tags")

@router.get("/trending")
async def get_trending_posts(
    limit: int = Query(10, ge=1, le=20),
    hours: int = Query(24, ge=1, le=168, description="Trending in last N hours")
):
    """Get trending posts across all categories"""
    try:
        posts = await ForumService.get_trending_posts(limit=limit, hours=hours)
        return posts
    except Exception as e:
        logger.error(f"Trending posts fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load trending posts")

@router.get("/recent")
async def get_recent_activity(
    limit: int = Query(15, ge=1, le=30),
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    """Get recent forum activity"""
    try:
        user_id = session.get_user_id() if session else None
        activity = await ForumService.get_recent_activity(limit=limit, user_id=user_id)
        return activity
    except Exception as e:
        logger.error(f"Recent activity fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load recent activity")
```

### 3. Pydantic Schemas for Forum Data

#### app/schemas/forum.py
```python
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ForumCategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    description_ar: Optional[str]
    icon: str
    color: str
    post_count: int
    reply_count: int
    last_activity_at: Optional[datetime]
    last_post: Optional[Dict[str, str]]  # {"title": "...", "author": "...", "created_at": "..."}
    requires_verification: bool

class ForumTagResponse(BaseModel):
    name: str
    slug: str
    description: Optional[str]
    color: str
    usage_count: int

class ForumPostAuthor(BaseModel):
    id: str
    name: str
    avatar: Optional[str]
    verification_status: str
    reputation_score: Optional[int]

class ForumPostSummary(BaseModel):
    id: str
    title: str
    slug: str
    content_preview: str  # First 200 characters
    author: ForumPostAuthor
    category: Dict[str, str]  # {"id": "...", "name": "...", "slug": "..."}
    tags: List[str]
    language: str
    content_type: str
    view_count: int
    reply_count: int
    upvote_count: int
    has_best_answer: bool
    is_pinned: bool
    is_featured: bool
    created_at: datetime
    last_reply_at: Optional[datetime]
    last_reply_author: Optional[str]

class CategoryPostsResponse(BaseModel):
    category: ForumCategoryResponse
    posts: List[ForumPostSummary]
    pagination: Dict[str, int]  # {"page": 1, "limit": 20, "total": 150, "pages": 8}
    available_tags: List[ForumTagResponse]

class ForumOverviewResponse(BaseModel):
    categories: List[ForumCategoryResponse]
    recent_posts: List[ForumPostSummary]
    trending_posts: List[ForumPostSummary]
    stats: Dict[str, int]  # {"total_posts": 1234, "total_users": 567, "posts_today": 12}
    featured_posts: List[ForumPostSummary]

class ForumActivityItem(BaseModel):
    type: str  # post_created, reply_added, best_answer_marked
    post_id: str
    post_title: str
    user_name: str
    user_avatar: Optional[str]
    category_name: str
    created_at: datetime
```

### 4. Service Layer Implementation

#### app/services/forum_service.py
```python
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.models.mongo_models import ForumCategory, ForumPost, ForumTag, UserProfile
from app.schemas.forum import (
    ForumOverviewResponse, ForumCategoryResponse, CategoryPostsResponse,
    ForumPostSummary, ForumTagResponse, ForumPostAuthor
)
from app.core.logging import logger

class ForumService:
    @staticmethod
    async def get_forum_overview(user_id: Optional[str] = None) -> ForumOverviewResponse:
        """Get forum overview with categories and recent activity"""
        # Get categories with stats
        categories = await ForumService.get_categories(include_stats=True)
        
        # Get recent posts (last 7 days)
        recent_posts = await ForumService.get_recent_posts(limit=10)
        
        # Get trending posts (last 24 hours, sorted by engagement)
        trending_posts = await ForumService.get_trending_posts(limit=5, hours=24)
        
        # Get featured posts
        featured_posts = await ForumPost.find(
            ForumPost.is_featured == True,
            ForumPost.status == "published"
        ).sort([("created_at", -1)]).limit(3).to_list()
        
        # Get overall stats
        total_posts = await ForumPost.find(ForumPost.status == "published").count()
        total_users = await UserProfile.find().count()
        posts_today = await ForumPost.find(
            ForumPost.status == "published",
            ForumPost.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        return ForumOverviewResponse(
            categories=categories,
            recent_posts=[await ForumService._post_to_summary(post) for post in recent_posts],
            trending_posts=[await ForumService._post_to_summary(post) for post in trending_posts],
            featured_posts=[await ForumService._post_to_summary(post) for post in featured_posts],
            stats={
                "total_posts": total_posts,
                "total_users": total_users,
                "posts_today": posts_today
            }
        )
    
    @staticmethod
    async def get_categories(include_stats: bool = True) -> List[ForumCategoryResponse]:
        """Get all forum categories"""
        categories = await ForumCategory.find(
            ForumCategory.is_active == True
        ).sort([("sort_order", 1)]).to_list()
        
        result = []
        for category in categories:
            last_post = None
            if category.last_post_id:
                post = await ForumPost.find_one(
                    ForumPost.id == category.last_post_id,
                    ForumPost.status == "published"
                )
                if post:
                    last_post = {
                        "title": post.title,
                        "author": post.author_name,
                        "created_at": post.created_at.isoformat()
                    }
            
            result.append(ForumCategoryResponse(
                id=str(category.id),
                name=category.name,
                slug=category.slug,
                description=category.description,
                description_ar=category.description_ar,
                icon=category.icon,
                color=category.color,
                post_count=category.post_count,
                reply_count=category.reply_count,
                last_activity_at=category.last_activity_at,
                last_post=last_post,
                requires_verification=category.requires_verification
            ))
        
        return result
    
    @staticmethod
    async def get_category_posts(
        category_slug: str,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "latest",
        tag_filter: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> CategoryPostsResponse:
        """Get posts for a specific category"""
        # Find category
        category = await ForumCategory.find_one(ForumCategory.slug == category_slug)
        if not category:
            raise ValueError("Category not found")
        
        # Build query
        query_filters = [
            ForumPost.category_id == str(category.id),
            ForumPost.status == "published"
        ]
        
        if tag_filter:
            query_filters.append(ForumPost.tags.contains(tag_filter))
        
        # Build sort criteria
        sort_criteria = []
        if sort_by == "popular":
            sort_criteria = [("view_count", -1), ("reply_count", -1)]
        elif sort_by == "trending":
            # Posts with recent activity and high engagement
            sort_criteria = [("last_reply_at", -1), ("reply_count", -1)]
        else:  # latest
            sort_criteria = [("is_pinned", -1), ("created_at", -1)]
        
        # Execute query
        skip = (page - 1) * limit
        posts = await ForumPost.find(
            {"$and": query_filters}
        ).sort(sort_criteria).skip(skip).limit(limit).to_list()
        
        total_count = await ForumPost.find({"$and": query_filters}).count()
        total_pages = (total_count + limit - 1) // limit
        
        # Get available tags for this category
        available_tags = await ForumService.get_category_tags(category_slug)
        
        return CategoryPostsResponse(
            category=ForumCategoryResponse(
                id=str(category.id),
                name=category.name,
                slug=category.slug,
                description=category.description,
                description_ar=category.description_ar,
                icon=category.icon,
                color=category.color,
                post_count=category.post_count,
                reply_count=category.reply_count,
                last_activity_at=category.last_activity_at,
                last_post=None,
                requires_verification=category.requires_verification
            ),
            posts=[await ForumService._post_to_summary(post) for post in posts],
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": total_pages
            },
            available_tags=available_tags
        )
    
    @staticmethod
    async def get_category_tags(category_slug: str) -> List[ForumTagResponse]:
        """Get tags for a specific category"""
        category = await ForumCategory.find_one(ForumCategory.slug == category_slug)
        if not category:
            return []
        
        tags = await ForumTag.find(
            ForumTag.category == str(category.id)
        ).sort([("usage_count", -1)]).to_list()
        
        return [
            ForumTagResponse(
                name=tag.name,
                slug=tag.slug,
                description=tag.description,
                color=tag.color,
                usage_count=tag.usage_count
            )
            for tag in tags
        ]
    
    @staticmethod
    async def get_trending_posts(limit: int = 10, hours: int = 24) -> List[ForumPost]:
        """Get trending posts based on recent activity and engagement"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        posts = await ForumPost.find(
            ForumPost.status == "published",
            ForumPost.created_at >= since
        ).sort([
            ("reply_count", -1),
            ("view_count", -1),
            ("upvote_count", -1)
        ]).limit(limit).to_list()
        
        return posts
    
    @staticmethod
    async def get_recent_posts(limit: int = 10) -> List[ForumPost]:
        """Get recent posts"""
        posts = await ForumPost.find(
            ForumPost.status == "published"
        ).sort([("created_at", -1)]).limit(limit).to_list()
        
        return posts
    
    @staticmethod
    async def _post_to_summary(post: ForumPost) -> ForumPostSummary:
        """Convert ForumPost to ForumPostSummary"""
        # Get author profile for additional info
        author_profile = await UserProfile.find_one(UserProfile.user_id == post.author_id)
        
        author = ForumPostAuthor(
            id=post.author_id,
            name=post.author_name,
            avatar=post.author_avatar,
            verification_status=post.author_verification_status,
            reputation_score=author_profile.reputation_score if author_profile else 0
        )
        
        # Get category info
        category = await ForumCategory.find_one(ForumCategory.id == post.category_id)
        category_info = {
            "id": post.category_id,
            "name": post.category_name,
            "slug": category.slug if category else ""
        }
        
        # Create content preview (first 200 chars, strip HTML)
        import re
        clean_content = re.sub(r'<[^>]+>', '', post.content)
        content_preview = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
        
        return ForumPostSummary(
            id=str(post.id),
            title=post.title,
            slug=post.slug,
            content_preview=content_preview,
            author=author,
            category=category_info,
            tags=post.tags,
            language=post.language,
            content_type=post.content_type,
            view_count=post.view_count,
            reply_count=post.reply_count,
            upvote_count=post.upvote_count,
            has_best_answer=post.has_best_answer,
            is_pinned=post.is_pinned,
            is_featured=post.is_featured,
            created_at=post.created_at,
            last_reply_at=post.last_reply_at,
            last_reply_author=post.last_reply_author
        )
```

### 5. Frontend Components

#### Create frontend/src/components/Forum/ForumOverview.tsx
```typescript
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MessageCircle, Users, TrendingUp, Pin, Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '@/lib/api';

interface ForumCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  post_count: number;
  reply_count: number;
  last_activity_at?: string;
  last_post?: {
    title: string;
    author: string;
    created_at: string;
  };
}

interface ForumPost {
  id: string;
  title: string;
  slug: string;
  content_preview: string;
  author: {
    name: string;
    verification_status: string;
  };
  category: {
    name: string;
    slug: string;
  };
  reply_count: number;
  view_count: number;
  is_pinned: boolean;
  is_featured: boolean;
  created_at: string;
}

interface ForumOverview {
  categories: ForumCategory[];
  recent_posts: ForumPost[];
  trending_posts: ForumPost[];
  featured_posts: ForumPost[];
  stats: {
    total_posts: number;
    total_users: number;
    posts_today: number;
  };
}

export default function ForumOverview() {
  const { t } = useTranslation();
  const [overview, setOverview] = useState<ForumOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchForumOverview();
  }, []);

  const fetchForumOverview = async () => {
    try {
      const response = await api.get('/api/v1/forum/');
      setOverview(response.data);
    } catch (error) {
      console.error('Failed to fetch forum overview:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (!overview) {
    return <div>Failed to load forum</div>;
  }

  return (
    <div className="space-y-6">
      {/* Forum Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="flex items-center p-6">
            <MessageCircle className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('forum.stats.total_posts')}</p>
              <p className="text-2xl font-bold">{overview.stats.total_posts.toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="flex items-center p-6">
            <Users className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('forum.stats.total_users')}</p>
              <p className="text-2xl font-bold">{overview.stats.total_users.toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="flex items-center p-6">
            <TrendingUp className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{t('forum.stats.posts_today')}</p>
              <p className="text-2xl font-bold">{overview.stats.posts_today}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Forum Categories */}
      <Card>
        <CardHeader>
          <CardTitle>{t('forum.categories.title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {overview.categories.map((category) => (
              <Link
                key={category.id}
                to={`/forum/category/${category.slug}`}
                className="block"
              >
                <Card className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
                          style={{ backgroundColor: category.color }}
                        >
                          <span className="text-lg">{category.icon}</span>
                        </div>
                        <div>
                          <h3 className="font-semibold">{category.name}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {category.description}
                          </p>
                        </div>
                      </div>
                      <div className="text-right text-sm text-gray-500">
                        <p>{category.post_count} {t('forum.posts')}</p>
                        <p>{category.reply_count} {t('forum.replies')}</p>
                      </div>
                    </div>
                    
                    {category.last_post && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs text-gray-500">
                          {t('forum.last_post')}: 
                          <span className="ml-1 font-medium">
                            {category.last_post.title}
                          </span>
                          {t('forum.by')} {category.last_post.author}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Posts */}
        <Card>
          <CardHeader>
            <CardTitle>{t('forum.recent_posts')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {overview.recent_posts.slice(0, 5).map((post) => (
                <div key={post.id} className="border-b border-gray-200 pb-3 last:border-b-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Link 
                        to={`/forum/post/${post.slug}`}
                        className="font-medium hover:text-blue-600 flex items-center"
                      >
                        {post.is_pinned && <Pin className="h-4 w-4 mr-1 text-blue-500" />}
                        {post.is_featured && <Star className="h-4 w-4 mr-1 text-yellow-500" />}
                        {post.title}
                      </Link>
                      <p className="text-sm text-gray-600 mt-1">
                        {post.content_preview}
                      </p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                        <span>{post.author.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {post.category.name}
                        </Badge>
                        <span>{post.reply_count} {t('forum.replies')}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Button variant="outline" className="w-full" asChild>
                <Link to="/forum/recent">{t('forum.view_all_recent')}</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Trending Posts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              {t('forum.trending_posts')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {overview.trending_posts.map((post) => (
                <div key={post.id} className="border-b border-gray-200 pb-3 last:border-b-0">
                  <Link 
                    to={`/forum/post/${post.slug}`}
                    className="font-medium hover:text-blue-600 block"
                  >
                    {post.title}
                  </Link>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>{post.author.name}</span>
                    <span>{post.view_count} {t('forum.views')}</span>
                    <span>{post.reply_count} {t('forum.replies')}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

## Implementation Steps

1. **Database Setup**
   ```bash
   # Create forum categories and tags collections
   # Set up indexes for optimal querying
   # Create default categories and tags
   ```

2. **Backend Implementation**
   ```bash
   # Implement ForumService with category management
   # Create API endpoints for forum navigation
   # Add proper error handling and validation
   ```

3. **Frontend Components**
   ```bash
   # Create forum overview and category components
   # Implement responsive design for mobile/desktop
   # Add Arabic/English language support
   ```

4. **Data Seeding**
   ```bash
   # Create initial forum categories
   # Add default tags for each category
   # Create sample posts for testing
   ```

## Testing Checklist
- [ ] Forum categories display correctly with stats
- [ ] Category filtering and sorting work properly
- [ ] Responsive design works on all screen sizes
- [ ] Arabic/English language switching functions
- [ ] Post previews show relevant information
- [ ] Category navigation and breadcrumbs work
- [ ] Trending and recent posts algorithms function
- [ ] Category access permissions respected
- [ ] Performance is acceptable with large datasets

## Default Categories to Create
- **Technical** (🔧): Equipment troubleshooting, automation, quality control
- **Business** (💼): Strategy, cost optimization, market insights
- **Training** (📚): Skills development, certification programs, workshops  
- **General** (💬): Networking, announcements, general discussions

## Dependencies
- Story 1 (User Profile Management) must be completed
- Database schema updates applied
- Frontend routing configured

## Notes
- Implement proper caching for category statistics
- Consider performance optimization for large forums
- Plan for future moderation tools and admin controls
- Ensure scalable architecture for growing content