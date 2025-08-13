"""
Forum API endpoints
Provides forum posts, categories, replies, and interactions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from app.services.database_service import UserService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mongo_models import ForumPost, ForumReply, User as MongoUser, UserBookmark, UserActivity
from typing import List, Optional
from app.schemas.forum import ForumPostCreate
from app.services.user_activity_service import UserActivityService
from app.services.forum_service import ForumService
from pydantic import BaseModel
import logging
from datetime import datetime
import re
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()


class ReplyCreate(BaseModel):
    content: str
    parent_reply_id: Optional[str] = None


def _normalize_category_name(raw: str) -> str:
    try:
        if not raw:
            return raw
        s = str(raw).replace("-", " ").strip().lower()
        return " ".join(w.capitalize() for w in s.split())
    except Exception:
        return raw
@router.post("/posts", status_code=201)
async def create_forum_post(
    post_data: ForumPostCreate,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Create a new forum post"""
    try:
        supertokens_user_id = session.get_user_id()

        # Map category_id (from frontend) to name. For now, assume it's a name already.
        category_name = post_data.category_id

        # Resolve author from PG->Mongo using session user
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        post = ForumPost(
            author_id=str(mongo_user.id),
            title=post_data.title,
            content=post_data.content,
            category=_normalize_category_name(category_name),
            tags=post_data.tags or []
        )
        await post.insert()

        # Log activity
        await UserActivityService.log_activity(
            user_id=str(mongo_user.id),
            activity_type="question",
            target_id=str(post.id),
            target_title=post.title,
            target_category=post.category
        )

        return {"id": str(post.id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating forum post: {e}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.get("/posts")
async def get_forum_posts(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, description="Number of posts to return"),
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get forum posts with optional category filter"""
    try:
        # Resolve current user's Mongo ID (for isLikedByUser flag)
        supertokens_user_id = session.get_user_id()
        current_user_mongo_id = None
        try:
            pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
            if pg_user:
                mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
                if mongo_user:
                    current_user_mongo_id = str(mongo_user.id)
        except Exception:
            current_user_mongo_id = None

        # Build query (case-insensitive category filter)
        query = {}
        if category and category != "all":
            try:
                query["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}
            except Exception:
                query["category"] = category
        
        # Get posts from database
        posts = await ForumPost.find(query).sort(-ForumPost.created_at).limit(limit).to_list()
        
        # Get user names for posts
        user_names = {}
        for post in posts:
            if post.author_id not in user_names:
                try:
                    user = await MongoUser.find_one(MongoUser.id == ObjectId(post.author_id))
                    user_names[post.author_id] = user.name if user else "Unknown User"
                except Exception:
                    user_names[post.author_id] = "Unknown User"
        
        # Convert to frontend format
        forum_data = []
        for post in posts:
            # Calculate time ago
            time_diff = datetime.utcnow() - post.created_at
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = max(1, time_diff.seconds // 60)
                time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
            # Get reply count
            reply_count = await ForumReply.find(ForumReply.post_id == str(post.id)).count()
            
            forum_data.append({
                "id": str(post.id),
                "title": post.title,
                "author": user_names.get(post.author_id, "Unknown User"),
                "authorTitle": "Community Member",  # Can be enhanced later
                "category": _normalize_category_name(post.category),
                "content": post.content,
                "replies": reply_count,
                "views": post.views,
                "likes": post.upvotes,
                "isLikedByUser": bool(current_user_mongo_id and current_user_mongo_id in getattr(post, 'liked_by', [])),
                "timeAgo": time_ago,
                "isPinned": post.is_pinned,
                "hasBestAnswer": post.has_best_answer,
                "isVerified": True,  # Can be enhanced later based on user verification
                "excerpt": post.content[:150] + "..." if len(post.content) > 150 else post.content,
                "tags": post.tags
            })
        
        return {
            "posts": forum_data,
            "total": len(forum_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting forum posts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum posts")

@router.get("/categories")
async def get_forum_categories(session: SessionContainer = Depends(verify_session())):
    """Get forum categories with real post counts (efficiently)"""
    try:
        # UPDATED: Use MongoDB aggregation for much better performance
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        category_cursor = ForumPost.aggregate(pipeline)
        raw_categories = await category_cursor.to_list()

        # Merge categories by normalized display name to avoid duplicates like
        # "automation" vs "Automation"
        merged: dict[str, int] = {}
        for cat in raw_categories:
            raw_name = cat.get("_id")
            if not raw_name:
                continue
            norm_name = _normalize_category_name(raw_name)
            merged[norm_name] = merged.get(norm_name, 0) + int(cat.get("count", 0))

        total_posts = sum(merged.values()) if merged else await ForumPost.find_all().count()

        # Format for frontend
        formatted_categories = [{"id": "all", "name": "All Topics", "count": total_posts}]
        for name, count in sorted(merged.items()):
            formatted_categories.append({
                "id": name.lower().replace(" ", "-"),
                "name": name,
                "count": count,
            })
        
        return {"categories": formatted_categories}
        
    except Exception as e:
        logger.error(f"Error getting forum categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum categories")

@router.get("/posts/{post_id}")
async def get_forum_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific forum post with comments"""
    try:
        # Get the post
        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Increment view count with user deduplication (realistic view counting)
        
        supertokens_user_id = session.get_user_id()
        should_increment = True
        
        # Check if this user has ever viewed this forum post before
        if supertokens_user_id:
            try:
                # Get mongo user for activity tracking
                pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id) 
                mongo_user = None
                if pg_user and pg_user.email:
                    mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
                
                if mongo_user:
                    user_id_str = str(mongo_user.id)
                    # Check if user has EVER viewed this forum post (realistic view counting)
                    existing_view = await UserActivity.find_one(
                        UserActivity.user_id == user_id_str,
                        UserActivity.activity_type == "view",
                        UserActivity.target_id == str(post.id),
                    )
                    if existing_view:
                        should_increment = False
                        logger.info(f"User {mongo_user.name} already viewed post {post.title} - not incrementing")
                    else:
                        logger.info(f"User {mongo_user.name} viewing post {post.title} for first time - incrementing")
            except Exception as e:
                logger.error(f"Error checking view history for user {supertokens_user_id}: {e}")
                # Don't increment on error - better to undercount than overcount
                should_increment = False
        
        if should_increment:
            post.views += 1
            await post.save()
            
            # Log the view activity
            if supertokens_user_id and mongo_user:
                try:
                    await UserActivityService.log_activity(
                        user_id=str(mongo_user.id),
                        activity_type="view",
                        target_id=str(post.id),
                        target_title=post.title,
                        target_category=post.category,
                        description=f"Viewed forum post: {post.title}",
                    )
                except Exception as e:
                    logger.error(f"Error logging view activity: {e}")
        
        # Get post author
        try:
            author = await MongoUser.find_one(MongoUser.id == ObjectId(post.author_id))
            author_name = author.name if author else "Unknown User"
        except Exception:
            author_name = "Unknown User"
        
        # Get replies/comments
        replies = await ForumReply.find(ForumReply.post_id == post_id).sort(ForumReply.created_at).to_list()
        
        # Get reply authors
        reply_data = []
        # Build a map for nesting
        reply_map = {}
        children_map = {}
        for reply in replies:
            try:
                reply_author = await MongoUser.find_one(MongoUser.id == ObjectId(reply.author_id))
                reply_author_name = reply_author.name if reply_author else "Unknown User"
            except Exception:
                reply_author_name = "Unknown User"
            
            # Calculate time ago for reply
            time_diff = datetime.utcnow() - reply.created_at
            if time_diff.days > 0:
                reply_time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                reply_time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = max(1, time_diff.seconds // 60)
                reply_time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            node = {
                "id": str(reply.id),
                "author": reply_author_name,
                "authorTitle": "Community Member",
                "content": reply.content,
                "timeAgo": reply_time_ago,
                "likes": reply.upvotes,
                "isVerified": True,
                "isBestAnswer": reply.is_best_answer,
                "replies": [],
                "parent_reply_id": getattr(reply, 'parent_reply_id', None),
            }
            reply_map[str(reply.id)] = node
            parent_id = getattr(reply, 'parent_reply_id', None)
            if parent_id:
                children_map.setdefault(parent_id, []).append(node)
            else:
                reply_data.append(node)

        # Attach children to their parents
        for parent_id, kids in children_map.items():
            parent_node = reply_map.get(parent_id)
            if parent_node:
                parent_node["replies"].extend(kids)
        
        # Calculate post time ago
        time_diff = datetime.utcnow() - post.created_at
        if time_diff.days > 0:
            time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = max(1, time_diff.seconds // 60)
            time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        
        return {
            "id": str(post.id),
            "title": post.title,
            "author": author_name,
            "authorTitle": "Community Member",
            "category": post.category,
            "content": post.content,
            "replies": len(reply_data),
            "views": post.views,
            "likes": post.upvotes,
            "timeAgo": time_ago,
            "isPinned": post.is_pinned,
            "hasBestAnswer": post.has_best_answer,
            "isVerified": True,
            "tags": post.tags,
            "comments": reply_data
        }
        
    except Exception as e:
        logger.error(f"Error getting forum post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum post")

@router.post("/posts/{post_id}/like")
async def like_forum_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Like/unlike a forum post (user-specific)."""
    try:
        supertokens_user_id = session.get_user_id()
        result = await ForumService.toggle_like(
            user_supertokens_id=supertokens_user_id,
            document_id=post_id,
            doc_type='post',
            db=db,
        )
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error liking post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to like post")

@router.post("/posts/{post_id}/replies")
async def create_reply(
    post_id: str,
    reply_data: ReplyCreate,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Create a new reply to a forum post"""
    try:
        supertokens_user_id = session.get_user_id()
        reply = await ForumService.create_reply(
            user_supertokens_id=supertokens_user_id,
            post_id=post_id,
            content=reply_data.content,
            parent_reply_id=reply_data.parent_reply_id,
            db=db,
        )
        return {"success": True, "reply_id": str(reply.id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating reply: {e}")
        raise HTTPException(status_code=500, detail="Failed to create reply")

@router.post("/replies/{reply_id}/like")
async def like_forum_reply(
    reply_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Like/unlike a forum reply (user-specific)."""
    try:
        supertokens_user_id = session.get_user_id()
        result = await ForumService.toggle_like(
            user_supertokens_id=supertokens_user_id,
            document_id=reply_id,
            doc_type='reply',
            db=db,
        )
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error liking reply {reply_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to like reply")

@router.get("/stats")
async def get_forum_stats(
    session: SessionContainer = Depends(verify_session())
):
    """Get real forum statistics"""
    try:
        # Get total topics count
        total_topics = await ForumPost.find_all().count()
        
        # Get total replies count (helpful answers)
        total_replies = await ForumReply.find_all().count()
        
        # Get unique active members (users who posted or replied)
        all_posts = await ForumPost.find_all().to_list()
        all_replies = await ForumReply.find_all().to_list()
        
        # Collect unique user IDs
        active_user_ids = set()
        for post in all_posts:
            active_user_ids.add(post.author_id)
        for reply in all_replies:
            active_user_ids.add(reply.author_id)
        
        active_members = len(active_user_ids)
        
        return {
            "total_topics": total_topics,
            "active_members": active_members,
            "helpful_answers": total_replies
        }
        
    except Exception as e:
        logger.error(f"Error getting forum stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum stats")

@router.get("/contributors")
async def get_top_contributors(
    limit: int = Query(5, description="Number of top contributors to return"),
    session: SessionContainer = Depends(verify_session())
):
    """Get top contributors with calculated points"""
    try:
        # Get all posts and replies to calculate points
        all_posts = await ForumPost.find_all().to_list()
        all_replies = await ForumReply.find_all().to_list()
        
        # Calculate points for each user
        user_points = {}
        user_names = {}
        
        # Points from posts (50 points per post + 5 points per like)
        for post in all_posts:
            if post.author_id not in user_points:
                user_points[post.author_id] = 0
                # Get user name
                try:
                    user = await MongoUser.find_one(MongoUser.id == ObjectId(post.author_id))
                    user_names[post.author_id] = user.name if user else "Unknown User"
                except:
                    user_names[post.author_id] = "Unknown User"
            
            # 50 points for creating a post
            user_points[post.author_id] += 50
            # 5 points per like received
            user_points[post.author_id] += post.upvotes * 5
        
        # Points from replies (20 points per reply + 3 points per like)
        for reply in all_replies:
            if reply.author_id not in user_points:
                user_points[reply.author_id] = 0
                # Get user name
                try:
                    user = await MongoUser.find_one(MongoUser.id == ObjectId(reply.author_id))
                    user_names[reply.author_id] = user.name if user else "Unknown User"
                except:
                    user_names[reply.author_id] = "Unknown User"
            
            # 20 points for creating a reply
            user_points[reply.author_id] += 20
            # 3 points per like received
            user_points[reply.author_id] += reply.upvotes * 3
            # Bonus 30 points if it's a best answer
            if reply.is_best_answer:
                user_points[reply.author_id] += 30
        
        # Sort users by points and get top contributors
        sorted_contributors = sorted(
            user_points.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        # Format response
        contributors = []
        for i, (user_id, points) in enumerate(sorted_contributors):
            name = user_names.get(user_id, "Unknown User")
            avatar = name[0].upper() if name and name != "Unknown User" else "?"
            
            contributors.append({
                "name": name,
                "points": points,
                "avatar": avatar,
                "rank": i + 1
            })
        
        return {
            "contributors": contributors
        }
        
    except Exception as e:
        logger.error(f"Error getting top contributors: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top contributors")


@router.get("/bookmarks")
async def get_forum_bookmarks(
    limit: int = Query(20, description="Max bookmarks to return"),
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db),
):
    """List current user's bookmarked forum posts (for Saved Posts page)."""
    try:
        supertokens_user_id = session.get_user_id()
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)
        bookmarks = await UserBookmark.find(
            UserBookmark.user_id == user_id_str,
            UserBookmark.target_type == "forum_post",
        ).sort(-UserBookmark.created_at).limit(limit).to_list()
        return bookmarks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forum bookmarks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum bookmarks")


@router.post("/posts/{post_id}/bookmark")
async def bookmark_forum_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Toggle bookmark on a forum post for the current user."""
    try:
        supertokens_user_id = session.get_user_id()
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Validate post exists
        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        user_id_str = str(mongo_user.id)
        existing = await UserBookmark.find_one(
            UserBookmark.user_id == user_id_str,
            UserBookmark.target_id == str(post.id),
        )
        if existing:
            await existing.delete()
            # Recalculate stats so dashboard reflects updated bookmark count
            try:
                await UserActivityService.recalculate_user_stats(user_id_str)
            except Exception:
                pass
            return {"bookmarked": False}

        # Use centralized service to log activity and recalc stats
        await UserActivityService.add_bookmark(
            user_id=user_id_str,
            target_type="forum_post",
            target_id=str(post.id),
            target_title=post.title,
            target_category=post.category,
        )
        return {"bookmarked": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling bookmark for forum post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bookmark")