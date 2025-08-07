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
        """Browse use cases with filters."""
        try:
            crud = get_use_case_crud(db)
            
            # Get use cases
            use_cases, total = await crud.get_multi(
                filters=filters,
                organization_id=str(current_user.organization_id) if current_user and filters.visibility == UseCaseVisibility.ORGANIZATION else None
            )
            
            # Convert to brief schema
            data = []
            for uc in use_cases:
                brief = UseCaseBrief(
                    id=uc.id,
                    title=uc.title,
                    company=uc.company,
                    industry=uc.industry,
                    category=uc.category,
                    description=uc.description[:200] + "..." if len(uc.description) > 200 else uc.description,
                    results={
                        "key_metric": uc.results.key_metric if uc.results else None,
                        "roi": f"{uc.results.roi.percentage}%" if uc.results and uc.results.roi and uc.results.roi.percentage else None
                    },
                    thumbnail=uc.media[0].thumbnail_path if uc.media else None,
                    tags=uc.tags,
                    verified=uc.verification.verified,
                    featured=uc.featured.is_featured,
                    views=uc.metrics.views,
                    likes=uc.metrics.likes,
                    published_by={
                        "name": uc.published_by.name,
                        "title": uc.published_by.title
                    },
                    published_at=uc.published_at
                )
                data.append(brief)
            
            # Build response
            return {
                "data": data,
                "pagination": {
                    "page": filters.page,
                    "page_size": filters.page_size,
                    "total_items": total,
                    "total_pages": (total + filters.page_size - 1) // filters.page_size
                },
                "filters_applied": {
                    k: v for k, v in filters.model_dump().items() 
                    if v is not None and k not in ["page", "page_size"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error browsing use cases: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to browse use cases"
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