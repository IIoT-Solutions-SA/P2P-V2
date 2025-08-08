"""Use Cases API endpoints."""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.rbac import get_current_user as get_current_active_user, get_current_user_optional
from app.core.rbac import require_organization_access
from app.db.mongodb import get_mongodb
from app.models.user import User
from app.models.use_case import UseCaseStatus, UseCaseVisibility
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
async def get_use_case_details(
    use_case_id: str,
    track_view: bool = Query(True, description="Track this view for analytics"),
    include_related: bool = Query(True, description="Include related use cases"),
    include_engagement: bool = Query(True, description="Include engagement metrics"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get comprehensive details about a specific use case.
    
    **Features:**
    - Complete use case information including all sections
    - Smart view tracking with duplicate prevention
    - Related use cases with similarity scoring
    - Engagement metrics (views, likes, saves)
    - Media gallery with optimized loading
    - Implementation timeline and phases
    - Results metrics and ROI analysis
    - Vendor and technology details
    - Location and contact information
    
    **Access Control:**
    - Public: Available to all users
    - Organization: Members of same organization
    - Private: Only owner and admins
    
    **Performance:**
    - Optimized data loading with selective inclusion
    - Cached related use cases
    - Compressed media metadata
    """
    result = await UseCaseService.get_use_case_details(
        db,
        use_case_id=use_case_id,
        current_user=current_user,
        track_view=track_view,
        include_related=include_related,
        include_engagement=include_engagement
    )
    
    return result


@router.get("/{use_case_id}/related", response_model=UseCaseListResponse)
async def get_related_use_cases(
    use_case_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of related use cases"),
    similarity_threshold: float = Query(0.3, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get use cases related to the specified use case.
    
    **Similarity Algorithm:**
    - Technology overlap scoring
    - Industry and category matching
    - ROI and metrics similarity
    - Geographic proximity (if available)
    - User engagement patterns
    
    **Features:**
    - Configurable similarity threshold
    - Respects access permissions
    - Excludes the original use case
    - Sorted by relevance score
    
    **Use Cases:**
    - "You might also like" recommendations
    - Cross-selling opportunities
    - Learning from similar implementations
    """
    result = await UseCaseService.get_related_use_cases(
        db,
        use_case_id=use_case_id,
        current_user=current_user,
        limit=limit,
        similarity_threshold=similarity_threshold
    )
    
    return UseCaseListResponse(**result)


@router.get("/{use_case_id}/engagement")
async def get_use_case_engagement(
    use_case_id: str,
    include_timeline: bool = Query(True, description="Include engagement timeline"),
    days_back: int = Query(30, ge=1, le=365, description="Days of history to include"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get detailed engagement metrics for a use case.
    
    **Metrics:**
    - Total views, likes, saves, shares
    - View timeline (daily/weekly breakdown)
    - Geographic distribution of views
    - User segment analysis (roles, industries)
    - Referrer sources and discovery methods
    - Peak engagement times and patterns
    
    **Access Control:**
    - Basic metrics: Available to all viewers
    - Detailed analytics: Owner and admins only
    - Anonymized data for organization members
    
    **Use Cases:**
    - Content performance analysis
    - Engagement optimization
    - ROI measurement for content creation
    """
    # Check if user has access to detailed analytics
    can_view_detailed = False
    if current_user:
        use_case = await UseCaseService.get_use_case_basic(db, use_case_id)
        if use_case and (
            str(current_user.id) == use_case.published_by.user_id or 
            current_user.role == 'admin'
        ):
            can_view_detailed = True
    
    result = await UseCaseService.get_use_case_engagement(
        db,
        use_case_id=use_case_id,
        current_user=current_user,
        include_timeline=include_timeline,
        days_back=days_back,
        detailed_analytics=can_view_detailed
    )
    
    return result


@router.get("/{use_case_id}/versions")
async def get_use_case_versions(
    use_case_id: str,
    include_drafts: bool = Query(False, description="Include draft versions"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get version history for a use case.
    
    **Features:**
    - Published version history
    - Draft versions (owner/admin only)
    - Change tracking and diff support
    - Restore capability for previous versions
    
    **Permissions:**
    - View history: Owner and admins only
    - Draft versions: Owner and admins only
    - Version comparison: Full access for owners
    
    **Use Cases:**
    - Content audit trails
    - Version comparison and rollback
    - Collaboration history tracking
    """
    result = await UseCaseService.get_use_case_versions(
        db,
        use_case_id=use_case_id,
        current_user=current_user,
        include_drafts=include_drafts
    )
    
    return result


@router.post("/{use_case_id}/report")
async def report_use_case(
    use_case_id: str,
    reason: str = Query(..., description="Reason for reporting"),
    details: Optional[str] = Query(None, description="Additional details"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Report a use case for review.
    
    **Report Reasons:**
    - inappropriate_content: Contains inappropriate material
    - spam: Spam or promotional content
    - misinformation: Contains false or misleading information
    - copyright: Copyright infringement
    - duplicate: Duplicate content
    - privacy: Privacy concerns
    - other: Other reason (requires details)
    
    **Process:**
    - Creates report record for admin review
    - Notifies moderation team
    - Anonymous reporting supported
    - Prevents duplicate reports from same user
    
    **Moderation:**
    - Admin review queue
    - Automated flagging for obvious violations
    - User notification system for report status
    """
    result = await UseCaseService.report_use_case(
        db,
        use_case_id=use_case_id,
        reporter_user_id=str(current_user.id),
        reason=reason,
        details=details
    )
    
    return result


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


@router.post("/{use_case_id}/publish", response_model=UseCaseResponse)
async def publish_use_case(
    use_case_id: str,
    visibility: UseCaseVisibility = Query(UseCaseVisibility.ORGANIZATION, description="Visibility level"),
    notify_followers: bool = Query(False, description="Notify followers about publication"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Publish a draft use case.
    
    **Publishing Process:**
    - Validates all required fields are complete
    - Sets status to published with timestamp
    - Configures visibility (public/organization/private)
    - Optionally notifies followers
    - Creates publication activity log
    
    **Validation:**
    - Title, description, results are required
    - At least one metric must be defined
    - Media files are validated if present
    
    **Permissions:**
    - Only the owner or an admin can publish
    - Organization approval may be required for public visibility
    
    **Notifications:**
    - Email notification to organization admins (if public)
    - Activity feed update for followers
    - Dashboard notification for author
    """
    result = await UseCaseService.publish_use_case(
        db,
        use_case_id=use_case_id,
        visibility=visibility,
        notify_followers=notify_followers,
        current_user=current_user
    )
    
    return UseCaseResponse(**result)


@router.post("/{use_case_id}/unpublish", response_model=UseCaseResponse)
async def unpublish_use_case(
    use_case_id: str,
    reason: Optional[str] = Query(None, description="Reason for unpublishing"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unpublish a published use case (revert to draft).
    
    **Process:**
    - Changes status from published to draft
    - Maintains all content and media
    - Removes from public/organization listings
    - Logs unpublishing reason
    
    **Use Cases:**
    - Content needs major updates
    - Compliance or accuracy issues
    - Temporary removal for review
    
    **Permissions:**
    - Owner or admin only
    - Reason required for audit trail
    """
    result = await UseCaseService.unpublish_use_case(
        db,
        use_case_id=use_case_id,
        reason=reason,
        current_user=current_user
    )
    
    return UseCaseResponse(**result)


@router.post("/{use_case_id}/duplicate", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_use_case(
    use_case_id: str,
    new_title: Optional[str] = Query(None, description="Title for duplicated use case"),
    as_template: bool = Query(False, description="Create as template without specific data"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Duplicate an existing use case.
    
    **Features:**
    - Creates a copy with new ID
    - Optionally rename the duplicate
    - Can create as template (structure only)
    - Maintains media references
    - Sets status to draft
    
    **Template Mode:**
    - Keeps structure and categories
    - Clears company-specific data
    - Removes metrics and results
    - Useful for creating similar use cases
    
    **Permissions:**
    - Public use cases: Any authenticated user can duplicate
    - Organization use cases: Organization members only
    - Private use cases: Owner only
    """
    result = await UseCaseService.duplicate_use_case(
        db,
        use_case_id=use_case_id,
        new_title=new_title,
        as_template=as_template,
        current_user=current_user
    )
    
    return UseCaseResponse(**result)


@router.post("/{use_case_id}/transfer-ownership")
async def transfer_ownership(
    use_case_id: str,
    new_owner_id: str = Query(..., description="User ID of new owner"),
    transfer_reason: str = Query(..., description="Reason for ownership transfer"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Transfer ownership of a use case to another user.
    
    **Process:**
    - Validates new owner exists and is in same organization
    - Updates published_by information
    - Maintains all content and history
    - Creates audit log entry
    - Notifies both parties
    
    **Restrictions:**
    - New owner must be in same organization
    - Cannot transfer to inactive users
    - Audit trail maintained for compliance
    
    **Permissions:**
    - Current owner or admin only
    - Organization admin approval may be required
    """
    result = await UseCaseService.transfer_ownership(
        db,
        use_case_id=use_case_id,
        new_owner_id=new_owner_id,
        transfer_reason=transfer_reason,
        current_user=current_user
    )
    
    return result


@router.get("/my/use-cases", response_model=UseCaseListResponse)
async def get_my_use_cases(
    status: Optional[UseCaseStatus] = Query(None, description="Filter by status"),
    visibility: Optional[UseCaseVisibility] = Query(None, description="Filter by visibility"),
    sort_by: str = Query("updated", regex="^(created|updated|views|likes)$", description="Sort field"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all use cases created by the current user.
    
    **Features:**
    - Shows all user's use cases (draft, published, archived)
    - Filterable by status and visibility
    - Sortable by date, views, or likes
    - Includes basic statistics
    
    **Use Cases:**
    - User dashboard view
    - Content management interface
    - Personal analytics review
    
    **Statistics Included:**
    - Total views and engagement
    - Publication status
    - Last updated timestamp
    """
    result = await UseCaseService.get_user_use_cases(
        db,
        user_id=str(current_user.id),
        status=status,
        visibility=visibility,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )
    
    return UseCaseListResponse(**result)


@router.get("/organization/use-cases", response_model=UseCaseListResponse)
async def get_organization_use_cases(
    status: Optional[UseCaseStatus] = Query(None, description="Filter by status"),
    author_id: Optional[str] = Query(None, description="Filter by author"),
    date_from: Optional[datetime] = Query(None, description="Filter by creation date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by creation date to"),
    sort_by: str = Query("updated", regex="^(created|updated|views|likes|author)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all use cases from the user's organization.
    
    **Features:**
    - Shows all organization use cases
    - Filterable by status, author, date range
    - Sortable by multiple criteria
    - Includes author information
    
    **Use Cases:**
    - Organization content overview
    - Team collaboration view
    - Content approval workflow
    - Organization analytics
    
    **Permissions:**
    - All organization members can view
    - Detailed analytics for admins only
    """
    result = await UseCaseService.get_organization_use_cases(
        db,
        organization_id=str(current_user.organization_id),
        status=status,
        author_id=author_id,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        current_user=current_user
    )
    
    return UseCaseListResponse(**result)


@router.post("/bulk/archive")
async def bulk_archive_use_cases(
    use_case_ids: List[str] = Query(..., description="List of use case IDs to archive"),
    archive_reason: Optional[str] = Query(None, description="Reason for archiving"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Archive multiple use cases at once.
    
    **Features:**
    - Batch archive operation
    - Maintains data but removes from active listings
    - Creates audit log for each item
    - Returns success/failure for each ID
    
    **Use Cases:**
    - Seasonal content cleanup
    - Compliance-driven archiving
    - Bulk content management
    
    **Permissions:**
    - User can only archive their own use cases
    - Admins can archive any organization use case
    """
    result = await UseCaseService.bulk_archive_use_cases(
        db,
        use_case_ids=use_case_ids,
        archive_reason=archive_reason,
        current_user=current_user
    )
    
    return result


@router.post("/bulk/delete")
async def bulk_delete_use_cases(
    use_case_ids: List[str] = Query(..., description="List of use case IDs to delete"),
    hard_delete: bool = Query(False, description="Permanently delete (admin only)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete multiple use cases at once.
    
    **Features:**
    - Batch delete operation
    - Soft delete by default (recoverable)
    - Hard delete option for admins
    - Returns success/failure for each ID
    
    **Soft Delete:**
    - Marks as deleted but retains data
    - Can be recovered within 30 days
    
    **Hard Delete:**
    - Permanently removes data
    - Deletes associated media files
    - Admin only operation
    
    **Permissions:**
    - Users can soft delete their own use cases
    - Hard delete requires admin role
    """
    if hard_delete and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can permanently delete use cases"
        )
    
    result = await UseCaseService.bulk_delete_use_cases(
        db,
        use_case_ids=use_case_ids,
        hard_delete=hard_delete,
        current_user=current_user
    )
    
    return result


@router.post("/bulk/update-visibility")
async def bulk_update_visibility(
    use_case_ids: List[str] = Query(..., description="List of use case IDs to update"),
    visibility: UseCaseVisibility = Query(..., description="New visibility level"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update visibility for multiple use cases.
    
    **Features:**
    - Batch visibility update
    - Validates permissions for each item
    - Creates audit log entries
    - Returns success/failure for each ID
    
    **Use Cases:**
    - Making multiple cases public after review
    - Restricting access for compliance
    - Organization-wide visibility changes
    
    **Permissions:**
    - Users can update their own use cases
    - Public visibility may require admin approval
    """
    result = await UseCaseService.bulk_update_visibility(
        db,
        use_case_ids=use_case_ids,
        visibility=visibility,
        current_user=current_user
    )
    
    return result


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


@router.post("/search/advanced")
async def advanced_search(
    query: str = Query(..., description="Search query"),
    filters: Optional[str] = Query(None, description="JSON-encoded filters"),
    facets: Optional[List[str]] = Query(None, description="Facets to include: category, industry, technologies, year"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Advanced search with faceted results and ranking.
    
    **Features:**
    - Full-text search across multiple fields
    - Faceted search with aggregations
    - Search result ranking and scoring
    - Filters for date range, category, industry, ROI
    
    **Facets available:**
    - category: Category distribution
    - industry: Industry distribution
    - technologies: Technology distribution
    - year: Year distribution
    
    **Ranking factors:**
    - Title match (highest weight)
    - Tag match
    - Technology match
    - Description match
    - View count
    - Publication date
    """
    import json
    
    # Parse filters if provided
    parsed_filters = None
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filters format. Must be valid JSON."
            )
    
    result = await UseCaseService.advanced_search(
        db,
        query=query,
        filters=parsed_filters,
        facets=facets,
        page=page,
        page_size=page_size,
        current_user=current_user
    )
    
    # Track search for analytics
    await UseCaseService.track_search(
        db,
        query=query,
        filters=parsed_filters,
        result_count=result.get("total", 0),
        current_user=current_user
    )
    
    return result


@router.post("/search/save")
async def save_search(
    query: str = Query(..., description="Search query to save"),
    name: str = Query(..., description="Name for the saved search"),
    filters: Optional[str] = Query(None, description="JSON-encoded filters"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Save a search query for later use.
    
    **Features:**
    - Save complex search queries
    - Include filters and settings
    - Quick access from dashboard
    - Usage tracking
    """
    import json
    
    # Parse filters if provided
    parsed_filters = None
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filters format. Must be valid JSON."
            )
    
    result = await UseCaseService.save_search(
        db,
        query=query,
        filters=parsed_filters,
        name=name,
        current_user=current_user
    )
    
    return result


@router.get("/search/saved")
async def get_saved_searches(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's saved searches.
    
    **Returns:**
    - List of saved searches
    - Usage statistics
    - Last used timestamp
    - Quick access links
    """
    searches = await UseCaseService.get_saved_searches(
        db,
        current_user=current_user
    )
    
    return {"searches": searches}


@router.get("/search/saved/{search_id}/execute")
async def execute_saved_search(
    search_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute a saved search.
    
    **Features:**
    - Quick execution of saved searches
    - Updates usage statistics
    - Maintains original filters
    - Paginated results
    """
    result = await UseCaseService.execute_saved_search(
        db,
        search_id=search_id,
        page=page,
        page_size=page_size,
        current_user=current_user
    )
    
    return result


@router.get("/search/history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=50, description="Number of history items"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's search history.
    
    **Features:**
    - Recent search queries
    - Result counts
    - Search timestamps
    - Quick re-run capability
    """
    history = await UseCaseService.get_search_history(
        db,
        current_user=current_user,
        limit=limit
    )
    
    return {"history": history}


@router.get("/location/filter")
async def get_use_cases_by_location(
    city: Optional[str] = Query(None, description="Filter by city"),
    region: Optional[str] = Query(None, description="Filter by region/state"),
    country: str = Query("Saudi Arabia", description="Filter by country"),
    radius_km: Optional[float] = Query(None, ge=1, le=500, description="Search radius in kilometers"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Center latitude for radius search"),
    lng: Optional[float] = Query(None, ge=-180, le=180, description="Center longitude for radius search"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get use cases filtered by location.
    
    **Features:**
    - Filter by city, region, or country
    - Geospatial search with radius from center point
    - Distance calculation for each result
    - Respects visibility permissions
    
    **Geospatial Search:**
    - Provide lat, lng, and radius_km for radius-based search
    - Results sorted by distance from center point
    - Distance included in response for each use case
    
    **Use Cases:**
    - Find implementations in specific cities
    - Discover nearby success stories
    - Regional market analysis
    """
    # Build center coordinates if provided
    center_coordinates = None
    if lat is not None and lng is not None:
        center_coordinates = {"lat": lat, "lng": lng}
    
    result = await UseCaseService.get_use_cases_by_location(
        db,
        city=city,
        region=region,
        country=country,
        radius_km=radius_km,
        center_coordinates=center_coordinates,
        page=page,
        page_size=page_size,
        current_user=current_user
    )
    
    return result


@router.get("/location/statistics")
async def get_location_statistics(
    group_by: str = Query("city", regex="^(city|region|country)$", description="Group statistics by"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get statistics about use case locations.
    
    **Features:**
    - Distribution of use cases by location
    - Average ROI per location
    - Total engagement metrics per location
    - Popular categories per location
    
    **Group By Options:**
    - city: City-level statistics
    - region: Region/state-level statistics  
    - country: Country-level statistics
    
    **Use Cases:**
    - Market analysis and trends
    - Regional performance comparison
    - Investment opportunity identification
    """
    result = await UseCaseService.get_location_statistics(
        db,
        group_by=group_by,
        current_user=current_user
    )
    
    return result


@router.patch("/{use_case_id}/location")
async def update_use_case_location(
    use_case_id: str,
    city: Optional[str] = Query(None, description="City name"),
    region: Optional[str] = Query(None, description="Region/state name"),
    country: Optional[str] = Query(None, description="Country name"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lng: Optional[float] = Query(None, ge=-180, le=180, description="Longitude"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update location information for a use case.
    
    **Features:**
    - Update city, region, country
    - Set GPS coordinates for geospatial features
    - Validation of coordinate ranges
    - Permission-based access control
    
    **Permissions:**
    - Only the owner or admin can update location
    
    **Coordinates:**
    - Latitude: -90 to 90
    - Longitude: -180 to 180
    - Used for radius searches and distance calculations
    """
    # Build coordinates if provided
    coordinates = None
    if lat is not None and lng is not None:
        coordinates = {"lat": lat, "lng": lng}
    
    result = await UseCaseService.update_use_case_location(
        db,
        use_case_id=use_case_id,
        city=city,
        region=region,
        country=country,
        coordinates=coordinates,
        current_user=current_user
    )
    
    return result


@router.get("/{use_case_id}/nearby")
async def get_nearby_use_cases(
    use_case_id: str,
    radius_km: float = Query(50, ge=1, le=500, description="Search radius in kilometers"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get use cases near a specific use case.
    
    **Features:**
    - Find use cases within radius of reference case
    - Distance calculation from reference point
    - Sorted by proximity
    - Excludes the reference use case itself
    
    **Requirements:**
    - Reference use case must have coordinates
    - Results respect visibility permissions
    
    **Use Cases:**
    - Find similar implementations nearby
    - Regional clustering analysis
    - Collaboration opportunities
    """
    result = await UseCaseService.get_nearby_use_cases(
        db,
        use_case_id=use_case_id,
        radius_km=radius_km,
        limit=limit,
        current_user=current_user
    )
    
    return result


@router.post("/location/create-index")
async def create_location_index(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create geospatial indexes for location queries.
    
    **Admin Only**: This endpoint requires admin privileges.
    
    **Creates:**
    - 2dsphere index for coordinate-based queries
    - Text indexes for city and region searches
    
    **Note:**
    - Run once during initial setup
    - Improves performance of location-based queries
    """
    # Check admin permission
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create indexes"
        )
    
    result = await UseCaseService.create_location_index(db)
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