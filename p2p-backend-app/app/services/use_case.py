"""Business logic service for Use Cases."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.crud.use_case import get_use_case_crud, CRUDUseCase
from app.models.use_case import UseCase, UseCaseStatus, UseCaseVisibility, UseCaseDraft
from app.models.user import User
from app.schemas.use_case import (
    UseCaseCreate,
    UseCaseUpdate,
    UseCaseFilters,
    UseCaseBrief,
    UseCaseDetail,
    DraftSave
)

logger = logging.getLogger(__name__)


class UseCaseService:
    """Service layer for Use Case operations."""
    
    @staticmethod
    async def create_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_in: UseCaseCreate,
        current_user: User
    ) -> UseCase:
        """Create a new use case."""
        try:
            # Validate user has permission to create use cases
            if not current_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Inactive users cannot create use cases"
                )
            
            # Get CRUD instance
            crud = get_use_case_crud(db)
            
            # Create use case
            use_case = await crud.create(
                obj_in=use_case_in,
                user_id=str(current_user.id),
                user_name=f"{current_user.first_name} {current_user.last_name}",
                user_title=current_user.title,
                user_email=current_user.email,
                organization_id=str(current_user.organization_id)
            )
            
            logger.info(f"User {current_user.id} created use case {use_case.id}")
            return use_case
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating use case: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create use case"
            )
    
    @staticmethod
    async def get_use_case_basic(
        db: AsyncIOMotorDatabase,
        use_case_id: str
    ) -> Optional[UseCase]:
        """Get basic use case info for permission checks."""
        try:
            crud = get_use_case_crud(db)
            return await crud.get(use_case_id=use_case_id)
        except Exception:
            return None
    
    @staticmethod
    async def get_use_case_details(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: Optional[User] = None,
        track_view: bool = True,
        include_related: bool = True,
        include_engagement: bool = True
    ) -> UseCaseDetail:
        """Get comprehensive use case details with enhanced features."""
        try:
            crud = get_use_case_crud(db)
            
            # Get use case with full projection
            use_case = await crud.get(use_case_id=use_case_id)
            
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check visibility permissions
            if use_case.visibility == UseCaseVisibility.PRIVATE:
                if not current_user or str(current_user.id) != use_case.published_by.user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to view this use case"
                    )
            
            elif use_case.visibility == UseCaseVisibility.ORGANIZATION:
                if not current_user or str(current_user.organization_id) != use_case.organization_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="This use case is only visible to organization members"
                    )
            
            # Smart view tracking with duplicate prevention
            if track_view:
                await UseCaseService._track_smart_view(
                    crud,
                    use_case_id=use_case_id,
                    viewer_id=str(current_user.id) if current_user else None,
                    organization_id=str(current_user.organization_id) if current_user else None
                )
            
            # Get related use cases with similarity scoring
            related = []
            if include_related:
                related = await UseCaseService._get_related_use_cases_smart(
                    db, use_case, current_user, limit=5
                )
            
            # Get engagement metrics if requested
            engagement_data = {}
            if include_engagement:
                engagement_data = await UseCaseService._get_engagement_summary(
                    crud, use_case_id, current_user
                )
            
            # Convert to detail schema
            use_case_dict = use_case.model_dump()
            
            # Remove sensitive information if not owner
            is_owner = current_user and str(current_user.id) == use_case.published_by.user_id
            if not is_owner:
                use_case_dict["published_by"].pop("email", None)
            
            # Add enhanced data
            use_case_dict["related_use_cases"] = related
            if engagement_data:
                use_case_dict.update(engagement_data)
            
            logger.info(
                f"Retrieved use case details {use_case_id} for user {current_user.id if current_user else 'guest'}"
            )
            
            return UseCaseDetail(**use_case_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting use case details {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get use case details"
            )
    
    @staticmethod
    async def _track_smart_view(
        crud: 'CRUDUseCase',
        use_case_id: str,
        viewer_id: Optional[str],
        organization_id: Optional[str]
    ):
        """Track view with duplicate prevention and session management."""
        try:
            from datetime import timedelta
            
            # Check if this user already viewed this use case recently (last hour)
            recent_cutoff = datetime.utcnow() - timedelta(hours=1)
            
            if viewer_id:
                # Check for recent view by this user
                recent_view = await crud.views.find_one({
                    "use_case_id": use_case_id,
                    "viewer_id": viewer_id,
                    "viewed_at": {"$gte": recent_cutoff}
                })
                
                if recent_view:
                    # Don't track duplicate view, but update timestamp
                    await crud.views.update_one(
                        {"_id": recent_view["_id"]},
                        {"$set": {"viewed_at": datetime.utcnow()}}
                    )
                    return
            
            # Track the view
            await crud.track_view(
                use_case_id=use_case_id,
                viewer_id=viewer_id,
                organization_id=organization_id
            )
            
        except Exception as e:
            # Don't fail the request if view tracking fails
            logger.warning(f"Failed to track view for use case {use_case_id}: {e}")
    
    @staticmethod
    async def _get_related_use_cases_smart(
        db: AsyncIOMotorDatabase,
        use_case: UseCase,
        current_user: Optional[User],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get related use cases using similarity algorithm."""
        try:
            crud = get_use_case_crud(db)
            
            # Build query for potential related cases
            base_query = {
                "status": "published",
                "id": {"$ne": use_case.id}  # Exclude current use case
            }
            
            # Apply visibility filters
            if current_user:
                base_query["$or"] = [
                    {"visibility": "public"},
                    {
                        "$and": [
                            {"visibility": "organization"},
                            {"organization_id": str(current_user.organization_id)}
                        ]
                    }
                ]
            else:
                base_query["visibility"] = "public"
            
            # Use MongoDB aggregation for similarity scoring
            pipeline = [
                {"$match": base_query},
                {
                    "$addFields": {
                        "similarity_score": {
                            "$add": [
                                # Category match (weight: 3)
                                {
                                    "$cond": [
                                        {"$eq": ["$category", use_case.category.value]},
                                        3,
                                        0
                                    ]
                                },
                                # Industry match (weight: 2)
                                {
                                    "$cond": [
                                        {"$eq": ["$industry", use_case.industry]},
                                        2,
                                        0
                                    ]
                                },
                                # Technology overlap (weight: 1 per match, max 3)
                                {
                                    "$min": [
                                        3,
                                        {
                                            "$size": {
                                                "$setIntersection": [
                                                    "$technologies",
                                                    use_case.technologies
                                                ]
                                            }
                                        }
                                    ]
                                },
                                # Similar ROI range (weight: 1)
                                {
                                    "$cond": [
                                        {
                                            "$and": [
                                                {"$ne": ["$results.roi.percentage", None]},
                                                {"$ne": [use_case.results.roi.percentage if use_case.results and use_case.results.roi else None, None]},
                                                {
                                                    "$lte": [
                                                        {
                                                            "$abs": {
                                                                "$subtract": [
                                                                    "$results.roi.percentage",
                                                                    use_case.results.roi.percentage if use_case.results and use_case.results.roi else 0
                                                                ]
                                                            }
                                                        },
                                                        20  # Within 20% ROI difference
                                                    ]
                                                }
                                            ]
                                        },
                                        1,
                                        0
                                    ]
                                }
                            ]
                        }
                    }
                },
                {"$match": {"similarity_score": {"$gte": 1}}},  # Minimum threshold
                {"$sort": {"similarity_score": -1, "metrics.views": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "id": 1, "title": 1, "category": 1, "company": 1,
                        "description": {"$substr": ["$description", 0, 150]},
                        "results.roi.percentage": 1,
                        "metrics.views": 1, "metrics.likes": 1,
                        "media": {"$slice": ["$media", 1]},
                        "similarity_score": 1
                    }
                }
            ]
            
            cursor = crud.collection.aggregate(pipeline)
            related_docs = await cursor.to_list(length=limit)
            
            # Convert to response format
            related = []
            for doc in related_docs:
                thumbnail = None
                if doc.get('media'):
                    first_media = doc['media'][0]
                    thumbnail = first_media.get('thumbnail_url') or first_media.get('url')
                
                related.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "company": doc["company"],
                    "description": doc["description"],
                    "roi_percentage": doc.get("results", {}).get("roi", {}).get("percentage"),
                    "views": doc.get("metrics", {}).get("views", 0),
                    "likes": doc.get("metrics", {}).get("likes", 0),
                    "thumbnail": thumbnail,
                    "similarity_score": doc["similarity_score"]
                })
            
            return related
            
        except Exception as e:
            logger.warning(f"Failed to get related use cases: {e}")
            return []
    
    @staticmethod
    async def _get_engagement_summary(
        crud: 'CRUDUseCase',
        use_case_id: str,
        current_user: Optional[User]
    ) -> Dict[str, Any]:
        """Get engagement metrics summary."""
        try:
            # Get basic engagement counts
            views_count = await crud.views.count_documents({"use_case_id": use_case_id})
            likes_count = await crud.likes.count_documents({"use_case_id": use_case_id})
            saves_count = await crud.saves.count_documents({"use_case_id": use_case_id})
            
            # Check user's personal engagement
            user_engagement = {}
            if current_user:
                user_liked = await crud.likes.find_one({
                    "use_case_id": use_case_id,
                    "user_id": str(current_user.id)
                }) is not None
                
                user_saved = await crud.saves.find_one({
                    "use_case_id": use_case_id,
                    "user_id": str(current_user.id)
                }) is not None
                
                user_engagement = {
                    "user_liked": user_liked,
                    "user_saved": user_saved
                }
            
            return {
                "engagement_summary": {
                    "total_views": views_count,
                    "total_likes": likes_count,
                    "total_saves": saves_count,
                    **user_engagement
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to get engagement summary: {e}")
            return {}
    
    @staticmethod
    async def get_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: Optional[User] = None,
        track_view: bool = True
    ) -> UseCaseDetail:
        """Legacy method - redirect to enhanced version."""
        return await UseCaseService.get_use_case_details(
            db,
            use_case_id=use_case_id,
            current_user=current_user,
            track_view=track_view,
            include_related=True,
            include_engagement=True
        )
    
    @staticmethod
    async def browse_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        filters: UseCaseFilters,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Browse use cases with advanced filtering, sorting, and pagination."""
        try:
            crud = get_use_case_crud(db)
            
            # Determine user access context
            current_user_org_id = str(current_user.organization_id) if current_user else None
            is_guest_user = current_user is None
            
            # Get use cases with enhanced filtering
            use_cases, total = await crud.get_multi(
                filters=filters,
                current_user_org_id=current_user_org_id,
                is_guest_user=is_guest_user
            )
            
            # Convert to brief format for list view
            data = []
            for uc in use_cases:
                try:
                    # Get first thumbnail if available
                    thumbnail = None
                    if uc.media:
                        first_media = uc.media[0]
                        thumbnail = getattr(first_media, 'thumbnail_url', None) or getattr(first_media, 'url', None)
                    
                    # Extract key metric for results preview
                    key_metric = None
                    roi_percentage = None
                    timeframe = None
                    
                    if uc.results:
                        timeframe = getattr(uc.results, 'timeframe', None)
                        
                        if uc.results.metrics:
                            first_metric = uc.results.metrics[0]
                            key_metric = f"{first_metric.name}: {first_metric.value}"
                        
                        if uc.results.roi:
                            roi_percentage = getattr(uc.results.roi, 'percentage', None)
                    
                    # Build brief use case data
                    brief_data = {
                        "id": uc.id,
                        "title": uc.title,
                        "company": uc.company,
                        "industry": uc.industry,
                        "category": uc.category,
                        "description": (
                            uc.description[:200] + "..."
                            if len(uc.description) > 200
                            else uc.description
                        ),
                        "results": {
                            "timeframe": timeframe,
                            "key_metric": key_metric,
                            "roi_percentage": roi_percentage
                        },
                        "thumbnail": thumbnail,
                        "tags": getattr(uc, 'tags', []),
                        "verified": (
                            getattr(uc.verification, 'status', None) == 'verified'
                            if hasattr(uc, 'verification') and uc.verification
                            else False
                        ),
                        "featured": (
                            getattr(uc.featured, 'status', False)
                            if hasattr(uc, 'featured') and uc.featured
                            else False
                        ),
                        "views": (
                            getattr(uc.metrics, 'views', 0)
                            if hasattr(uc, 'metrics') and uc.metrics
                            else 0
                        ),
                        "likes": (
                            getattr(uc.metrics, 'likes', 0)
                            if hasattr(uc, 'metrics') and uc.metrics
                            else 0
                        ),
                        "published_by": {
                            "name": getattr(uc.published_by, 'name', 'Unknown') if uc.published_by else 'Unknown',
                            "title": getattr(uc.published_by, 'title', 'N/A') if uc.published_by else 'N/A'
                        },
                        "published_at": getattr(uc, 'published_at', None)
                    }
                    
                    data.append(brief_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing use case {uc.id} for brief view: {e}")
                    continue
            
            # Calculate pagination metadata
            total_pages = (total + filters.page_size - 1) // filters.page_size if total > 0 else 1
            start_index = (filters.page - 1) * filters.page_size + 1 if total > 0 else 0
            end_index = min(filters.page * filters.page_size, total)
            
            # Prepare filters applied summary
            filters_applied = {}
            for key, value in filters.model_dump().items():
                if value is not None and key not in ["page", "page_size"]:
                    # Handle enum values
                    if hasattr(value, 'value'):
                        filters_applied[key] = value.value
                    else:
                        filters_applied[key] = value
            
            # Build comprehensive response
            response = {
                "data": data,
                "pagination": {
                    "page": filters.page,
                    "page_size": filters.page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": filters.page < total_pages,
                    "has_prev": filters.page > 1,
                    "start_index": start_index,
                    "end_index": end_index
                },
                "filters_applied": filters_applied
            }
            
            logger.info(
                f"Browse use cases returned {len(data)} results "
                f"(page {filters.page}/{total_pages}, total {total})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error browsing use cases with filters {filters.model_dump()}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to browse use cases: {str(e)}"
            )
    
    @staticmethod
    async def update_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        use_case_in: UseCaseUpdate,
        current_user: User
    ) -> UseCase:
        """Update a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Get existing use case
            existing = await crud.get(use_case_id=use_case_id)
            
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check permissions (owner or admin)
            if str(current_user.id) != existing.published_by.user_id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to update this use case"
                )
            
            # Update use case
            updated = await crud.update(
                use_case_id=use_case_id,
                obj_in=use_case_in,
                user_id=str(current_user.id)
            )
            
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update use case"
                )
            
            logger.info(f"User {current_user.id} updated use case {use_case_id}")
            return updated
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update use case"
            )
    
    @staticmethod
    async def delete_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: User,
        hard_delete: bool = False
    ) -> Dict[str, str]:
        """Delete a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Get existing use case
            existing = await crud.get(use_case_id=use_case_id)
            
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check permissions (owner or admin)
            if str(current_user.id) != existing.published_by.user_id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this use case"
                )
            
            # Delete use case
            success = await crud.delete(
                use_case_id=use_case_id,
                soft=not hard_delete
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete use case"
                )
            
            logger.info(f"User {current_user.id} {'hard' if hard_delete else 'soft'} deleted use case {use_case_id}")
            
            return {
                "message": f"Use case {'permanently' if hard_delete else ''} deleted successfully",
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete use case"
            )
    
    @staticmethod
    async def save_draft(
        db: AsyncIOMotorDatabase,
        *,
        draft_in: DraftSave,
        current_user: User
    ) -> UseCaseDraft:
        """Save a use case draft."""
        try:
            crud = get_use_case_crud(db)
            
            # If updating existing use case, check permissions
            if draft_in.use_case_id:
                existing = await crud.get(use_case_id=draft_in.use_case_id)
                if existing and str(current_user.id) != existing.published_by.user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to edit this use case"
                    )
            
            # Save draft
            draft = await crud.save_draft(
                draft_data=draft_in,
                user_id=str(current_user.id),
                organization_id=str(current_user.organization_id)
            )
            
            logger.info(f"User {current_user.id} saved draft")
            return draft
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save draft"
            )
    
    @staticmethod
    async def get_draft(
        db: AsyncIOMotorDatabase,
        *,
        current_user: User,
        use_case_id: Optional[str] = None
    ) -> Optional[UseCaseDraft]:
        """Get user's draft."""
        try:
            crud = get_use_case_crud(db)
            
            draft = await crud.get_draft(
                user_id=str(current_user.id),
                use_case_id=use_case_id
            )
            
            return draft
            
        except Exception as e:
            logger.error(f"Error getting draft: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get draft"
            )
    
    @staticmethod
    async def toggle_like(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: User
    ) -> Dict[str, Any]:
        """Toggle like status for a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Check use case exists
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Toggle like
            liked, total_likes = await crud.toggle_like(
                use_case_id=use_case_id,
                user_id=str(current_user.id),
                organization_id=str(current_user.organization_id)
            )
            
            return {
                "liked": liked,
                "total_likes": total_likes
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error toggling like: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle like"
            )
    
    @staticmethod
    async def get_trending_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        period: str,
        limit: int,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Get trending use cases based on views, likes, and recency."""
        try:
            from datetime import timedelta
            
            # Calculate period start date
            now = datetime.utcnow()
            if period == "day":
                start_date = now - timedelta(days=1)
            elif period == "week":
                start_date = now - timedelta(days=7)
            else:  # month
                start_date = now - timedelta(days=30)
            
            # Build query for trending calculation
            query = {
                "status": "published",
                "published_at": {"$gte": start_date}
            }
            
            # Apply visibility filters
            if current_user:
                query["$or"] = [
                    {"visibility": "public"},
                    {
                        "$and": [
                            {"visibility": "organization"},
                            {"organization_id": str(current_user.organization_id)}
                        ]
                    }
                ]
            else:
                query["visibility"] = "public"
            
            # Aggregate trending score
            pipeline = [
                {"$match": query},
                {
                    "$addFields": {
                        "trending_score": {
                            "$add": [
                                {"$multiply": [{"$ifNull": ["$metrics.views", 0]}, 1]},
                                {"$multiply": [{"$ifNull": ["$metrics.likes", 0]}, 3]},
                                {"$multiply": [
                                    {"$divide": [
                                        {"$subtract": [now, "$published_at"]},
                                        86400000  # milliseconds in a day
                                    ]},
                                    -0.1  # Recency boost (newer = higher score)
                                ]}
                            ]
                        }
                    }
                },
                {"$sort": {"trending_score": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "id": 1, "title": 1, "category": 1, "company": 1,
                        "description": {"$substr": ["$description", 0, 100]},
                        "metrics": 1, "published_at": 1, "trending_score": 1,
                        "media": {"$slice": ["$media", 1]}
                    }
                }
            ]
            
            crud = get_use_case_crud(db)
            cursor = crud.collection.aggregate(pipeline)
            trending = await cursor.to_list(length=limit)
            
            return {
                "trending": trending,
                "period": period
            }
            
        except Exception as e:
            logger.error(f"Error getting trending use cases: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get trending use cases"
            )
    
    @staticmethod
    async def get_search_suggestions(
        db: AsyncIOMotorDatabase,
        *,
        query: str,
        limit: int,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Get search suggestions based on query."""
        try:
            crud = get_use_case_crud(db)
            
            # Build base filter
            base_query = {"status": "published"}
            
            if current_user:
                base_query["$or"] = [
                    {"visibility": "public"},
                    {
                        "$and": [
                            {"visibility": "organization"},
                            {"organization_id": str(current_user.organization_id)}
                        ]
                    }
                ]
            else:
                base_query["visibility"] = "public"
            
            # Aggregation for suggestions
            pipeline = [
                {"$match": base_query},
                {
                    "$project": {
                        "suggestions": {
                            "$concatArrays": [
                                ["$title"],
                                "$tags",
                                "$technologies",
                                ["$company"],
                                ["$industry"]
                            ]
                        }
                    }
                },
                {"$unwind": "$suggestions"},
                {
                    "$match": {
                        "suggestions": {
                            "$regex": query,
                            "$options": "i"
                        }
                    }
                },
                {"$group": {"_id": "$suggestions", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit},
                {"$project": {"suggestion": "$_id", "_id": 0}}
            ]
            
            cursor = crud.collection.aggregate(pipeline)
            suggestions = await cursor.to_list(length=limit)
            
            return {
                "suggestions": [s["suggestion"] for s in suggestions],
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get search suggestions"
            )
    
    @staticmethod
    async def get_category_statistics(
        db: AsyncIOMotorDatabase,
        *,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Get statistics about use case categories."""
        try:
            crud = get_use_case_crud(db)
            
            # Build base query
            base_query = {"status": "published"}
            
            if current_user:
                base_query["$or"] = [
                    {"visibility": "public"},
                    {
                        "$and": [
                            {"visibility": "organization"},
                            {"organization_id": str(current_user.organization_id)}
                        ]
                    }
                ]
            else:
                base_query["visibility"] = "public"
            
            # Aggregate category statistics
            pipeline = [
                {"$match": base_query},
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1},
                        "avg_roi": {"$avg": "$results.roi.percentage"},
                        "total_views": {"$sum": "$metrics.views"},
                        "total_likes": {"$sum": "$metrics.likes"},
                        "technologies": {"$push": "$technologies"},
                        "latest_update": {"$max": "$updated_at"}
                    }
                },
                {
                    "$project": {
                        "category": "$_id",
                        "count": 1,
                        "avg_roi": {"$round": ["$avg_roi", 1]},
                        "total_views": 1,
                        "total_likes": 1,
                        "top_technologies": {
                            "$slice": [
                                {"$reduce": {
                                    "input": "$technologies",
                                    "initialValue": [],
                                    "in": {"$concatArrays": ["$$value", "$$this"]}
                                }},
                                5
                            ]
                        },
                        "latest_update": 1,
                        "_id": 0
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            cursor = crud.collection.aggregate(pipeline)
            statistics = await cursor.to_list(length=None)
            
            return {
                "categories": statistics,
                "total_categories": len(statistics),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting category statistics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get category statistics"
            )
    
    @staticmethod
    async def get_related_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: Optional[User] = None,
        limit: int = 5,
        similarity_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """Get related use cases as standalone endpoint."""
        try:
            crud = get_use_case_crud(db)
            
            # Get the original use case
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check access permissions
            if use_case.visibility == UseCaseVisibility.PRIVATE:
                if not current_user or str(current_user.id) != use_case.published_by.user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to view this use case"
                    )
            elif use_case.visibility == UseCaseVisibility.ORGANIZATION:
                if not current_user or str(current_user.organization_id) != use_case.organization_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="This use case is only visible to organization members"
                    )
            
            # Get related use cases
            related = await UseCaseService._get_related_use_cases_smart(
                db, use_case, current_user, limit
            )
            
            # Filter by similarity threshold
            filtered_related = [
                r for r in related 
                if r.get('similarity_score', 0) >= similarity_threshold
            ]
            
            # Convert to brief format for consistency
            brief_cases = []
            for related_case in filtered_related:
                brief_cases.append({
                    "id": related_case["id"],
                    "title": related_case["title"],
                    "company": related_case["company"],
                    "industry": "N/A",  # Not included in related query
                    "category": related_case["category"],
                    "description": related_case["description"],
                    "results": {
                        "roi_percentage": related_case.get("roi_percentage")
                    },
                    "thumbnail": related_case.get("thumbnail"),
                    "tags": [],  # Not included in related query
                    "verified": False,  # Not included in related query
                    "featured": False,  # Not included in related query
                    "views": related_case["views"],
                    "likes": related_case["likes"],
                    "published_by": {"name": "N/A", "title": "N/A"},
                    "published_at": None,
                    "similarity_score": related_case["similarity_score"]
                })
            
            return {
                "data": brief_cases,
                "pagination": {
                    "page": 1,
                    "page_size": len(brief_cases),
                    "total": len(brief_cases),
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
                },
                "filters_applied": {
                    "related_to": use_case_id,
                    "similarity_threshold": similarity_threshold
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting related use cases for {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get related use cases"
            )
    
    @staticmethod
    async def get_use_case_engagement(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: Optional[User] = None,
        include_timeline: bool = True,
        days_back: int = 30,
        detailed_analytics: bool = False
    ) -> Dict[str, Any]:
        """Get detailed engagement analytics for a use case."""
        try:
            from datetime import timedelta
            
            crud = get_use_case_crud(db)
            
            # Verify use case exists and user has permission
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Basic engagement metrics (available to all)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get engagement counts
            total_views = await crud.views.count_documents({"use_case_id": use_case_id})
            total_likes = await crud.likes.count_documents({"use_case_id": use_case_id})
            total_saves = await crud.saves.count_documents({"use_case_id": use_case_id})
            
            # Period-specific counts
            period_views = await crud.views.count_documents({
                "use_case_id": use_case_id,
                "viewed_at": {"$gte": start_date}
            })
            
            period_likes = await crud.likes.count_documents({
                "use_case_id": use_case_id,
                "liked_at": {"$gte": start_date}
            })
            
            period_saves = await crud.saves.count_documents({
                "use_case_id": use_case_id,
                "saved_at": {"$gte": start_date}
            })
            
            engagement_data = {
                "use_case_id": use_case_id,
                "period_days": days_back,
                "total_engagement": {
                    "views": total_views,
                    "likes": total_likes,
                    "saves": total_saves
                },
                "period_engagement": {
                    "views": period_views,
                    "likes": period_likes,
                    "saves": period_saves
                }
            }
            
            # Add timeline data if requested
            if include_timeline:
                timeline_data = await UseCaseService._get_engagement_timeline(
                    crud, use_case_id, start_date, end_date
                )
                engagement_data["timeline"] = timeline_data
            
            # Add detailed analytics for authorized users
            if detailed_analytics:
                detailed_data = await UseCaseService._get_detailed_analytics(
                    crud, use_case_id, start_date, end_date
                )
                engagement_data["detailed_analytics"] = detailed_data
            
            return engagement_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting engagement data for {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get engagement data"
            )
    
    @staticmethod
    async def _get_engagement_timeline(
        crud: 'CRUDUseCase',
        use_case_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily engagement timeline."""
        try:
            pipeline = [
                {
                    "$match": {
                        "use_case_id": use_case_id,
                        "viewed_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$viewed_at"
                            }
                        },
                        "views": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            cursor = crud.views.aggregate(pipeline)
            timeline_data = await cursor.to_list(length=None)
            
            return [
                {
                    "date": item["_id"],
                    "views": item["views"]
                }
                for item in timeline_data
            ]
            
        except Exception as e:
            logger.warning(f"Failed to get engagement timeline: {e}")
            return []
    
    @staticmethod
    async def _get_detailed_analytics(
        crud: 'CRUDUseCase',
        use_case_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get detailed analytics for authorized users."""
        try:
            # Get viewer organization distribution
            org_pipeline = [
                {
                    "$match": {
                        "use_case_id": use_case_id,
                        "viewed_at": {"$gte": start_date, "$lte": end_date},
                        "organization_id": {"$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": "$organization_id",
                        "views": {"$sum": 1}
                    }
                },
                {"$sort": {"views": -1}},
                {"$limit": 10}
            ]
            
            cursor = crud.views.aggregate(org_pipeline)
            org_distribution = await cursor.to_list(length=10)
            
            # Get peak viewing hours
            hour_pipeline = [
                {
                    "$match": {
                        "use_case_id": use_case_id,
                        "viewed_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {"$hour": "$viewed_at"},
                        "views": {"$sum": 1}
                    }
                },
                {"$sort": {"views": -1}}
            ]
            
            cursor = crud.views.aggregate(hour_pipeline)
            hour_distribution = await cursor.to_list(length=24)
            
            return {
                "top_viewing_organizations": [
                    {"organization_id": item["_id"], "views": item["views"]}
                    for item in org_distribution
                ],
                "peak_hours": [
                    {"hour": item["_id"], "views": item["views"]}
                    for item in hour_distribution
                ]
            }
            
        except Exception as e:
            logger.warning(f"Failed to get detailed analytics: {e}")
            return {}
    
    @staticmethod
    async def get_use_case_versions(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: User,
        include_drafts: bool = False
    ) -> Dict[str, Any]:
        """Get version history for a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Verify use case exists and user has permission
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check permissions (owner or admin only)
            if str(current_user.id) != use_case.published_by.user_id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view version history"
                )
            
            # For now, return basic version info
            # This would be enhanced with actual version tracking
            versions = [
                {
                    "version": "1.0",
                    "created_at": use_case.created_at,
                    "updated_at": use_case.updated_at,
                    "status": use_case.status.value,
                    "changes": "Initial version",
                    "created_by": use_case.published_by.name
                }
            ]
            
            return {
                "use_case_id": use_case_id,
                "versions": versions,
                "total_versions": len(versions)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting versions for {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get version history"
            )
    
    @staticmethod
    async def report_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        reporter_user_id: str,
        reason: str,
        details: Optional[str] = None
    ) -> Dict[str, str]:
        """Report a use case for review."""
        try:
            crud = get_use_case_crud(db)
            
            # Verify use case exists
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check for duplicate reports from same user
            existing_report = await db.use_case_reports.find_one({
                "use_case_id": use_case_id,
                "reporter_user_id": reporter_user_id,
                "status": "pending"
            })
            
            if existing_report:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already reported this use case"
                )
            
            # Create report record
            report_data = {
                "id": str(uuid4()),
                "use_case_id": use_case_id,
                "reporter_user_id": reporter_user_id,
                "reason": reason,
                "details": details,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "reviewed_at": None,
                "reviewed_by": None,
                "resolution": None
            }
            
            await db.use_case_reports.insert_one(report_data)
            
            logger.info(
                f"Use case {use_case_id} reported by user {reporter_user_id} for reason: {reason}"
            )
            
            return {
                "message": "Use case reported successfully",
                "report_id": report_data["id"],
                "status": "pending"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reporting use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to report use case"
            )

    @staticmethod
    async def toggle_save(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: User
    ) -> Dict[str, Any]:
        """Toggle save/bookmark status for a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Check use case exists
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Toggle save
            saved, total_saves = await crud.toggle_save(
                use_case_id=use_case_id,
                user_id=str(current_user.id),
                organization_id=str(current_user.organization_id)
            )
            
            return {
                "saved": saved,
                "total_saves": total_saves
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error toggling save: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle save"
            )
    
    @staticmethod
    async def publish_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        visibility: UseCaseVisibility,
        notify_followers: bool,
        current_user: User
    ) -> Dict[str, Any]:
        """Publish a draft use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Get the use case
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check permissions
            if str(current_user.id) != use_case.published_by.user_id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to publish this use case"
                )
            
            # Validate required fields for publication
            if not use_case.title or not use_case.description:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title and description are required for publication"
                )
            
            if not use_case.results or not use_case.results.metrics:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one result metric is required for publication"
                )
            
            # Update status and visibility
            update_data = {
                "status": UseCaseStatus.PUBLISHED.value,
                "visibility": visibility.value,
                "published_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await crud.collection.update_one(
                {"id": use_case_id},
                {"$set": update_data}
            )
            
            # TODO: Send notifications if requested
            if notify_followers:
                logger.info(f"Would notify followers about use case {use_case_id} publication")
            
            logger.info(f"Published use case {use_case_id} with visibility {visibility.value}")
            
            return {
                "id": use_case_id,
                "title": use_case.title,
                "status": UseCaseStatus.PUBLISHED,
                "message": f"Use case published successfully with {visibility.value} visibility"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error publishing use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to publish use case"
            )
    
    @staticmethod
    async def unpublish_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        reason: Optional[str],
        current_user: User
    ) -> Dict[str, Any]:
        """Unpublish a use case (revert to draft)."""
        try:
            crud = get_use_case_crud(db)
            
            # Get the use case
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check permissions
            if str(current_user.id) != use_case.published_by.user_id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to unpublish this use case"
                )
            
            # Update status
            update_data = {
                "status": UseCaseStatus.DRAFT.value,
                "updated_at": datetime.utcnow(),
                "unpublished_at": datetime.utcnow(),
                "unpublish_reason": reason
            }
            
            await crud.collection.update_one(
                {"id": use_case_id},
                {"$set": update_data}
            )
            
            logger.info(f"Unpublished use case {use_case_id} with reason: {reason}")
            
            return {
                "id": use_case_id,
                "title": use_case.title,
                "status": UseCaseStatus.DRAFT,
                "message": "Use case unpublished and reverted to draft"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error unpublishing use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unpublish use case"
            )
    
    @staticmethod
    async def duplicate_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        new_title: Optional[str],
        as_template: bool,
        current_user: User
    ) -> Dict[str, Any]:
        """Duplicate a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Get the original use case
            original = await crud.get(use_case_id=use_case_id)
            if not original:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check access permissions
            if original.visibility == UseCaseVisibility.PRIVATE:
                if str(current_user.id) != original.published_by.user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to duplicate this private use case"
                    )
            elif original.visibility == UseCaseVisibility.ORGANIZATION:
                if str(current_user.organization_id) != original.organization_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to duplicate this organization use case"
                    )
            
            # Create duplicate
            duplicate_data = original.model_dump()
            duplicate_data["id"] = str(uuid4())
            duplicate_data["title"] = new_title or f"Copy of {original.title}"
            duplicate_data["status"] = UseCaseStatus.DRAFT.value
            duplicate_data["visibility"] = UseCaseVisibility.PRIVATE.value
            duplicate_data["published_by"] = {
                "user_id": str(current_user.id),
                "name": f"{current_user.first_name} {current_user.last_name}",
                "title": current_user.title,
                "email": current_user.email
            }
            duplicate_data["organization_id"] = str(current_user.organization_id)
            duplicate_data["created_at"] = datetime.utcnow()
            duplicate_data["updated_at"] = datetime.utcnow()
            duplicate_data["published_at"] = None
            
            # Clear metrics if template mode
            if as_template:
                duplicate_data["company"] = ""
                duplicate_data["results"] = {"metrics": [], "roi": None}
                duplicate_data["metrics"] = {"views": 0, "likes": 0, "saves": 0}
            
            # Reset engagement metrics
            duplicate_data["metrics"] = {"views": 0, "likes": 0, "saves": 0}
            duplicate_data["verification"] = {"status": "unverified"}
            duplicate_data["featured"] = {"status": False}
            
            # Insert duplicate
            await crud.collection.insert_one(duplicate_data)
            
            logger.info(f"Duplicated use case {use_case_id} as {duplicate_data['id']}")
            
            return {
                "id": duplicate_data["id"],
                "title": duplicate_data["title"],
                "status": UseCaseStatus.DRAFT,
                "message": f"Use case duplicated successfully{'as template' if as_template else ''}"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error duplicating use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to duplicate use case"
            )
    
    @staticmethod
    async def transfer_ownership(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        new_owner_id: str,
        transfer_reason: str,
        current_user: User
    ) -> Dict[str, str]:
        """Transfer ownership of a use case."""
        try:
            crud = get_use_case_crud(db)
            
            # Get the use case
            use_case = await crud.get(use_case_id=use_case_id)
            if not use_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Use case not found"
                )
            
            # Check permissions
            if str(current_user.id) != use_case.published_by.user_id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to transfer ownership"
                )
            
            # Get new owner
            from app.crud.user import get_user_crud
            user_crud = get_user_crud(db)
            new_owner = await user_crud.get(new_owner_id)
            
            if not new_owner:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="New owner not found"
                )
            
            if str(new_owner.organization_id) != use_case.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New owner must be in the same organization"
                )
            
            if not new_owner.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot transfer to inactive user"
                )
            
            # Update ownership
            update_data = {
                "published_by": {
                    "user_id": str(new_owner.id),
                    "name": f"{new_owner.first_name} {new_owner.last_name}",
                    "title": new_owner.title,
                    "email": new_owner.email
                },
                "updated_at": datetime.utcnow(),
                "ownership_transferred_at": datetime.utcnow(),
                "ownership_transfer_reason": transfer_reason,
                "previous_owner_id": use_case.published_by.user_id
            }
            
            await crud.collection.update_one(
                {"id": use_case_id},
                {"$set": update_data}
            )
            
            logger.info(
                f"Transferred ownership of use case {use_case_id} from {current_user.id} to {new_owner_id}"
            )
            
            return {
                "message": "Ownership transferred successfully",
                "use_case_id": use_case_id,
                "new_owner_id": new_owner_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error transferring ownership of {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to transfer ownership"
            )
    
    @staticmethod
    async def get_user_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        user_id: str,
        status: Optional[UseCaseStatus],
        visibility: Optional[UseCaseVisibility],
        sort_by: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """Get all use cases for a specific user."""
        try:
            crud = get_use_case_crud(db)
            
            # Build query
            query = {"published_by.user_id": user_id}
            
            if status:
                query["status"] = status.value
            
            if visibility:
                query["visibility"] = visibility.value
            
            # Build sort
            sort_map = {
                "created": "created_at",
                "updated": "updated_at",
                "views": "metrics.views",
                "likes": "metrics.likes"
            }
            sort_field = sort_map.get(sort_by, "updated_at")
            
            # Get total count
            total = await crud.collection.count_documents(query)
            
            # Get use cases
            skip = (page - 1) * page_size
            cursor = crud.collection.find(query)
            cursor = cursor.sort(sort_field, -1)
            cursor = cursor.skip(skip).limit(page_size)
            
            use_cases = await cursor.to_list(length=page_size)
            
            # Convert to brief format
            data = []
            for uc in use_cases:
                data.append({
                    "id": uc["id"],
                    "title": uc["title"],
                    "company": uc["company"],
                    "industry": uc["industry"],
                    "category": uc["category"],
                    "description": uc["description"][:200] + "..." if len(uc["description"]) > 200 else uc["description"],
                    "results": {},
                    "thumbnail": None,
                    "tags": uc.get("tags", []),
                    "verified": uc.get("verification", {}).get("status") == "verified",
                    "featured": uc.get("featured", {}).get("status", False),
                    "views": uc.get("metrics", {}).get("views", 0),
                    "likes": uc.get("metrics", {}).get("likes", 0),
                    "published_by": {
                        "name": uc["published_by"]["name"],
                        "title": uc["published_by"].get("title", "N/A")
                    },
                    "published_at": uc.get("published_at"),
                    "status": uc["status"],
                    "visibility": uc.get("visibility", "private")
                })
            
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            return {
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user use cases: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user use cases"
            )
    
    @staticmethod
    async def get_organization_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        organization_id: str,
        status: Optional[UseCaseStatus],
        author_id: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        sort_by: str,
        page: int,
        page_size: int,
        current_user: User
    ) -> Dict[str, Any]:
        """Get all use cases for an organization."""
        try:
            crud = get_use_case_crud(db)
            
            # Build query
            query = {"organization_id": organization_id}
            
            if status:
                query["status"] = status.value
            
            if author_id:
                query["published_by.user_id"] = author_id
            
            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = date_from
                if date_to:
                    date_query["$lte"] = date_to
                query["created_at"] = date_query
            
            # Build sort
            sort_map = {
                "created": "created_at",
                "updated": "updated_at",
                "views": "metrics.views",
                "likes": "metrics.likes",
                "author": "published_by.name"
            }
            sort_field = sort_map.get(sort_by, "updated_at")
            
            # Get total count
            total = await crud.collection.count_documents(query)
            
            # Get use cases
            skip = (page - 1) * page_size
            cursor = crud.collection.find(query)
            cursor = cursor.sort(sort_field, -1)
            cursor = cursor.skip(skip).limit(page_size)
            
            use_cases = await cursor.to_list(length=page_size)
            
            # Convert to brief format
            data = []
            for uc in use_cases:
                data.append({
                    "id": uc["id"],
                    "title": uc["title"],
                    "company": uc["company"],
                    "industry": uc["industry"],
                    "category": uc["category"],
                    "description": uc["description"][:200] + "..." if len(uc["description"]) > 200 else uc["description"],
                    "results": {},
                    "thumbnail": None,
                    "tags": uc.get("tags", []),
                    "verified": uc.get("verification", {}).get("status") == "verified",
                    "featured": uc.get("featured", {}).get("status", False),
                    "views": uc.get("metrics", {}).get("views", 0),
                    "likes": uc.get("metrics", {}).get("likes", 0),
                    "published_by": {
                        "name": uc["published_by"]["name"],
                        "title": uc["published_by"].get("title", "N/A")
                    },
                    "published_at": uc.get("published_at"),
                    "status": uc["status"],
                    "created_at": uc["created_at"]
                })
            
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            return {
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting organization use cases: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get organization use cases"
            )
    
    @staticmethod
    async def bulk_archive_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        use_case_ids: List[str],
        archive_reason: Optional[str],
        current_user: User
    ) -> Dict[str, Any]:
        """Archive multiple use cases."""
        try:
            crud = get_use_case_crud(db)
            
            results = {"success": [], "failed": []}
            
            for use_case_id in use_case_ids:
                try:
                    # Get the use case
                    use_case = await crud.get(use_case_id=use_case_id)
                    if not use_case:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Use case not found"
                        })
                        continue
                    
                    # Check permissions
                    can_archive = (
                        str(current_user.id) == use_case.published_by.user_id or
                        (current_user.role == "admin" and str(current_user.organization_id) == use_case.organization_id)
                    )
                    
                    if not can_archive:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Permission denied"
                        })
                        continue
                    
                    # Archive the use case
                    await crud.collection.update_one(
                        {"id": use_case_id},
                        {
                            "$set": {
                                "status": "archived",
                                "archived_at": datetime.utcnow(),
                                "archive_reason": archive_reason,
                                "archived_by": str(current_user.id)
                            }
                        }
                    )
                    
                    results["success"].append(use_case_id)
                    
                except Exception as e:
                    results["failed"].append({
                        "id": use_case_id,
                        "reason": str(e)
                    })
            
            return {
                "message": f"Archived {len(results['success'])} use cases",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk archive: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to archive use cases"
            )
    
    @staticmethod
    async def bulk_delete_use_cases(
        db: AsyncIOMotorDatabase,
        *,
        use_case_ids: List[str],
        hard_delete: bool,
        current_user: User
    ) -> Dict[str, Any]:
        """Delete multiple use cases."""
        try:
            crud = get_use_case_crud(db)
            
            results = {"success": [], "failed": []}
            
            for use_case_id in use_case_ids:
                try:
                    # Get the use case
                    use_case = await crud.get(use_case_id=use_case_id)
                    if not use_case:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Use case not found"
                        })
                        continue
                    
                    # Check permissions
                    can_delete = (
                        str(current_user.id) == use_case.published_by.user_id or
                        current_user.role == "admin"
                    )
                    
                    if not can_delete:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Permission denied"
                        })
                        continue
                    
                    # Delete the use case
                    success = await crud.delete(
                        use_case_id=use_case_id,
                        soft=not hard_delete
                    )
                    
                    if success:
                        results["success"].append(use_case_id)
                    else:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Delete operation failed"
                        })
                    
                except Exception as e:
                    results["failed"].append({
                        "id": use_case_id,
                        "reason": str(e)
                    })
            
            return {
                "message": f"{'Hard' if hard_delete else 'Soft'} deleted {len(results['success'])} use cases",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete use cases"
            )
    
    @staticmethod
    async def bulk_update_visibility(
        db: AsyncIOMotorDatabase,
        *,
        use_case_ids: List[str],
        visibility: UseCaseVisibility,
        current_user: User
    ) -> Dict[str, Any]:
        """Update visibility for multiple use cases."""
        try:
            crud = get_use_case_crud(db)
            
            results = {"success": [], "failed": []}
            
            for use_case_id in use_case_ids:
                try:
                    # Get the use case
                    use_case = await crud.get(use_case_id=use_case_id)
                    if not use_case:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Use case not found"
                        })
                        continue
                    
                    # Check permissions
                    can_update = (
                        str(current_user.id) == use_case.published_by.user_id or
                        current_user.role == "admin"
                    )
                    
                    if not can_update:
                        results["failed"].append({
                            "id": use_case_id,
                            "reason": "Permission denied"
                        })
                        continue
                    
                    # Update visibility
                    await crud.collection.update_one(
                        {"id": use_case_id},
                        {
                            "$set": {
                                "visibility": visibility.value,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    results["success"].append(use_case_id)
                    
                except Exception as e:
                    results["failed"].append({
                        "id": use_case_id,
                        "reason": str(e)
                    })
            
            return {
                "message": f"Updated visibility for {len(results['success'])} use cases to {visibility.value}",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk visibility update: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update visibility"
            )