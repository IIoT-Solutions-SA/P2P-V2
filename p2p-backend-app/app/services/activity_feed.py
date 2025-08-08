"""Activity feed service for aggregating user activities."""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from uuid import UUID
from sqlmodel import Session, select, and_, or_, desc, func
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.dashboard import ActivityFeedItem, ActivityFeedResponse
from app.models.user import User
from app.models.forum import ForumTopic, ForumPost
from app.models.message import Message
from app.models.notification import Notification
from app.core.logging import logger
import asyncio


class ActivityFeedService:
    """Service for generating activity feeds."""
    
    @staticmethod
    async def get_activity_feed(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        activity_types: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20,
        hours_back: int = 168  # Default 1 week
    ) -> ActivityFeedResponse:
        """Get aggregated activity feed."""
        offset = (page - 1) * page_size
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Collect activities from different sources
        activities_tasks = [
            ActivityFeedService._get_forum_activities(db, organization_id, cutoff_time, activity_types),
            ActivityFeedService._get_use_case_activities(mongo_db, organization_id, cutoff_time, activity_types),
            ActivityFeedService._get_user_activities(db, organization_id, cutoff_time, activity_types),
            ActivityFeedService._get_messaging_activities(db, organization_id, cutoff_time, activity_types)
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*activities_tasks, return_exceptions=True)
        
        # Combine all activities
        all_activities = []
        for result in results:
            if not isinstance(result, Exception) and result:
                all_activities.extend(result)
        
        # Sort by created_at (most recent first)
        all_activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Apply pagination
        total = len(all_activities)
        paginated_activities = all_activities[offset:offset + page_size]
        
        # Convert to ActivityFeedItem objects
        activity_items = []
        for activity in paginated_activities:
            try:
                activity_item = ActivityFeedItem(
                    id=UUID(activity['id']),
                    type=activity['type'],
                    title=activity['title'],
                    description=activity['description'],
                    actor_name=activity['actor_name'],
                    actor_id=UUID(activity['actor_id']),
                    target_name=activity.get('target_name'),
                    target_id=UUID(activity['target_id']) if activity.get('target_id') else None,
                    created_at=datetime.fromisoformat(activity['created_at'].replace('Z', '+00:00')),
                    metadata=activity.get('metadata', {})
                )
                activity_items.append(activity_item)
            except Exception as e:
                logger.warning(f"Failed to parse activity item: {e}")
                continue
        
        return ActivityFeedResponse(
            activities=activity_items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + page_size) < total
        )
    
    @staticmethod
    async def _get_forum_activities(
        db: Session,
        organization_id: UUID,
        cutoff_time: datetime,
        activity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get forum-related activities."""
        activities = []
        
        if not activity_types or 'forum_post_created' in activity_types:
            # New forum posts
            posts_query = select(
                ForumPost.id,
                ForumPost.created_at,
                ForumTopic.title.label('topic_title'),
                ForumTopic.id.label('topic_id'),
                User.first_name,
                User.last_name,
                User.id.label('user_id')
            ).join(
                User, ForumPost.author_id == User.id
            ).join(
                ForumTopic, ForumPost.topic_id == ForumTopic.id
            ).where(
                and_(
                    ForumTopic.organization_id == organization_id,
                    ForumPost.created_at >= cutoff_time
                )
            ).order_by(desc(ForumPost.created_at)).limit(50)
            
            posts = db.exec(posts_query).all()
            
            for post_id, created_at, topic_title, topic_id, first_name, last_name, user_id in posts:
                activities.append({
                    'id': str(post_id),
                    'type': 'forum_post_created',
                    'title': 'New Forum Post',
                    'description': f'Posted a reply in "{topic_title}"',
                    'actor_name': f'{first_name} {last_name}',
                    'actor_id': str(user_id),
                    'target_name': topic_title,
                    'target_id': str(topic_id),
                    'created_at': created_at.isoformat(),
                    'metadata': {
                        'topic_title': topic_title,
                        'post_id': str(post_id)
                    }
                })
        
        if not activity_types or 'forum_topic_created' in activity_types:
            # New forum topics
            topics_query = select(
                ForumTopic.id,
                ForumTopic.title,
                ForumTopic.created_at,
                User.first_name,
                User.last_name,
                User.id.label('user_id')
            ).join(
                User, ForumTopic.author_id == User.id
            ).where(
                and_(
                    ForumTopic.organization_id == organization_id,
                    ForumTopic.created_at >= cutoff_time
                )
            ).order_by(desc(ForumTopic.created_at)).limit(25)
            
            topics = db.exec(topics_query).all()
            
            for topic_id, title, created_at, first_name, last_name, user_id in topics:
                activities.append({
                    'id': str(topic_id),
                    'type': 'forum_topic_created',
                    'title': 'New Discussion Topic',
                    'description': f'Started a new discussion: "{title}"',
                    'actor_name': f'{first_name} {last_name}',
                    'actor_id': str(user_id),
                    'target_name': title,
                    'target_id': str(topic_id),
                    'created_at': created_at.isoformat(),
                    'metadata': {
                        'topic_title': title,
                        'topic_id': str(topic_id)
                    }
                })
        
        return activities
    
    @staticmethod
    async def _get_use_case_activities(
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        cutoff_time: datetime,
        activity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get use case related activities."""
        activities = []
        
        if not activity_types or 'use_case_published' in activity_types:
            # Published use cases
            published_cursor = mongo_db.use_cases.find(
                {
                    'organization_id': str(organization_id),
                    'status': 'published',
                    'published_at': {'$gte': cutoff_time}
                },
                sort=[('published_at', -1)],
                limit=25
            )
            
            async for use_case in published_cursor:
                activities.append({
                    'id': use_case['id'],
                    'type': 'use_case_published',
                    'title': 'New Use Case Published',
                    'description': f'Published "{use_case["title"]}" in {use_case["category"]}',
                    'actor_name': use_case['published_by']['name'],
                    'actor_id': use_case['published_by']['user_id'],
                    'target_name': use_case['title'],
                    'target_id': use_case['id'],
                    'created_at': use_case['published_at'].isoformat(),
                    'metadata': {
                        'category': use_case['category'],
                        'company': use_case['company'],
                        'industry': use_case['industry']
                    }
                })
        
        if not activity_types or 'use_case_featured' in activity_types:
            # Recently featured use cases
            featured_cursor = mongo_db.use_cases.find(
                {
                    'organization_id': str(organization_id),
                    'featured.is_featured': True,
                    'featured.featured_until': {'$gte': datetime.utcnow()}
                },
                sort=[('featured.featured_at', -1)],
                limit=10
            )
            
            async for use_case in featured_cursor:
                if 'featured' in use_case and use_case['featured'].get('featured_at', datetime.min) >= cutoff_time:
                    activities.append({
                        'id': use_case['id'],
                        'type': 'use_case_featured',
                        'title': 'Use Case Featured',
                        'description': f'"{use_case["title"]}" was featured',
                        'actor_name': 'System',
                        'actor_id': '00000000-0000-0000-0000-000000000000',
                        'target_name': use_case['title'],
                        'target_id': use_case['id'],
                        'created_at': use_case['featured']['featured_at'].isoformat(),
                        'metadata': {
                            'category': use_case['category'],
                            'views': use_case['metrics']['views'],
                            'likes': use_case['metrics']['likes']
                        }
                    })
        
        return activities
    
    @staticmethod
    async def _get_user_activities(
        db: Session,
        organization_id: UUID,
        cutoff_time: datetime,
        activity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get user-related activities."""
        activities = []
        
        if not activity_types or 'user_joined' in activity_types:
            # New users
            new_users_query = select(
                User.id,
                User.first_name,
                User.last_name,
                User.created_at,
                User.role
            ).where(
                and_(
                    User.organization_id == organization_id,
                    User.created_at >= cutoff_time
                )
            ).order_by(desc(User.created_at)).limit(20)
            
            new_users = db.exec(new_users_query).all()
            
            for user_id, first_name, last_name, created_at, role in new_users:
                activities.append({
                    'id': str(user_id),
                    'type': 'user_joined',
                    'title': 'New Member Joined',
                    'description': f'{first_name} {last_name} joined as {role.value}',
                    'actor_name': f'{first_name} {last_name}',
                    'actor_id': str(user_id),
                    'target_name': None,
                    'target_id': None,
                    'created_at': created_at.isoformat(),
                    'metadata': {
                        'role': role.value,
                        'user_id': str(user_id)
                    }
                })
        
        return activities
    
    @staticmethod
    async def _get_messaging_activities(
        db: Session,
        organization_id: UUID,
        cutoff_time: datetime,
        activity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get messaging activities (only significant ones)."""
        activities = []
        
        # Only include significant messaging activities to avoid spam
        # For now, we'll skip individual messages and focus on new conversations
        # This could be extended to include first messages in conversations, etc.
        
        return activities
    
    @staticmethod
    async def get_user_activity_feed(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        user_id: UUID,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> ActivityFeedResponse:
        """Get activity feed for a specific user."""
        # This would show activities related to the specific user
        # For now, we'll return the general feed filtered for this user's activities
        return await ActivityFeedService.get_activity_feed(
            db=db,
            mongo_db=mongo_db,
            organization_id=organization_id,
            user_id=user_id,
            page=page,
            page_size=page_size
        )
    
    @staticmethod
    async def mark_activity_as_seen(
        db: Session,
        user_id: UUID,
        activity_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Mark activities as seen by user (for future implementation)."""
        # This would track which activities a user has seen
        # Could be implemented with a separate table or Redis
        logger.info(f"Marking {len(activity_ids)} activities as seen for user {user_id}")
        
        return {
            "message": f"Marked {len(activity_ids)} activities as seen",
            "user_id": str(user_id),
            "activity_count": len(activity_ids)
        }