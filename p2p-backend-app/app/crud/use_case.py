"""CRUD operations for Use Cases using MongoDB."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from bson import ObjectId

from app.models.use_case import (
    UseCase,
    UseCaseDraft,
    UseCaseView,
    UseCaseLike,
    UseCaseSave,
    UseCaseStatus,
    UseCaseVisibility
)
from app.schemas.use_case import (
    UseCaseCreate,
    UseCaseUpdate,
    UseCaseFilters,
    DraftSave
)

logger = logging.getLogger(__name__)


class CRUDUseCase:
    """CRUD operations for Use Cases."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.use_cases
        self.drafts = db.use_case_drafts
        self.views = db.use_case_views
        self.likes = db.use_case_likes
        self.saves = db.use_case_saves
    
    async def create(
        self,
        *,
        obj_in: UseCaseCreate,
        user_id: str,
        user_name: str,
        user_title: Optional[str],
        user_email: str,
        organization_id: str
    ) -> UseCase:
        """Create a new use case."""
        try:
            # Create UseCase document
            use_case_data = obj_in.model_dump()
            use_case_data.update({
                "organization_id": organization_id,
                "published_by": {
                    "user_id": user_id,
                    "name": user_name,
                    "title": user_title,
                    "email": user_email
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Set published_at if status is published
            if use_case_data.get("status") == UseCaseStatus.PUBLISHED:
                use_case_data["published_at"] = datetime.utcnow()
            
            # Create UseCase model
            use_case = UseCase(**use_case_data)
            
            # Insert into MongoDB
            result = await self.collection.insert_one(
                use_case.model_dump(by_alias=True)
            )
            
            # Set the MongoDB _id
            use_case.id = str(result.inserted_id)
            
            logger.info(f"Created use case {use_case.id} for organization {organization_id}")
            return use_case
            
        except Exception as e:
            logger.error(f"Error creating use case: {e}")
            raise
    
    async def get(
        self,
        *,
        use_case_id: str,
        organization_id: Optional[str] = None
    ) -> Optional[UseCase]:
        """Get a use case by ID."""
        try:
            query = {"id": use_case_id}
            if organization_id:
                query["organization_id"] = organization_id
            
            doc = await self.collection.find_one(query)
            if doc:
                return UseCase(**doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting use case {use_case_id}: {e}")
            raise
    
    async def get_multi(
        self,
        *,
        filters: UseCaseFilters,
        organization_id: Optional[str] = None
    ) -> tuple[List[UseCase], int]:
        """Get multiple use cases with filters and pagination."""
        try:
            # Build query
            query = {"status": UseCaseStatus.PUBLISHED}
            
            if organization_id:
                query["organization_id"] = organization_id
            
            if filters.category:
                query["category"] = filters.category
            
            if filters.industry:
                query["industry"] = filters.industry
            
            if filters.technologies:
                query["technologies"] = {"$in": filters.technologies}
            
            if filters.verified is not None:
                query["verification.verified"] = filters.verified
            
            if filters.featured is not None:
                query["featured.is_featured"] = filters.featured
            
            # Text search
            if filters.search:
                query["$text"] = {"$search": filters.search}
            
            # Count total
            total = await self.collection.count_documents(query)
            
            # Build sort
            sort_field = {
                "date": "created_at",
                "views": "metrics.views",
                "likes": "metrics.likes",
                "roi": "results.roi.percentage"
            }.get(filters.sort_by, "created_at")
            
            sort_order = -1 if filters.order == "desc" else 1
            
            # Execute query with pagination
            skip = (filters.page - 1) * filters.page_size
            cursor = self.collection.find(query)
            cursor = cursor.sort(sort_field, sort_order)
            cursor = cursor.skip(skip).limit(filters.page_size)
            
            # Get results
            use_cases = []
            async for doc in cursor:
                use_cases.append(UseCase(**doc))
            
            return use_cases, total
            
        except Exception as e:
            logger.error(f"Error getting multiple use cases: {e}")
            raise
    
    async def update(
        self,
        *,
        use_case_id: str,
        obj_in: UseCaseUpdate,
        user_id: str
    ) -> Optional[UseCase]:
        """Update a use case."""
        try:
            # Get update data
            update_data = obj_in.model_dump(exclude_unset=True)
            if not update_data:
                return await self.get(use_case_id=use_case_id)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Set published_at if changing to published status
            if update_data.get("status") == UseCaseStatus.PUBLISHED:
                existing = await self.get(use_case_id=use_case_id)
                if existing and not existing.published_at:
                    update_data["published_at"] = datetime.utcnow()
            
            # Update document
            result = await self.collection.find_one_and_update(
                {"id": use_case_id},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
            
            if result:
                logger.info(f"Updated use case {use_case_id} by user {user_id}")
                return UseCase(**result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating use case {use_case_id}: {e}")
            raise
    
    async def delete(
        self,
        *,
        use_case_id: str,
        soft: bool = True
    ) -> bool:
        """Delete a use case (soft delete by default)."""
        try:
            if soft:
                # Soft delete
                result = await self.collection.update_one(
                    {"id": use_case_id},
                    {
                        "$set": {
                            "status": UseCaseStatus.ARCHIVED,
                            "deleted_at": datetime.utcnow()
                        }
                    }
                )
            else:
                # Hard delete
                result = await self.collection.delete_one({"id": use_case_id})
            
            success = result.modified_count > 0 if soft else result.deleted_count > 0
            if success:
                logger.info(f"{'Soft' if soft else 'Hard'} deleted use case {use_case_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting use case {use_case_id}: {e}")
            raise
    
    async def save_draft(
        self,
        *,
        draft_data: DraftSave,
        user_id: str,
        organization_id: str
    ) -> UseCaseDraft:
        """Save a use case draft."""
        try:
            # Create or update draft
            draft = UseCaseDraft(
                use_case_id=draft_data.use_case_id,
                user_id=user_id,
                organization_id=organization_id,
                draft_data=draft_data.draft_data,
                current_step=draft_data.current_step,
                last_saved=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            # Upsert draft
            filter_query = {
                "user_id": user_id,
                "organization_id": organization_id
            }
            
            if draft_data.use_case_id:
                filter_query["use_case_id"] = draft_data.use_case_id
            
            await self.drafts.replace_one(
                filter_query,
                draft.model_dump(by_alias=True),
                upsert=True
            )
            
            logger.info(f"Saved draft for user {user_id}")
            return draft
            
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            raise
    
    async def get_draft(
        self,
        *,
        user_id: str,
        use_case_id: Optional[str] = None
    ) -> Optional[UseCaseDraft]:
        """Get a user's draft."""
        try:
            query = {"user_id": user_id}
            if use_case_id:
                query["use_case_id"] = use_case_id
            
            doc = await self.drafts.find_one(query)
            if doc:
                return UseCaseDraft(**doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting draft: {e}")
            raise
    
    async def track_view(
        self,
        *,
        use_case_id: str,
        viewer_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Track a use case view."""
        try:
            # Create view record
            view = UseCaseView(
                use_case_id=use_case_id,
                viewer_id=viewer_id,
                organization_id=organization_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                viewed_at=datetime.utcnow()
            )
            
            # Insert view
            await self.views.insert_one(view.model_dump(by_alias=True))
            
            # Update view count
            await self.collection.update_one(
                {"id": use_case_id},
                {"$inc": {"metrics.views": 1}}
            )
            
            # Update unique views if viewer_id provided
            if viewer_id:
                # Check if user has viewed before
                existing = await self.views.find_one({
                    "use_case_id": use_case_id,
                    "viewer_id": viewer_id
                })
                
                if not existing:
                    await self.collection.update_one(
                        {"id": use_case_id},
                        {"$inc": {"metrics.unique_views": 1}}
                    )
            
        except Exception as e:
            logger.error(f"Error tracking view: {e}")
            # Don't raise - view tracking should not break the request
    
    async def toggle_like(
        self,
        *,
        use_case_id: str,
        user_id: str,
        organization_id: str
    ) -> tuple[bool, int]:
        """Toggle like status for a use case."""
        try:
            # Check if already liked
            existing = await self.likes.find_one({
                "use_case_id": use_case_id,
                "user_id": user_id
            })
            
            if existing:
                # Unlike
                await self.likes.delete_one({
                    "use_case_id": use_case_id,
                    "user_id": user_id
                })
                
                # Update count
                result = await self.collection.find_one_and_update(
                    {"id": use_case_id},
                    {"$inc": {"metrics.likes": -1}},
                    return_document=ReturnDocument.AFTER
                )
                
                liked = False
            else:
                # Like
                like = UseCaseLike(
                    use_case_id=use_case_id,
                    user_id=user_id,
                    organization_id=organization_id
                )
                
                await self.likes.insert_one(like.model_dump(by_alias=True))
                
                # Update count
                result = await self.collection.find_one_and_update(
                    {"id": use_case_id},
                    {"$inc": {"metrics.likes": 1}},
                    return_document=ReturnDocument.AFTER
                )
                
                liked = True
            
            total_likes = result["metrics"]["likes"] if result else 0
            
            logger.info(f"User {user_id} {'liked' if liked else 'unliked'} use case {use_case_id}")
            return liked, total_likes
            
        except Exception as e:
            logger.error(f"Error toggling like: {e}")
            raise
    
    async def toggle_save(
        self,
        *,
        use_case_id: str,
        user_id: str,
        organization_id: str
    ) -> tuple[bool, int]:
        """Toggle save/bookmark status for a use case."""
        try:
            # Check if already saved
            existing = await self.saves.find_one({
                "use_case_id": use_case_id,
                "user_id": user_id
            })
            
            if existing:
                # Unsave
                await self.saves.delete_one({
                    "use_case_id": use_case_id,
                    "user_id": user_id
                })
                
                # Update count
                result = await self.collection.find_one_and_update(
                    {"id": use_case_id},
                    {"$inc": {"metrics.saves": -1}},
                    return_document=ReturnDocument.AFTER
                )
                
                saved = False
            else:
                # Save
                save = UseCaseSave(
                    use_case_id=use_case_id,
                    user_id=user_id,
                    organization_id=organization_id
                )
                
                await self.saves.insert_one(save.model_dump(by_alias=True))
                
                # Update count
                result = await self.collection.find_one_and_update(
                    {"id": use_case_id},
                    {"$inc": {"metrics.saves": 1}},
                    return_document=ReturnDocument.AFTER
                )
                
                saved = True
            
            total_saves = result["metrics"]["saves"] if result else 0
            
            logger.info(f"User {user_id} {'saved' if saved else 'unsaved'} use case {use_case_id}")
            return saved, total_saves
            
        except Exception as e:
            logger.error(f"Error toggling save: {e}")
            raise


# Singleton instance
use_case_crud = None

def get_use_case_crud(db: AsyncIOMotorDatabase) -> CRUDUseCase:
    """Get or create CRUD instance."""
    global use_case_crud
    if not use_case_crud:
        use_case_crud = CRUDUseCase(db)
    return use_case_crud