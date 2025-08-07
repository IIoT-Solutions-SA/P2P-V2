"""Use Cases API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.rbac import get_current_user as get_current_active_user, get_current_user_optional
from app.core.rbac import require_organization_access
from app.db.mongodb import get_mongodb
from app.models.user import User
from app.services.use_case import UseCaseService
from app.schemas.use_case import (
    UseCaseCreate,
    UseCaseUpdate,
    UseCaseResponse,
    UseCaseDetail,
    UseCaseListResponse,
    UseCaseFilters,
    DraftSave,
    DraftResponse,
    LikeResponse,
    SaveResponse
)

router = APIRouter()


@router.post("/", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_use_case(
    use_case_in: UseCaseCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new use case.
    
    **Required fields:**
    - title: Use case title (10-200 characters)
    - company: Company name
    - industry: Industry sector
    - category: One of [automation, quality, maintenance, efficiency, innovation, sustainability]
    - description: Detailed description (50-5000 characters)
    - results: Metrics and ROI information
    
    **Optional fields:**
    - challenge: Problem statement
    - solution: Solution approach
    - implementation: Timeline, phases, team size, budget
    - technologies: List of technologies used
    - vendors: Vendor/supplier information
    - location: City, region, coordinates
    - tags: Searchable tags
    - status: draft|published (default: draft)
    - visibility: public|organization|private (default: organization)
    """
    # Ensure user belongs to an organization
    await require_organization_access(
        db,
        current_user,
        current_user.organization_id
    )
    
    # Create use case
    use_case = await UseCaseService.create_use_case(
        db,
        use_case_in=use_case_in,
        current_user=current_user
    )
    
    return UseCaseResponse(
        id=use_case.id,
        title=use_case.title,
        status=use_case.status,
        created_at=use_case.created_at,
        message="Use case created successfully"
    )


@router.get("/", response_model=UseCaseListResponse)
async def browse_use_cases(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    technologies: Optional[List[str]] = Query(None, description="Filter by technologies"),
    verified: Optional[bool] = Query(None, description="Show only verified cases"),
    featured: Optional[bool] = Query(None, description="Show only featured cases"),
    sort_by: Optional[str] = Query("date", pattern="^(date|views|likes|roi)$", description="Sort field"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, min_length=2, max_length=200, description="Search query"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Browse published use cases with filters and pagination.
    
    **Filters:**
    - category: automation|quality|maintenance|efficiency|innovation|sustainability
    - industry: Filter by industry sector
    - technologies: Filter by technologies used
    - verified: Show only verified use cases
    - featured: Show only featured use cases
    
    **Sorting:**
    - sort_by: date|views|likes|roi
    - order: asc|desc
    
    **Search:**
    - search: Full-text search across title, description, solution, and tags
    """
    filters = UseCaseFilters(
        page=page,
        page_size=page_size,
        category=category,
        industry=industry,
        technologies=technologies,
        verified=verified,
        featured=featured,
        sort_by=sort_by,
        order=order,
        search=search
    )
    
    result = await UseCaseService.browse_use_cases(
        db,
        filters=filters,
        current_user=current_user
    )
    
    return UseCaseListResponse(**result)


@router.get("/{use_case_id}", response_model=UseCaseDetail)
async def get_use_case(
    use_case_id: str,
    track_view: bool = Query(True, description="Track this view"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific use case.
    
    **Features:**
    - Full use case details including all fields
    - View tracking (can be disabled with track_view=false)
    - Related use cases
    - Respects visibility settings (public/organization/private)
    """
    return await UseCaseService.get_use_case(
        db,
        use_case_id=use_case_id,
        current_user=current_user,
        track_view=track_view
    )


@router.patch("/{use_case_id}", response_model=UseCaseResponse)
async def update_use_case(
    use_case_id: str,
    use_case_in: UseCaseUpdate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing use case.
    
    **Permissions:**
    - Only the owner or an admin can update a use case
    
    **Updatable fields:**
    - All fields from creation are updatable
    - Partial updates supported (only send fields to update)
    """
    use_case = await UseCaseService.update_use_case(
        db,
        use_case_id=use_case_id,
        use_case_in=use_case_in,
        current_user=current_user
    )
    
    return UseCaseResponse(
        id=use_case.id,
        title=use_case.title,
        status=use_case.status,
        created_at=use_case.created_at,
        message="Use case updated successfully"
    )


@router.delete("/{use_case_id}")
async def delete_use_case(
    use_case_id: str,
    hard_delete: bool = Query(False, description="Permanently delete (admin only)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a use case.
    
    **Permissions:**
    - Only the owner or an admin can delete a use case
    
    **Delete modes:**
    - Soft delete (default): Archives the use case
    - Hard delete: Permanently removes the use case (admin only)
    """
    # Only admins can hard delete
    if hard_delete and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can permanently delete use cases"
        )
    
    result = await UseCaseService.delete_use_case(
        db,
        use_case_id=use_case_id,
        current_user=current_user,
        hard_delete=hard_delete
    )
    
    return result


@router.post("/drafts", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def save_draft(
    draft_in: DraftSave,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Save a use case draft for multi-step form.
    
    **Features:**
    - Saves partial use case data
    - Tracks current step in multi-step form
    - Auto-expires after 30 days
    - One draft per user (overwrites existing)
    """
    draft = await UseCaseService.save_draft(
        db,
        draft_in=draft_in,
        current_user=current_user
    )
    
    return DraftResponse(
        draft_id=draft.id,
        use_case_id=draft.use_case_id,
        saved_at=draft.last_saved,
        expires_at=draft.expires_at
    )


@router.get("/drafts/current", response_model=Optional[DraftResponse])
async def get_current_draft(
    use_case_id: Optional[str] = Query(None, description="Get draft for specific use case"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current user's draft.
    
    **Features:**
    - Returns the most recent draft for the user
    - Can filter by specific use case ID
    - Returns null if no draft exists
    """
    draft = await UseCaseService.get_draft(
        db,
        current_user=current_user,
        use_case_id=use_case_id
    )
    
    if draft:
        return DraftResponse(
            draft_id=draft.id,
            use_case_id=draft.use_case_id,
            saved_at=draft.last_saved,
            expires_at=draft.expires_at
        )
    
    return None


@router.post("/{use_case_id}/like", response_model=LikeResponse)
async def toggle_like(
    use_case_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Toggle like status for a use case.
    
    **Features:**
    - Like if not already liked
    - Unlike if already liked
    - Returns current like status and total count
    """
    result = await UseCaseService.toggle_like(
        db,
        use_case_id=use_case_id,
        current_user=current_user
    )
    
    return LikeResponse(**result)


@router.post("/{use_case_id}/save", response_model=SaveResponse)
async def toggle_save(
    use_case_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Toggle save/bookmark status for a use case.
    
    **Features:**
    - Save if not already saved
    - Unsave if already saved
    - Returns current save status and total count
    """
    result = await UseCaseService.toggle_save(
        db,
        use_case_id=use_case_id,
        current_user=current_user
    )
    
    return SaveResponse(**result)


@router.get("/trending", response_model=TrendingResponse)
async def get_trending_use_cases(
    period: str = Query("week", regex="^(day|week|month)$", description="Trending period"),
    limit: int = Query(10, ge=1, le=50, description="Number of trending items"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get trending use cases based on views, likes, and recency.
    
    **Periods:**
    - day: Trending in the last 24 hours
    - week: Trending in the last 7 days (default)
    - month: Trending in the last 30 days
    
    **Trending Algorithm:**
    - Combines view count, like count, and publication recency
    - Weighted scoring system
    - Respects visibility settings
    """
    result = await UseCaseService.get_trending_use_cases(
        db,
        period=period,
        limit=limit,
        current_user=current_user
    )
    
    return TrendingResponse(**result)


@router.get("/search/suggestions", response_model=SuggestionsResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Search query for suggestions"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get search suggestions based on query.
    
    **Features:**
    - Title and tag-based suggestions
    - Company and technology suggestions
    - Popular search terms
    - Real-time suggestions based on existing data
    
    **Use cases:**
    - Autocomplete for search boxes
    - Query refinement suggestions
    - Popular search discovery
    """
    result = await UseCaseService.get_search_suggestions(
        db,
        query=q,
        limit=limit,
        current_user=current_user
    )
    
    return SuggestionsResponse(**result)


@router.get("/categories/stats")
async def get_category_statistics(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get statistics about use case categories.
    
    **Returns:**
    - Count per category
    - Average ROI per category
    - Popular technologies per category
    - Recent activity per category
    
    **Use cases:**
    - Dashboard analytics
    - Category selection UI
    - Market insights
    """
    result = await UseCaseService.get_category_statistics(
        db,
        current_user=current_user
    )
    
    return result


@router.get("/featured", response_model=UseCaseListResponse)
async def get_featured_use_cases(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get featured use cases with enhanced presentation.
    
    **Features:**
    - Only verified and featured use cases
    - Enhanced metadata and images
    - Curated order based on business value
    - Optimized for homepage and highlights
    
    **Presentation:**
    - High-quality thumbnails
    - Key performance metrics highlighted
    - Success story format
    """
    filters = UseCaseFilters(
        page=page,
        page_size=page_size,
        featured=True,
        verified=True,
        sort_by="roi",
        order="desc"
    )
    
    result = await UseCaseService.browse_use_cases(
        db,
        filters=filters,
        current_user=current_user
    )
    
    return UseCaseListResponse(**result)