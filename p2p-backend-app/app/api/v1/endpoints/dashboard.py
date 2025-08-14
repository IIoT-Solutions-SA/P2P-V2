"""
Dashboard API endpoints
Provides real-time user stats, activities, and dashboard data
"""

from fastapi import APIRouter, Depends, HTTPException
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from app.services.user_activity_service import UserActivityService
from app.services.database_service import UserService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class DraftCreate(BaseModel):
    title: str
    content: str
    post_type: str = "forum_post"
    category: Optional[str] = None
    tags: List[str] = []

@router.get("/stats")
async def get_dashboard_stats(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get user dashboard statistics"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user stats from MongoDB (using email to find MongoDB user)
        from app.models.mongo_models import User as MongoUser
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user statistics
        user_stats = await UserActivityService.get_user_stats(str(mongo_user.id))
        
        if not user_stats:
            # Return default stats if none exist yet
            return {
                "questions_asked": 0,
                "answers_given": 0,
                "bookmarks_saved": 0,
                "reputation_score": 0,
                "activity_level": 0.0,
                "use_cases_submitted": 0,
                "best_answers": 0,
                "draft_posts": 0,
                "connections_count": 0
            }
        
        return {
            "questions_asked": user_stats.questions_asked,
            "answers_given": user_stats.answers_given,
            "bookmarks_saved": user_stats.bookmarks_saved,
            "reputation_score": user_stats.reputation_score,
            "activity_level": round(user_stats.activity_level, 1),
            "use_cases_submitted": user_stats.use_cases_submitted,
            "best_answers": user_stats.best_answers,
            "draft_posts": user_stats.draft_posts,
            "connections_count": user_stats.connections_count
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@router.get("/activities")
async def get_dashboard_activities(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get recent community activities for dashboard feed"""
    try:
        # Get community activities (recent activities from all users)
        activities = await UserActivityService.get_community_activities(limit=10)
        
        return {
            "activities": activities
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard activities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard activities")

@router.get("/bookmarks")
async def get_user_bookmarks(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bookmarked items"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user bookmarks
        bookmarks = await UserActivityService.get_user_bookmarks(str(mongo_user.id))
        
        # Convert to response format
        bookmark_items = []
        for bookmark in bookmarks:
            bookmark_items.append({
                "id": str(bookmark.id),
                "target_type": bookmark.target_type,
                "target_id": bookmark.target_id,
                "title": bookmark.target_title,
                "category": bookmark.target_category,
                "saved_at": bookmark.created_at.isoformat()
            })
        
        return {
            "bookmarks": bookmark_items,
            "total": len(bookmark_items)
        }
        
    except Exception as e:
        logger.error(f"Error getting user bookmarks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user bookmarks")

@router.post("/bookmark")
async def add_bookmark(
    bookmark_data: dict,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Add a bookmark for the user"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Add bookmark
        bookmark = await UserActivityService.add_bookmark(
            user_id=str(mongo_user.id),
            target_type=bookmark_data.get("target_type"),
            target_id=bookmark_data.get("target_id"),
            target_title=bookmark_data.get("target_title"),
            target_category=bookmark_data.get("target_category")
        )
        
        if not bookmark:
            raise HTTPException(status_code=400, detail="Failed to add bookmark")
        
        return {
            "success": True,
            "bookmark_id": str(bookmark.id)
        }
        
    except Exception as e:
        logger.error(f"Error adding bookmark: {e}")
        raise HTTPException(status_code=500, detail="Failed to add bookmark")

@router.get("/drafts")
async def get_user_drafts(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get user's draft posts"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user drafts
        drafts = await UserActivityService.get_user_drafts(str(mongo_user.id))
        
        # Convert to response format
        draft_items = []
        for draft in drafts:
            draft_items.append({
                "id": str(draft.id),
                "title": draft.title,
                "content": draft.content[:200] + "..." if len(draft.content) > 200 else draft.content,
                "post_type": draft.post_type,
                "category": draft.category,
                "created_at": draft.created_at.isoformat(),
                "updated_at": draft.updated_at.isoformat()
            })
        
        return {
            "drafts": draft_items,
            "total": len(draft_items)
        }
        
    except Exception as e:
        logger.error(f"Error getting user drafts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user drafts")

@router.post("/drafts", status_code=201)
async def create_draft_post(
    draft_data: DraftCreate,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Create a new draft post"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Create draft
        draft = await UserActivityService.create_draft_post(
            user_id=str(mongo_user.id),
            title=draft_data.title,
            content=draft_data.content,
            post_type=draft_data.post_type,
            category=draft_data.category,
            tags=draft_data.tags
        )
        
        if not draft:
            raise HTTPException(status_code=500, detail="Failed to create draft")
        
        return {
            "success": True,
            "draft_id": str(draft.id),
            "message": "Draft saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating draft post: {e}")
        raise HTTPException(status_code=500, detail="Failed to create draft")

@router.put("/drafts/{draft_id}")
async def update_draft_post(
    draft_id: str,
    draft_data: DraftCreate,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing draft post"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser, DraftPost
        from bson import ObjectId
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Find and update the draft
        try:
            draft = await DraftPost.find_one(
                DraftPost.id == ObjectId(draft_id),
                DraftPost.user_id == str(mongo_user.id)
            )
        except Exception:
            draft = None
            
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        # Update the draft
        draft.title = draft_data.title
        draft.content = draft_data.content
        draft.category = draft_data.category
        draft.post_type = draft_data.post_type
        draft.tags = draft_data.tags
        draft.updated_at = datetime.utcnow()
        await draft.save()
        
        return {
            "success": True,
            "draft_id": str(draft.id),
            "message": "Draft updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating draft post: {e}")
        raise HTTPException(status_code=500, detail="Failed to update draft")

@router.delete("/drafts/{draft_id}")
async def delete_draft_post(
    draft_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Delete a draft post"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser, DraftPost
        from bson import ObjectId
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Find and delete the draft
        try:
            draft = await DraftPost.find_one(
                DraftPost.id == ObjectId(draft_id),
                DraftPost.user_id == str(mongo_user.id)
            )
        except Exception:
            draft = None
            
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        # Delete the draft
        await draft.delete()
        
        # Trigger stats recalculation to update draft count
        await UserActivityService.recalculate_user_stats(str(mongo_user.id))
        
        return {
            "success": True,
            "message": "Draft deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting draft post: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete draft")

@router.post("/recalculate-stats")
async def recalculate_user_stats(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger user stats recalculation (for testing/admin)"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get PostgreSQL user to get the MongoDB user ID
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user from MongoDB
        from app.models.mongo_models import User as MongoUser
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Recalculate stats
        user_stats = await UserActivityService.recalculate_user_stats(str(mongo_user.id))
        
        if not user_stats:
            raise HTTPException(status_code=500, detail="Failed to recalculate stats")
        
        return {
            "success": True,
            "stats": {
                "questions_asked": user_stats.questions_asked,
                "answers_given": user_stats.answers_given,
                "reputation_score": user_stats.reputation_score,
                "activity_level": user_stats.activity_level
            }
        }
        
    except Exception as e:
        logger.error(f"Error recalculating user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to recalculate user stats")