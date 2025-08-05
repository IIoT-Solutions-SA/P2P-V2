"""
User Activity and Stats Management Service
Handles dashboard statistics, activity feeds, and user engagement data
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.mongo_models import (
    UserActivity, UserStats, UserBookmark, DraftPost,
    ForumPost, ForumReply, UseCase, User
)
import logging

logger = logging.getLogger(__name__)

class UserActivityService:
    """Service for managing user activities and statistics"""
    
    @staticmethod
    async def log_activity(user_id: str, activity_type: str, target_id: str, 
                          target_title: Optional[str] = None, 
                          target_category: Optional[str] = None,
                          description: Optional[str] = None):
        """Log a user activity for dashboard feed"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                target_id=target_id,
                target_title=target_title,
                target_category=target_category,
                description=description
            )
            await activity.insert()
            logger.info(f"Logged activity: {activity_type} by user {user_id}")
            
            # Trigger stats recalculation
            await UserActivityService.recalculate_user_stats(user_id)
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    @staticmethod
    async def get_user_activities(user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent activities for a user's dashboard feed"""
        try:
            activities = await UserActivity.find(
                UserActivity.user_id == user_id
            ).sort(-UserActivity.created_at).limit(limit).to_list()
            
            # Convert to dashboard format
            feed_items = []
            for activity in activities:
                # Calculate time ago
                time_diff = datetime.utcnow() - activity.created_at
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours} hours ago"
                else:
                    minutes = time_diff.seconds // 60
                    time_ago = f"{minutes} minutes ago"
                
                feed_items.append({
                    "type": activity.activity_type,
                    "action": UserActivityService._get_action_text(activity.activity_type),
                    "content": activity.target_title or activity.description,
                    "time": time_ago,
                    "category": activity.target_category
                })
            
            return feed_items
            
        except Exception as e:
            logger.error(f"Error getting user activities: {e}")
            return []
    
    @staticmethod
    async def get_community_activities(limit: int = 10) -> List[Dict]:
        """Get recent community activities for dashboard feed"""
        try:
            activities = await UserActivity.find().sort(-UserActivity.created_at).limit(limit).to_list()
            
            # Get user names for activities
            from bson import ObjectId
            user_names = {}
            for activity in activities:
                if activity.user_id not in user_names:
                    try:
                        # Convert string ID to ObjectId for lookup
                        user = await User.find_one(User.id == ObjectId(activity.user_id))
                        user_names[activity.user_id] = user.name if user else "Unknown User"
                    except Exception as e:
                        logger.error(f"Error looking up user {activity.user_id}: {e}")
                        user_names[activity.user_id] = "Unknown User"
            
            # Convert to dashboard format
            feed_items = []
            for activity in activities:
                time_diff = datetime.utcnow() - activity.created_at
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours} hours ago"
                else:
                    minutes = max(1, time_diff.seconds // 60)
                    time_ago = f"{minutes} minutes ago"
                
                feed_items.append({
                    "type": activity.activity_type,
                    "user": user_names.get(activity.user_id, "Unknown User"),
                    "action": UserActivityService._get_action_text(activity.activity_type),
                    "content": activity.target_title or activity.description,
                    "time": time_ago,
                    "category": activity.target_category
                })
            
            return feed_items
            
        except Exception as e:
            logger.error(f"Error getting community activities: {e}")
            return []
    
    @staticmethod 
    def _get_action_text(activity_type: str) -> str:
        """Convert activity type to human readable action"""
        action_map = {
            "question": "asked a new question",
            "answer": "answered a question", 
            "usecase": "added a new use case",
            "bookmark": "bookmarked an item",
            "like": "liked a post",
            "comment": "commented on a post"
        }
        return action_map.get(activity_type, "performed an action")
    
    @staticmethod
    async def recalculate_user_stats(user_id: str):
        """Calculate/update user statistics for dashboard"""
        try:
            # Count questions asked (forum posts by user)
            questions_asked = await ForumPost.find(ForumPost.author_id == user_id).count()
            
            # Count answers given (forum replies by user)  
            answers_given = await ForumReply.find(ForumReply.author_id == user_id).count()
            
            # Count best answers
            best_answers = await ForumReply.find(
                ForumReply.author_id == user_id,
                ForumReply.is_best_answer == True
            ).count()
            
            # Count use cases submitted
            use_cases_submitted = await UseCase.find(UseCase.submitted_by == user_id).count()
            
            # Count bookmarks/saved items
            bookmarks_saved = await UserBookmark.find(UserBookmark.user_id == user_id).count()
            
            # Count draft posts  
            draft_posts = await DraftPost.find(DraftPost.user_id == user_id).count()
            
            # Calculate total upvotes received
            user_posts = await ForumPost.find(ForumPost.author_id == user_id).to_list()
            user_replies = await ForumReply.find(ForumReply.author_id == user_id).to_list()
            total_upvotes_received = sum(post.upvotes for post in user_posts) + sum(reply.upvotes for reply in user_replies)
            
            # Calculate reputation score (weighted scoring)
            reputation_score = (
                questions_asked * 2 +      # 2 points per question
                answers_given * 3 +        # 3 points per answer  
                best_answers * 15 +        # 15 points per best answer
                use_cases_submitted * 10 + # 10 points per use case
                total_upvotes_received * 1 # 1 point per upvote
            )
            
            # Calculate activity level (based on recent activity)
            recent_activities = await UserActivity.find(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            activity_level = min(100.0, (recent_activities / 20.0) * 100)  # Cap at 100%
            
            # Update or create user stats
            user_stats = await UserStats.find_one(UserStats.user_id == user_id)
            if user_stats:
                user_stats.questions_asked = questions_asked
                user_stats.answers_given = answers_given
                user_stats.best_answers = best_answers
                user_stats.use_cases_submitted = use_cases_submitted
                user_stats.bookmarks_saved = bookmarks_saved
                user_stats.total_upvotes_received = total_upvotes_received
                user_stats.reputation_score = reputation_score
                user_stats.activity_level = activity_level
                user_stats.draft_posts = draft_posts
                user_stats.last_calculated = datetime.utcnow()
                await user_stats.save()
            else:
                user_stats = UserStats(
                    user_id=user_id,
                    questions_asked=questions_asked,
                    answers_given=answers_given,
                    best_answers=best_answers,
                    use_cases_submitted=use_cases_submitted,
                    bookmarks_saved=bookmarks_saved,
                    total_upvotes_received=total_upvotes_received,
                    reputation_score=reputation_score,
                    activity_level=activity_level,
                    draft_posts=draft_posts
                )
                await user_stats.insert()
            
            logger.info(f"Updated stats for user {user_id}: {reputation_score} reputation")
            return user_stats
            
        except Exception as e:
            logger.error(f"Error calculating user stats: {e}")
            return None
    
    @staticmethod
    async def get_user_stats(user_id: str) -> Optional[UserStats]:
        """Get user statistics for dashboard"""
        try:
            user_stats = await UserStats.find_one(UserStats.user_id == user_id)
            if not user_stats:
                # Calculate stats for first time
                user_stats = await UserActivityService.recalculate_user_stats(user_id)
            return user_stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    @staticmethod
    async def add_bookmark(user_id: str, target_type: str, target_id: str, target_title: str, target_category: Optional[str] = None):
        """Add a bookmark/saved item for user"""
        try:
            # Check if already bookmarked
            existing = await UserBookmark.find_one(
                UserBookmark.user_id == user_id,
                UserBookmark.target_id == target_id
            )
            if existing:
                return existing
            
            bookmark = UserBookmark(
                user_id=user_id,
                target_type=target_type,
                target_id=target_id,
                target_title=target_title,
                target_category=target_category
            )
            await bookmark.insert()
            
            # Log activity
            await UserActivityService.log_activity(
                user_id=user_id,
                activity_type="bookmark",
                target_id=target_id,
                target_title=target_title,
                target_category=target_category,
                description=f"Bookmarked: {target_title}"
            )
            
            return bookmark
            
        except Exception as e:
            logger.error(f"Error adding bookmark: {e}")
            return None
    
    @staticmethod
    async def get_user_bookmarks(user_id: str, limit: int = 10) -> List[UserBookmark]:
        """Get user's bookmarked items"""
        try:
            bookmarks = await UserBookmark.find(
                UserBookmark.user_id == user_id
            ).sort(-UserBookmark.created_at).limit(limit).to_list()
            return bookmarks
        except Exception as e:
            logger.error(f"Error getting user bookmarks: {e}")
            return []
    
    @staticmethod
    async def create_draft_post(user_id: str, title: str, content: str, post_type: str, category: Optional[str] = None, tags: List[str] = None):
        """Create a draft post for user"""
        try:
            draft = DraftPost(
                user_id=user_id,
                title=title,
                content=content,
                post_type=post_type,
                category=category,
                tags=tags or []
            )
            await draft.insert()
            
            # Trigger stats recalculation
            await UserActivityService.recalculate_user_stats(user_id)
            
            return draft
            
        except Exception as e:
            logger.error(f"Error creating draft post: {e}")
            return None
    
    @staticmethod
    async def get_user_drafts(user_id: str) -> List[DraftPost]:
        """Get user's draft posts"""
        try:
            drafts = await DraftPost.find(
                DraftPost.user_id == user_id
            ).sort(-DraftPost.updated_at).to_list()
            return drafts
        except Exception as e:
            logger.error(f"Error getting user drafts: {e}")
            return []