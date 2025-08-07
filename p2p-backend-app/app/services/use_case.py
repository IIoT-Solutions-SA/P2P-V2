"""Business logic service for Use Cases."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
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
    async def get_use_case(
        db: AsyncIOMotorDatabase,
        *,
        use_case_id: str,
        current_user: Optional[User] = None,
        track_view: bool = True
    ) -> UseCaseDetail:
        """Get a use case by ID."""
        try:
            crud = get_use_case_crud(db)
            
            # Get use case
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
            
            # Track view if requested
            if track_view:
                await crud.track_view(
                    use_case_id=use_case_id,
                    viewer_id=str(current_user.id) if current_user else None,
                    organization_id=str(current_user.organization_id) if current_user else None
                )
            
            # Get related use cases (simple implementation for now)
            related = []
            if use_case.related_use_cases:
                for related_id in use_case.related_use_cases[:3]:
                    related_uc = await crud.get(use_case_id=related_id)
                    if related_uc:
                        related.append({
                            "id": related_uc.id,
                            "title": related_uc.title,
                            "category": related_uc.category,
                            "roi": related_uc.results.roi.percentage if related_uc.results.roi else None
                        })
            
            # Convert to detail schema
            use_case_dict = use_case.model_dump()
            
            # Remove sensitive information if not owner
            if not current_user or str(current_user.id) != use_case.published_by.user_id:
                use_case_dict["published_by"].pop("email", None)
            
            # Add related use cases
            use_case_dict["related_use_cases"] = related
            
            return UseCaseDetail(**use_case_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get use case"
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