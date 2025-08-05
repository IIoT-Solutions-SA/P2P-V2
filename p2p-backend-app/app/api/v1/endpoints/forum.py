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
from app.models.mongo_models import ForumPost, ForumReply, User as MongoUser
from typing import List, Optional
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/posts")
async def get_forum_posts(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, description="Number of posts to return"),
    session: SessionContainer = Depends(verify_session())
):
    """Get forum posts with optional category filter"""
    try:
        # Build query
        query = {}
        if category and category != "all":
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
                "category": post.category,
                "content": post.content,
                "replies": reply_count,
                "views": post.views,
                "likes": post.upvotes,
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
async def get_forum_categories():
    """Get forum categories with real post counts"""
    try:
        # Get all posts to calculate category counts
        all_posts = await ForumPost.find_all().to_list()
        
        # Count posts by category
        category_counts = {}
        for post in all_posts:
            category = post.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Build categories response
        categories = [
            {
                "id": "all",
                "name": "All Topics", 
                "count": len(all_posts),
                "color": "bg-gray-100"
            }
        ]
        
        # Add specific categories
        category_configs = {
            "Automation": {"color": "bg-blue-100"},
            "Quality Management": {"color": "bg-green-100"},
            "Maintenance": {"color": "bg-yellow-100"},
            "Artificial Intelligence": {"color": "bg-purple-100"},
            "Internet of Things": {"color": "bg-orange-100"}
        }
        
        for category_name, config in category_configs.items():
            count = category_counts.get(category_name, 0)
            categories.append({
                "id": category_name.lower().replace(" ", "_"),
                "name": category_name,
                "count": count,
                "color": config["color"]
            })
        
        return {
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting forum categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum categories")

@router.get("/posts/{post_id}")
async def get_forum_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session())
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
        
        # Increment view count
        post.views += 1
        await post.save()
        
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
            
            reply_data.append({
                "id": str(reply.id),
                "author": reply_author_name,
                "authorTitle": "Community Member",
                "content": reply.content,
                "timeAgo": reply_time_ago,
                "likes": reply.upvotes,
                "isVerified": True,
                "isBestAnswer": reply.is_best_answer,
                "replies": []  # Nested replies can be added later
            })
        
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
    session: SessionContainer = Depends(verify_session())
):
    """Like/unlike a forum post"""
    try:
        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # For now, just increment likes - can add user tracking later
        post.upvotes += 1
        await post.save()
        
        return {
            "success": True,
            "likes": post.upvotes
        }
        
    except Exception as e:
        logger.error(f"Error liking post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to like post")

@router.post("/posts/{post_id}/replies")
async def create_reply(
    post_id: str,
    reply_data: dict,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Create a new reply to a forum post"""
    try:
        supertokens_user_id = session.get_user_id()
        
        # Get user info
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Verify post exists
        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Create reply
        reply = ForumReply(
            post_id=post_id,
            author_id=str(mongo_user.id),
            content=reply_data.get("content", ""),
            upvotes=0,
            is_best_answer=False
        )
        await reply.insert()
        
        # Update post reply count
        post.reply_count += 1
        await post.save()
        
        return {
            "success": True,
            "reply_id": str(reply.id)
        }
        
    except Exception as e:
        logger.error(f"Error creating reply: {e}")
        raise HTTPException(status_code=500, detail="Failed to create reply")

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