"""Trending content service for identifying popular content."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from sqlmodel import Session, select, and_, or_, desc, func
from motor.motor_asyncio import AsyncIOMotorDatabase
from enum import Enum

from app.models.dashboard import TrendingContent, TrendingContentResponse, TimeRange
from app.models.user import User
from app.models.forum import ForumTopic, ForumPost
from app.core.logging import get_logger
import asyncio

logger = get_logger(__name__)
import math


class TrendingAlgorithm(str, Enum):
    """Trending algorithms available."""
    HOT = "hot"  # Reddit-style hot algorithm
    TRENDING = "trending"  # Time-decay with engagement
    POPULAR = "popular"  # Simple engagement count
    RECENT = "recent"  # Most recent with minimum engagement


class TrendingService:
    """Service for identifying trending content."""
    
    @staticmethod
    async def get_trending_content(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        content_types: Optional[List[str]] = None,
        time_window: TimeRange = TimeRange.WEEK,
        algorithm: TrendingAlgorithm = TrendingAlgorithm.HOT,
        limit: int = 20
    ) -> TrendingContentResponse:
        """Get trending content across all types."""
        # Collect trending content from different sources
        tasks = []
        
        if not content_types or 'forum_post' in content_types:
            tasks.append(TrendingService._get_trending_forum_posts(
                db, organization_id, time_window, algorithm, limit // 2
            ))
        
        if not content_types or 'use_case' in content_types:
            tasks.append(TrendingService._get_trending_use_cases(
                mongo_db, organization_id, time_window, algorithm, limit // 2
            ))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all trending content
        all_trending = []
        for result in results:
            if not isinstance(result, Exception) and result:
                all_trending.extend(result)
        
        # Sort by trending score
        all_trending.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results
        trending_content = all_trending[:limit]
        
        # Algorithm info
        algorithm_info = {
            "algorithm_used": algorithm.value,
            "time_window": time_window.value,
            "factors": TrendingService._get_algorithm_info(algorithm),
            "total_candidates_evaluated": len(all_trending)
        }
        
        return TrendingContentResponse(
            content=trending_content,
            algorithm_info=algorithm_info,
            time_window=time_window
        )
    
    @staticmethod
    async def _get_trending_forum_posts(
        db: Session,
        organization_id: UUID,
        time_window: TimeRange,
        algorithm: TrendingAlgorithm,
        limit: int
    ) -> List[TrendingContent]:
        """Get trending forum posts."""
        # Calculate time range
        cutoff_time = TrendingService._get_cutoff_time(time_window)
        
        # Get forum posts with engagement metrics
        query = select(
            ForumPost.id,
            ForumPost.created_at,
            ForumPost.likes,
            ForumPost.views,
            ForumTopic.title,
            User.first_name,
            User.last_name,
            User.id.label('author_id'),
            func.count(ForumPost.id).label('reply_count')  # Self-join would be needed for actual reply count
        ).join(
            User, ForumPost.author_id == User.id
        ).join(
            ForumTopic, ForumPost.topic_id == ForumTopic.id
        ).where(
            and_(
                ForumTopic.organization_id == organization_id,
                ForumPost.created_at >= cutoff_time,
                ForumPost.is_deleted == False
            )
        ).group_by(
            ForumPost.id, ForumPost.created_at, ForumPost.likes, ForumPost.views,
            ForumTopic.title, User.first_name, User.last_name, User.id
        ).order_by(desc(ForumPost.created_at)).limit(limit * 3)  # Get more candidates
        
        posts = db.exec(query).all()
        
        trending_posts = []
        for post_id, created_at, likes, views, title, first_name, last_name, author_id, reply_count in posts:
            # Calculate trending score
            score = TrendingService._calculate_trending_score(
                likes=likes or 0,
                views=views or 0,
                comments=reply_count or 0,
                created_at=created_at,
                algorithm=algorithm
            )
            
            trending_posts.append(TrendingContent(
                id=post_id,
                type='forum_post',
                title=title[:100] + '...' if len(title) > 100 else title,
                author_name=f'{first_name} {last_name}',
                author_id=author_id,
                score=score,
                views=views or 0,
                likes=likes or 0,
                comments=reply_count or 0,
                created_at=created_at,
                trending_since=datetime.utcnow()
            ))
        
        # Sort by score and return top results
        trending_posts.sort(key=lambda x: x.score, reverse=True)
        return trending_posts[:limit]
    
    @staticmethod
    async def _get_trending_use_cases(
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        time_window: TimeRange,
        algorithm: TrendingAlgorithm,
        limit: int
    ) -> List[TrendingContent]:
        """Get trending use cases."""
        cutoff_time = TrendingService._get_cutoff_time(time_window)
        
        # MongoDB aggregation pipeline for trending use cases
        pipeline = [
            {
                "$match": {
                    "organization_id": str(organization_id),
                    "status": "published",
                    "published_at": {"$gte": cutoff_time}
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "id": 1,
                    "title": 1,
                    "published_by": 1,
                    "published_at": 1,
                    "created_at": 1,
                    "metrics": 1,
                    "views": {"$ifNull": ["$metrics.views", 0]},
                    "likes": {"$ifNull": ["$metrics.likes", 0]},
                    "saves": {"$ifNull": ["$metrics.saves", 0]},
                    "inquiries": {"$ifNull": ["$metrics.inquiries", 0]}
                }
            },
            {
                "$limit": limit * 3  # Get more candidates
            }
        ]
        
        cursor = mongo_db.use_cases.aggregate(pipeline)
        trending_cases = []
        
        async for use_case in cursor:
            # Calculate trending score
            score = TrendingService._calculate_trending_score(
                likes=use_case.get('likes', 0),
                views=use_case.get('views', 0),
                comments=use_case.get('inquiries', 0),  # Use inquiries as comments
                saves=use_case.get('saves', 0),
                created_at=use_case.get('published_at', use_case.get('created_at')),
                algorithm=algorithm
            )
            
            trending_cases.append(TrendingContent(
                id=UUID(use_case['id']),
                type='use_case',
                title=use_case['title'],
                author_name=use_case['published_by']['name'],
                author_id=UUID(use_case['published_by']['user_id']),
                score=score,
                views=use_case.get('views', 0),
                likes=use_case.get('likes', 0),
                comments=use_case.get('inquiries', 0),
                created_at=use_case.get('published_at', use_case.get('created_at')),
                trending_since=datetime.utcnow()
            ))
        
        # Sort by score and return top results
        trending_cases.sort(key=lambda x: x.score, reverse=True)
        return trending_cases[:limit]
    
    @staticmethod
    def _calculate_trending_score(
        likes: int,
        views: int,
        comments: int,
        created_at: datetime,
        algorithm: TrendingAlgorithm,
        saves: int = 0
    ) -> float:
        """Calculate trending score based on algorithm."""
        if algorithm == TrendingAlgorithm.HOT:
            return TrendingService._hot_score(likes, comments, created_at)
        elif algorithm == TrendingAlgorithm.TRENDING:
            return TrendingService._trending_score(likes, views, comments, saves, created_at)
        elif algorithm == TrendingAlgorithm.POPULAR:
            return TrendingService._popular_score(likes, views, comments, saves)
        else:  # RECENT
            return TrendingService._recent_score(likes, views, comments, created_at)
    
    @staticmethod
    def _hot_score(likes: int, comments: int, created_at: datetime) -> float:
        """Reddit-style hot algorithm."""
        # Score based on upvotes and time decay
        score = likes + (comments * 0.5)  # Comments worth half a like
        
        # Time decay - content gets less hot over time
        age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
        decay_factor = math.pow(0.8, age_hours / 24)  # 20% decay per day
        
        return score * decay_factor
    
    @staticmethod
    def _trending_score(
        likes: int, 
        views: int, 
        comments: int, 
        saves: int, 
        created_at: datetime
    ) -> float:
        """Comprehensive trending score with engagement weighting."""
        # Weighted engagement score
        engagement_score = (
            (likes * 3) +      # Likes are most valuable
            (saves * 2.5) +    # Saves show deep engagement
            (comments * 2) +   # Comments show interaction
            (views * 0.1)      # Views are least valuable but still count
        )
        
        # Recency boost - newer content gets higher score
        age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
        if age_hours < 24:
            recency_boost = 2.0 - (age_hours / 24)  # 2x boost for very new content
        else:
            recency_boost = math.pow(0.9, (age_hours - 24) / 24)  # 10% decay per day after first day
        
        return engagement_score * recency_boost
    
    @staticmethod
    def _popular_score(likes: int, views: int, comments: int, saves: int) -> float:
        """Simple popularity score without time decay."""
        return (likes * 3) + (saves * 2.5) + (comments * 2) + (views * 0.1)
    
    @staticmethod
    def _recent_score(likes: int, views: int, comments: int, created_at: datetime) -> float:
        """Recent content with minimum engagement threshold."""
        min_engagement = likes + comments + (views / 10)
        
        # Only consider content with some engagement
        if min_engagement < 1:
            return 0.0
        
        # Score heavily weighted toward recency
        age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
        recency_score = max(0, 168 - age_hours) / 168  # Linear decay over 7 days
        
        return recency_score * min_engagement
    
    @staticmethod
    def _get_cutoff_time(time_window: TimeRange) -> datetime:
        """Get cutoff time for trending calculation."""
        now = datetime.utcnow()
        
        if time_window == TimeRange.DAY:
            return now - timedelta(days=1)
        elif time_window == TimeRange.WEEK:
            return now - timedelta(weeks=1)
        elif time_window == TimeRange.MONTH:
            return now - timedelta(days=30)
        elif time_window == TimeRange.QUARTER:
            return now - timedelta(days=90)
        elif time_window == TimeRange.YEAR:
            return now - timedelta(days=365)
        else:  # ALL_TIME
            return datetime.min.replace(tzinfo=now.tzinfo)
    
    @staticmethod
    def _get_algorithm_info(algorithm: TrendingAlgorithm) -> Dict[str, str]:
        """Get information about the trending algorithm."""
        if algorithm == TrendingAlgorithm.HOT:
            return {
                "description": "Reddit-style hot algorithm",
                "factors": "Likes, comments, time decay",
                "best_for": "Balancing popularity with recency"
            }
        elif algorithm == TrendingAlgorithm.TRENDING:
            return {
                "description": "Comprehensive engagement with time weighting",
                "factors": "Likes (3x), saves (2.5x), comments (2x), views (0.1x), recency boost",
                "best_for": "Finding truly engaging recent content"
            }
        elif algorithm == TrendingAlgorithm.POPULAR:
            return {
                "description": "Simple popularity without time decay",
                "factors": "Likes (3x), saves (2.5x), comments (2x), views (0.1x)",
                "best_for": "All-time most popular content"
            }
        else:  # RECENT
            return {
                "description": "Recent content with minimum engagement",
                "factors": "Recency with engagement threshold",
                "best_for": "Latest active content"
            }
    
    @staticmethod
    async def get_trending_by_category(
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        category: str,
        content_type: str = 'use_case',
        limit: int = 10
    ) -> List[TrendingContent]:
        """Get trending content by category."""
        if content_type == 'use_case':
            return await TrendingService._get_trending_use_cases_by_category(
                mongo_db, organization_id, category, limit
            )
        else:
            # Forum categories would need category field in forum topics
            return []
    
    @staticmethod
    async def _get_trending_use_cases_by_category(
        mongo_db: AsyncIOMotorDatabase,
        organization_id: UUID,
        category: str,
        limit: int
    ) -> List[TrendingContent]:
        """Get trending use cases in specific category."""
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        
        pipeline = [
            {
                "$match": {
                    "organization_id": str(organization_id),
                    "status": "published",
                    "category": category,
                    "published_at": {"$gte": cutoff_time}
                }
            },
            {
                "$addFields": {
                    "score": {
                        "$add": [
                            {"$multiply": [{"$ifNull": ["$metrics.likes", 0]}, 3]},
                            {"$multiply": [{"$ifNull": ["$metrics.saves", 0]}, 2.5]},
                            {"$multiply": [{"$ifNull": ["$metrics.inquiries", 0]}, 2]},
                            {"$multiply": [{"$ifNull": ["$metrics.views", 0]}, 0.1]}
                        ]
                    }
                }
            },
            {"$sort": {"score": -1}},
            {"$limit": limit}
        ]
        
        cursor = mongo_db.use_cases.aggregate(pipeline)
        trending_cases = []
        
        async for use_case in cursor:
            trending_cases.append(TrendingContent(
                id=UUID(use_case['id']),
                type='use_case',
                title=use_case['title'],
                author_name=use_case['published_by']['name'],
                author_id=UUID(use_case['published_by']['user_id']),
                score=use_case['score'],
                views=use_case.get('metrics', {}).get('views', 0),
                likes=use_case.get('metrics', {}).get('likes', 0),
                comments=use_case.get('metrics', {}).get('inquiries', 0),
                created_at=use_case['published_at'],
                trending_since=datetime.utcnow()
            ))
        
        return trending_cases