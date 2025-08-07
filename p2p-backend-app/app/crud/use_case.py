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
        current_user_org_id: Optional[str] = None,
        is_guest_user: bool = False
    ) -> tuple[List[UseCase], int]:
        """Get multiple use cases with advanced filters and pagination."""
        try:
            # Build base query for published use cases
            query = {"status": UseCaseStatus.PUBLISHED.value}
            
            # Access control based on user authentication
            if is_guest_user:
                # Guest users can only see public use cases
                query["visibility"] = UseCaseVisibility.PUBLIC.value
            elif current_user_org_id:
                # Authenticated users can see public + their organization's use cases
                query["$or"] = [
                    {"visibility": UseCaseVisibility.PUBLIC.value},
                    {
                        "$and": [
                            {"visibility": UseCaseVisibility.ORGANIZATION.value},
                            {"organization_id": current_user_org_id}
                        ]
                    }
                ]
            else:
                # Default to public only if no org context
                query["visibility"] = UseCaseVisibility.PUBLIC.value
            
            # Apply category filter
            if filters.category:
                query["category"] = filters.category.value if hasattr(filters.category, 'value') else filters.category
            
            # Apply industry filter (case-insensitive partial match)
            if filters.industry:
                query["industry"] = {"$regex": filters.industry, "$options": "i"}
            
            # Apply technologies filter
            if filters.technologies:
                # Convert comma-separated string to list if needed
                tech_list = filters.technologies
                if isinstance(tech_list, str):
                    tech_list = [tech.strip() for tech in tech_list.split(',') if tech.strip()]
                
                if tech_list:
                    query["technologies"] = {"$in": tech_list}
            
            # Apply verification filter
            if filters.verified is not None:
                if filters.verified:
                    query["verification.status"] = "verified"
                else:
                    query["$or"] = [
                        {"verification.status": {"$ne": "verified"}},
                        {"verification": {"$exists": False}}
                    ]
            
            # Apply featured filter
            if filters.featured is not None:
                if filters.featured:
                    query["featured.status"] = True
                else:
                    query["$or"] = [
                        {"featured.status": False},
                        {"featured": {"$exists": False}}
                    ]
            
            # Apply full-text search across multiple fields
            if filters.search:
                search_term = filters.search.strip()
                search_query = {
                    "$or": [
                        {"title": {"$regex": search_term, "$options": "i"}},
                        {"description": {"$regex": search_term, "$options": "i"}},
                        {"solution": {"$regex": search_term, "$options": "i"}},
                        {"challenge": {"$regex": search_term, "$options": "i"}},
                        {"company": {"$regex": search_term, "$options": "i"}},
                        {"tags": {"$regex": search_term, "$options": "i"}},
                        {"technologies": {"$regex": search_term, "$options": "i"}},
                        {"vendors.name": {"$regex": search_term, "$options": "i"}}
                    ]
                }
                
                # Combine search with existing query logic
                if "$or" in query:
                    # If we already have an $or clause, we need to restructure
                    existing_or = query.pop("$or")
                    query = {
                        "$and": [
                            query,  # Base query without $or
                            {"$or": existing_or},  # Original $or clause
                            search_query  # Search $or clause
                        ]
                    }
                else:
                    query.update(search_query)
            
            # Build sort criteria with multiple fallbacks
            sort_criteria = []
            
            if filters.sort_by == "date":
                sort_criteria.append(("published_at", -1 if filters.order == "desc" else 1))
            elif filters.sort_by == "views":
                sort_criteria.append(("metrics.views", -1 if filters.order == "desc" else 1))
            elif filters.sort_by == "likes":
                sort_criteria.append(("metrics.likes", -1 if filters.order == "desc" else 1))
            elif filters.sort_by == "roi":
                sort_criteria.append(("results.roi.percentage", -1 if filters.order == "desc" else 1))
            else:
                # Default sort
                sort_criteria.append(("published_at", -1))
            
            # Add secondary sort by publication date for consistent ordering
            if filters.sort_by != "date":
                sort_criteria.append(("published_at", -1))
            
            # Count total matching documents
            total = await self.collection.count_documents(query)
            
            # Calculate pagination
            skip = (filters.page - 1) * filters.page_size
            
            # Build cursor with optimized projection for list view
            projection = {
                "id": 1, "title": 1, "company": 1, "industry": 1, "category": 1,
                "description": 1, "results": 1, "tags": 1, "technologies": 1,
                "verification": 1, "featured": 1, "metrics": 1,
                "published_by.name": 1, "published_by.title": 1,
                "published_at": 1, "media": {"$slice": 1}  # Only first media for thumbnail
            }
            
            cursor = self.collection.find(query, projection)
            
            # Apply sorting
            for field, direction in sort_criteria:
                cursor = cursor.sort(field, direction)
            
            # Apply pagination
            cursor = cursor.skip(skip).limit(filters.page_size)
            
            # Execute query and convert to UseCase objects
            use_cases = []
            async for doc in cursor:
                try:
                    use_case = UseCase(**doc)
                    use_cases.append(use_case)
                except Exception as e:
                    logger.warning(f"Skipping invalid use case document {doc.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(
                f"Retrieved {len(use_cases)} use cases (page {filters.page}, "
                f"total {total}) with filters: {filters.model_dump()}"
            )
            
            return use_cases, total
            
        except Exception as e:
            logger.error(f"Error getting multiple use cases with filters {filters.model_dump()}: {e}")
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