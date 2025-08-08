"""Dashboard service for statistics and analytics."""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from sqlmodel import Session, select, func, and_, or_, desc, asc
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.dashboard import (
    DashboardStatistics, UserStatistics, ContentStatistics,
    EntityCount, ActivityFeedItem, ActivityFeedResponse,
    TrendingContent, TrendingContentResponse, PerformanceMetrics,
    TimeRange, QuickStats, AnalyticsQuery, AnalyticsResponse,
    SystemMetrics
)
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.forum import ForumTopic, ForumPost
from app.models.message import Message, Conversation
from app.models.notification import Notification
from app.models.use_case import UseCase, UseCaseStatus, UseCaseCategory
from app.core.logging import get_logger
from app.services.performance import cache_result

logger = get_logger(__name__)
import asyncio


class DashboardService:
    """Service for dashboard statistics and analytics."""
    
    @staticmethod
    @cache_result(ttl_seconds=300, key_prefix="dashboard_stats")
    async def get_dashboard_statistics(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        time_range: TimeRange = TimeRange.MONTH
    ) -> DashboardStatistics:
        """Get comprehensive dashboard statistics."""
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = DashboardService._get_start_date(end_date, time_range)
        
        # Run all statistics queries concurrently
        user_stats_task = DashboardService._get_user_statistics(db, organization_id, start_date, end_date)
        content_stats_task = DashboardService._get_content_statistics(db, mongo_db, organization_id, start_date, end_date)
        system_stats_task = DashboardService._get_system_metrics(db, organization_id)
        recent_activities_task = DashboardService._get_recent_activities(db, mongo_db, organization_id, limit=10)
        trending_posts_task = DashboardService._get_trending_forum_posts(db, organization_id, limit=5)
        trending_use_cases_task = DashboardService._get_trending_use_cases(mongo_db, organization_id, limit=5)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            user_stats_task,
            content_stats_task,
            system_stats_task,
            recent_activities_task,
            trending_posts_task,
            trending_use_cases_task,
            return_exceptions=True
        )
        
        # Extract results
        user_stats = results[0] if not isinstance(results[0], Exception) else UserStatistics()
        content_stats = results[1] if not isinstance(results[1], Exception) else ContentStatistics()
        system_stats = results[2] if not isinstance(results[2], Exception) else SystemMetrics()
        recent_activities = results[3] if not isinstance(results[3], Exception) else []
        trending_posts = results[4] if not isinstance(results[4], Exception) else []
        trending_use_cases = results[5] if not isinstance(results[5], Exception) else []
        
        # Calculate key metrics
        key_metrics = {
            "user_growth_rate": user_stats.total_users.growth_rate or 0.0,
            "content_engagement": content_stats.content_engagement.get("average_engagement", 0.0),
            "activity_score": len(recent_activities) / 10.0,  # normalized to 0-1
            "system_health": (system_stats.uptime_percentage / 100.0 + (1 - system_stats.error_rate)) / 2
        }
        
        return DashboardStatistics(
            organization_id=organization_id,
            time_range=time_range,
            users=user_stats,
            content=content_stats,
            system=system_stats,
            recent_activities=recent_activities,
            trending_posts=trending_posts,
            trending_use_cases=trending_use_cases,
            key_metrics=key_metrics
        )
    
    @staticmethod
    async def _get_user_statistics(
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> UserStatistics:
        """Get user-related statistics."""
        # Total users
        total_users = db.exec(
            select(func.count(User.id)).where(User.organization_id == organization_id)
        ).one()
        
        # New users in different periods
        new_today = db.exec(
            select(func.count(User.id)).where(
                and_(
                    User.organization_id == organization_id,
                    User.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                )
            )
        ).one()
        
        new_this_week = db.exec(
            select(func.count(User.id)).where(
                and_(
                    User.organization_id == organization_id,
                    User.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
        ).one()
        
        new_this_month = db.exec(
            select(func.count(User.id)).where(
                and_(
                    User.organization_id == organization_id,
                    User.created_at >= start_date
                )
            )
        ).one()
        
        # Active users (users with activity in the last 30 days)
        active_users = db.exec(
            select(func.count(User.id)).where(
                and_(
                    User.organization_id == organization_id,
                    User.last_active >= datetime.utcnow() - timedelta(days=30)
                )
            )
        ).one()
        
        # Role distribution
        role_stats = db.exec(
            select(User.role, func.count(User.id))
            .where(User.organization_id == organization_id)
            .group_by(User.role)
        ).all()
        role_distribution = {role.value: count for role, count in role_stats}
        
        # Top contributors (users with most forum posts)
        top_contributors = db.exec(
            select(User.first_name, User.last_name, func.count(ForumPost.id).label("post_count"))
            .join(ForumPost, User.id == ForumPost.author_id)
            .where(User.organization_id == organization_id)
            .group_by(User.id, User.first_name, User.last_name)
            .order_by(desc("post_count"))
            .limit(5)
        ).all()
        
        top_contributors_list = [
            {
                "name": f"{first_name} {last_name}",
                "post_count": count
            }
            for first_name, last_name, count in top_contributors
        ]
        
        # Calculate growth rate
        previous_period_start = start_date - (end_date - start_date)
        previous_users = db.exec(
            select(func.count(User.id)).where(
                and_(
                    User.organization_id == organization_id,
                    User.created_at < start_date
                )
            )
        ).one()
        
        growth_rate = 0.0
        if previous_users > 0:
            growth_rate = ((new_this_month / previous_users) * 100) if previous_users > 0 else 0.0
        
        total_users_count = EntityCount(
            total=total_users,
            active=active_users,
            new_today=new_today,
            new_this_week=new_this_week,
            new_this_month=new_this_month,
            growth_rate=growth_rate
        )
        
        return UserStatistics(
            total_users=total_users_count,
            online_users=0,  # Would need session tracking
            top_contributors=top_contributors_list,
            role_distribution=role_distribution
        )
    
    @staticmethod
    async def _get_content_statistics(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> ContentStatistics:
        """Get content-related statistics."""
        # Forum statistics
        total_topics = db.exec(
            select(func.count(ForumTopic.id)).where(ForumTopic.organization_id == organization_id)
        ).one()
        
        total_posts = db.exec(
            select(func.count(ForumPost.id))
            .join(ForumTopic, ForumPost.topic_id == ForumTopic.id)
            .where(ForumTopic.organization_id == organization_id)
        ).one()
        
        new_posts_this_month = db.exec(
            select(func.count(ForumPost.id))
            .join(ForumTopic, ForumPost.topic_id == ForumTopic.id)
            .where(
                and_(
                    ForumTopic.organization_id == organization_id,
                    ForumPost.created_at >= start_date
                )
            )
        ).one()
        
        # Use case statistics from MongoDB
        use_cases_cursor = mongo_db.use_cases.aggregate([
            {"$match": {"organization_id": str(organization_id)}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "published": {"$sum": {"$cond": [{"$eq": ["$status", "published"]}, 1, 0]}},
                "new_this_month": {
                    "$sum": {"$cond": [{"$gte": ["$created_at", start_date]}, 1, 0]}
                }
            }}
        ])
        use_case_stats = await use_cases_cursor.to_list(1)
        use_case_data = use_case_stats[0] if use_case_stats else {"total": 0, "published": 0, "new_this_month": 0}
        
        # Message statistics
        total_messages = db.exec(
            select(func.count(Message.id)).where(Message.organization_id == organization_id)
        ).one()
        
        new_messages_this_month = db.exec(
            select(func.count(Message.id)).where(
                and_(
                    Message.organization_id == organization_id,
                    Message.created_at >= start_date
                )
            )
        ).one()
        
        # Popular categories from use cases
        categories_cursor = mongo_db.use_cases.aggregate([
            {"$match": {"organization_id": str(organization_id), "status": "published"}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ])
        categories_data = await categories_cursor.to_list(5)
        popular_categories = [{"category": cat["_id"], "count": cat["count"]} for cat in categories_data]
        
        return ContentStatistics(
            forum_posts=EntityCount(total=total_posts, new_this_month=new_posts_this_month),
            forum_topics=EntityCount(total=total_topics),
            use_cases=EntityCount(
                total=use_case_data["total"],
                active=use_case_data["published"],
                new_this_month=use_case_data["new_this_month"]
            ),
            messages=EntityCount(total=total_messages, new_this_month=new_messages_this_month),
            popular_categories=popular_categories
        )
    
    @staticmethod
    async def _get_system_metrics(
        db: Session,
        organization_id: UUID
    ) -> SystemMetrics:
        """Get system performance metrics."""
        # Mock system metrics - in production, these would come from monitoring systems
        return SystemMetrics(
            total_requests=10000,
            api_response_time=150.0,
            database_query_time=25.0,
            cache_hit_rate=0.85,
            error_rate=0.01,
            uptime_percentage=99.9
        )
    
    @staticmethod
    async def _get_recent_activities(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent activity feed."""
        activities = []
        
        # Recent forum posts
        recent_posts = db.exec(
            select(ForumPost.id, ForumPost.created_at, User.first_name, User.last_name, ForumTopic.title)
            .join(User, ForumPost.author_id == User.id)
            .join(ForumTopic, ForumPost.topic_id == ForumTopic.id)
            .where(ForumTopic.organization_id == organization_id)
            .order_by(desc(ForumPost.created_at))
            .limit(limit // 2)
        ).all()
        
        for post_id, created_at, first_name, last_name, topic_title in recent_posts:
            activities.append({
                "id": str(post_id),
                "type": "forum_post",
                "title": "New forum post",
                "description": f"Posted in {topic_title}",
                "actor_name": f"{first_name} {last_name}",
                "created_at": created_at.isoformat()
            })
        
        # Recent use cases from MongoDB
        use_cases_cursor = mongo_db.use_cases.find(
            {"organization_id": str(organization_id), "status": "published"},
            sort=[("published_at", -1)],
            limit=limit // 2
        )
        async for use_case in use_cases_cursor:
            activities.append({
                "id": use_case["id"],
                "type": "use_case_published",
                "title": "New use case published",
                "description": use_case["title"],
                "actor_name": use_case["published_by"]["name"],
                "created_at": use_case["published_at"].isoformat()
            })
        
        # Sort by created_at
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        return activities[:limit]
    
    @staticmethod
    async def _get_trending_forum_posts(
        db: Session,
        organization_id: UUID,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get trending forum posts."""
        # Simple trending algorithm based on recent activity and likes
        trending_posts = db.exec(
            select(
                ForumPost.id,
                ForumPost.created_at,
                ForumPost.likes,
                ForumPost.views,
                ForumTopic.title,
                User.first_name,
                User.last_name
            )
            .join(User, ForumPost.author_id == User.id)
            .join(ForumTopic, ForumPost.topic_id == ForumTopic.id)
            .where(
                and_(
                    ForumTopic.organization_id == organization_id,
                    ForumPost.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            )
            .order_by(desc(ForumPost.likes + ForumPost.views))
            .limit(limit)
        ).all()
        
        return [
            {
                "id": str(post_id),
                "type": "forum_post",
                "title": title,
                "author_name": f"{first_name} {last_name}",
                "likes": likes,
                "views": views,
                "created_at": created_at.isoformat(),
                "score": likes + views
            }
            for post_id, created_at, likes, views, title, first_name, last_name in trending_posts
        ]
    
    @staticmethod
    async def _get_trending_use_cases(
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get trending use cases."""
        # Trending algorithm based on views, likes, and recency
        pipeline = [
            {"$match": {
                "organization_id": str(organization_id),
                "status": "published",
                "published_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            }},
            {"$addFields": {
                "score": {
                    "$add": [
                        "$metrics.views",
                        {"$multiply": ["$metrics.likes", 2]},
                        {"$multiply": ["$metrics.saves", 3]}
                    ]
                }
            }},
            {"$sort": {"score": -1}},
            {"$limit": limit}
        ]
        
        cursor = mongo_db.use_cases.aggregate(pipeline)
        trending_cases = []
        
        async for use_case in cursor:
            trending_cases.append({
                "id": use_case["id"],
                "type": "use_case",
                "title": use_case["title"],
                "author_name": use_case["published_by"]["name"],
                "views": use_case["metrics"]["views"],
                "likes": use_case["metrics"]["likes"],
                "created_at": use_case["published_at"].isoformat(),
                "score": use_case["score"]
            })
        
        return trending_cases
    
    @staticmethod
    @cache_result(ttl_seconds=60, key_prefix="quick_stats")
    async def get_quick_stats(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        user_id: UUID,
        organization_id: UUID
    ) -> QuickStats:
        """Get quick statistics for dashboard header."""
        # Count forum posts
        total_posts = db.exec(
            select(func.count(ForumPost.id))
            .join(ForumTopic, ForumPost.topic_id == ForumTopic.id)
            .where(ForumTopic.organization_id == organization_id)
        ).one()
        
        # Count users
        total_users = db.exec(
            select(func.count(User.id)).where(User.organization_id == organization_id)
        ).one()
        
        # Count use cases
        use_cases_count = await mongo_db.use_cases.count_documents({
            "organization_id": str(organization_id),
            "status": "published"
        })
        
        # Unread messages
        unread_messages = db.exec(
            select(func.count(Message.id)).where(
                and_(
                    Message.recipient_id == user_id,
                    Message.is_read == False
                )
            )
        ).one()
        
        # Unread notifications
        unread_notifications = db.exec(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        ).one()
        
        return QuickStats(
            total_posts=total_posts,
            total_users=total_users,
            total_use_cases=use_cases_count,
            unread_messages=unread_messages,
            pending_tasks=unread_notifications
        )
    
    @staticmethod
    def _get_start_date(end_date: datetime, time_range: TimeRange) -> datetime:
        """Calculate start date based on time range."""
        if time_range == TimeRange.DAY:
            return end_date - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            return end_date - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            return end_date - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            return end_date - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            return end_date - timedelta(days=365)
        else:  # ALL_TIME
            return datetime.min.replace(tzinfo=end_date.tzinfo)