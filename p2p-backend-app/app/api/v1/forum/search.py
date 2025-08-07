"""Forum search endpoints."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user as get_current_active_user
from app.core.rbac import require_organization_access
from app.db.session import get_db
from app.models.user import User
from app.services.forum import ForumService
from app.schemas.forum import (
    ForumSearchQuery,
    ForumSearchResponse
)

router = APIRouter()


@router.get("/", response_model=ForumSearchResponse)
async def search_forum(
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    search_in: Optional[str] = Query("all", regex="^(all|topics|posts)$", description="Search scope"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    author_id: Optional[UUID] = Query(None, description="Filter by author ID"),
    date_from: Optional[datetime] = Query(None, description="Filter posts from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter posts until this date"),
    sort_by: Optional[str] = Query("relevance", regex="^(relevance|date|likes)$", description="Sort results by"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search across forum topics and posts.
    
    **Search Features:**
    - Full-text search in topic titles, content, and post content
    - Filter by category, author, or date range
    - Sort by relevance, date, or popularity (likes)
    - Search in all content, topics only, or posts only
    
    **Parameters:**
    - `q`: Search query (minimum 2 characters)
    - `search_in`: Scope of search (all/topics/posts)
    - `category_id`: Filter by specific category
    - `author_id`: Filter by specific author
    - `date_from`: Filter content created after this date
    - `date_to`: Filter content created before this date
    - `sort_by`: Sort results by relevance, date, or likes
    - `page`: Page number for pagination
    - `page_size`: Number of results per page (max 100)
    
    **Returns:**
    - Paginated list of search results with highlights
    - Each result includes type (topic/post), content, author, and metadata
    - Search time in milliseconds for performance monitoring
    
    **Example Search Queries:**
    - "production efficiency" - Find all content about production efficiency
    - "sensor" with category_id - Find sensor-related content in specific category
    - "quality" with author_id - Find all quality-related posts by specific user
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # Create search query object
    search_query = ForumSearchQuery(
        q=q,
        search_in=search_in,
        category_id=category_id,
        author_id=author_id,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )
    
    # Perform search
    return await ForumService.search_forum(
        db,
        search_query=search_query,
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, max_length=50, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get search suggestions based on partial query.
    
    **Features:**
    - Returns popular search terms matching the partial query
    - Suggests topic titles that match
    - Limited to user's organization
    
    **Parameters:**
    - `q`: Partial search query (minimum 2 characters)
    - `limit`: Maximum number of suggestions (max 20)
    
    **Returns:**
    - List of suggested search terms
    - Popular matching topic titles
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # For now, return simple suggestions based on topic titles
    # In production, this would use a more sophisticated suggestion system
    from app.crud.forum import forum_topic
    
    suggestions = []
    
    # Get topics matching the partial query
    topics, _ = await forum_topic.get_multi_with_search(
        db,
        search_params={
            "search": q,
            "page": 1,
            "page_size": limit
        },
        organization_id=current_user.organization_id,
        skip=0,
        limit=limit
    )
    
    # Extract unique title words as suggestions
    for topic in topics:
        # Add the full title if it matches
        if q.lower() in topic.title.lower():
            suggestions.append(topic.title)
        
        # Add individual words that match
        words = topic.title.split()
        for word in words:
            if q.lower() in word.lower() and len(word) > 3:
                if word.lower() not in [s.lower() for s in suggestions]:
                    suggestions.append(word)
    
    # Limit suggestions
    suggestions = suggestions[:limit]
    
    return {
        "suggestions": suggestions,
        "query": q
    }


@router.get("/trending")
async def get_trending_searches(
    period: Optional[str] = Query("week", regex="^(day|week|month)$", description="Time period"),
    limit: int = Query(10, ge=1, le=20, description="Number of trending terms"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get trending search terms in the forum.
    
    **Features:**
    - Shows popular search terms for the specified period
    - Helps users discover hot topics
    - Organization-specific trends
    
    **Parameters:**
    - `period`: Time period (day/week/month)
    - `limit`: Number of trending terms to return (max 20)
    
    **Returns:**
    - List of trending search terms with search counts
    - Popular topics for the period
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    # For now, return mock trending data
    # In production, this would track actual search queries
    trending = [
        {"term": "automation sensors", "count": 45},
        {"term": "quality management", "count": 38},
        {"term": "production efficiency", "count": 32},
        {"term": "maintenance schedule", "count": 28},
        {"term": "IoT integration", "count": 25},
        {"term": "cost reduction", "count": 22},
        {"term": "safety protocols", "count": 20},
        {"term": "AI implementation", "count": 18},
        {"term": "supply chain", "count": 15},
        {"term": "energy efficiency", "count": 12}
    ]
    
    return {
        "trending": trending[:limit],
        "period": period,
        "organization_id": str(current_user.organization_id)
    }