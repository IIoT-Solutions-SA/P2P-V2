"""CRUD operations for forum models."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.forum import (
    ForumCategory,
    ForumTopic, 
    ForumPost,
    ForumTopicLike,
    ForumPostLike,
    ForumTopicView
)
from app.models.user import User
from app.models.organization import Organization
from app.schemas.forum import (
    ForumCategoryCreate,
    ForumCategoryUpdate,
    ForumTopicCreate,
    ForumTopicUpdate,
    ForumTopicSearchQuery,
    ForumPostCreate,
    ForumPostUpdate
)


class CRUDForumCategory(CRUDBase[ForumCategory, ForumCategoryCreate, ForumCategoryUpdate]):
    """CRUD operations for forum categories."""
    
    async def get_active_categories(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ForumCategory]:
        """Get active categories ordered by sort_order."""
        query = (
            select(self.model)
            .where(self.model.is_active == True)
            .order_by(self.model.sort_order, self.model.name)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_counts(
        self,
        db: AsyncSession,
        category_id: UUID,
        topics_delta: int = 0,
        posts_delta: int = 0
    ) -> None:
        """Update topic and post counts for a category."""
        category = await self.get(db, category_id)
        if category:
            category.topics_count = max(0, category.topics_count + topics_delta)
            category.posts_count = max(0, category.posts_count + posts_delta)
            await db.commit()


class CRUDForumTopic(CRUDBase[ForumTopic, ForumTopicCreate, ForumTopicUpdate]):
    """CRUD operations for forum topics."""
    
    async def create_with_user(
        self,
        db: AsyncSession,
        *,
        obj_in: ForumTopicCreate,
        author_id: UUID,
        organization_id: UUID
    ) -> ForumTopic:
        """Create a new topic with author and organization."""
        obj_data = obj_in.model_dump()
        obj_data.update({
            "author_id": author_id,
            "organization_id": organization_id,
            "last_activity_at": datetime.utcnow()
        })
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update category counts
        category_crud = CRUDForumCategory(ForumCategory)
        await category_crud.update_counts(db, obj_in.category_id, topics_delta=1)
        
        return db_obj
    
    async def get_with_relations(
        self,
        db: AsyncSession,
        topic_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> Optional[ForumTopic]:
        """Get topic with author and category information."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.author),
                selectinload(self.model.category)
            )
            .where(self.model.id == topic_id)
        )
        
        if organization_id:
            query = query.where(self.model.organization_id == organization_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi_with_search(
        self,
        db: AsyncSession,
        *,
        search_params: ForumTopicSearchQuery,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ForumTopic], int]:
        """Get topics with search, filter, and pagination."""
        
        # Base query with relations
        query = (
            select(self.model)
            .options(
                selectinload(self.model.author),
                selectinload(self.model.category)
            )
            .where(self.model.organization_id == organization_id)
        )
        
        # Apply filters
        if search_params.search:
            search_term = f"%{search_params.search.lower()}%"
            query = query.where(
                or_(
                    func.lower(self.model.title).contains(search_term),
                    func.lower(self.model.content).contains(search_term),
                    func.lower(self.model.excerpt).contains(search_term)
                )
            )
        
        if search_params.category_id:
            query = query.where(self.model.category_id == search_params.category_id)
            
        if search_params.author_id:
            query = query.where(self.model.author_id == search_params.author_id)
            
        if search_params.is_pinned is not None:
            query = query.where(self.model.is_pinned == search_params.is_pinned)
            
        if search_params.has_best_answer is not None:
            query = query.where(self.model.has_best_answer == search_params.has_best_answer)
        
        # Count query for total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply sorting
        if search_params.sort_by == "title":
            sort_field = self.model.title
        elif search_params.sort_by == "created_at":
            sort_field = self.model.created_at
        elif search_params.sort_by == "views_count":
            sort_field = self.model.views_count
        elif search_params.sort_by == "likes_count":
            sort_field = self.model.likes_count
        else:  # default to last_activity_at
            sort_field = self.model.last_activity_at
            
        if search_params.sort_order == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
            
        # Handle pinned posts (always show first)
        query = query.order_by(desc(self.model.is_pinned), sort_field)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        topics = result.scalars().all()
        
        return topics, total_count
    
    async def increment_views(
        self,
        db: AsyncSession,
        topic_id: UUID,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        organization_id: Optional[UUID] = None
    ) -> None:
        """Increment topic view count and record view."""
        # Check if user has already viewed this topic recently (within 1 hour)
        if user_id:
            recent_view_query = (
                select(ForumTopicView)
                .where(
                    and_(
                        ForumTopicView.topic_id == topic_id,
                        ForumTopicView.user_id == user_id,
                        ForumTopicView.created_at > datetime.utcnow() - timedelta(hours=1)
                    )
                )
            )
            result = await db.execute(recent_view_query)
            if result.scalar_one_or_none():
                return  # Don't count multiple views within an hour
        
        # Record the view
        view_record = ForumTopicView(
            topic_id=topic_id,
            user_id=user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(view_record)
        
        # Increment topic view count
        topic = await self.get(db, topic_id)
        if topic:
            topic.views_count += 1
            await db.commit()
    
    async def update_activity(
        self,
        db: AsyncSession,
        topic_id: UUID,
        last_post_id: Optional[UUID] = None,
        last_post_author_id: Optional[UUID] = None
    ) -> None:
        """Update topic activity information."""
        topic = await self.get(db, topic_id)
        if topic:
            topic.last_activity_at = datetime.utcnow()
            if last_post_id:
                topic.last_post_id = last_post_id
            if last_post_author_id:
                topic.last_post_author_id = last_post_author_id
            await db.commit()


class CRUDForumPost(CRUDBase[ForumPost, ForumPostCreate, ForumPostUpdate]):
    """CRUD operations for forum posts."""
    
    async def create_with_user(
        self,
        db: AsyncSession,
        *,
        obj_in: ForumPostCreate,
        author_id: UUID,
        organization_id: UUID
    ) -> ForumPost:
        """Create a new post with author and organization."""
        obj_data = obj_in.model_dump()
        obj_data.update({
            "author_id": author_id,
            "organization_id": organization_id
        })
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update topic activity and post count
        topic_crud = CRUDForumTopic(ForumTopic)
        topic = await topic_crud.get(db, obj_in.topic_id)
        if topic:
            topic.posts_count += 1
            await topic_crud.update_activity(
                db, 
                obj_in.topic_id, 
                last_post_id=db_obj.id,
                last_post_author_id=author_id
            )
            
            # Update category post count
            category_crud = CRUDForumCategory(ForumCategory)
            await category_crud.update_counts(db, topic.category_id, posts_delta=1)
        
        # Update parent post reply count if this is a reply
        if obj_in.parent_post_id:
            parent_post = await self.get(db, obj_in.parent_post_id)
            if parent_post:
                parent_post.replies_count += 1
                await db.commit()
        
        return db_obj
    
    async def get_topic_posts(
        self,
        db: AsyncSession,
        topic_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[ForumPost]:
        """Get posts for a topic with author information."""
        query = (
            select(self.model)
            .options(selectinload(self.model.author))
            .where(
                and_(
                    self.model.topic_id == topic_id,
                    self.model.organization_id == organization_id,
                    self.model.is_deleted == False
                )
            )
            .order_by(self.model.created_at)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_replies(
        self,
        db: AsyncSession,
        post_id: UUID,
        organization_id: UUID
    ) -> Optional[ForumPost]:
        """Get post with its replies."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.author),
                selectinload(self.model.replies).selectinload(ForumPost.author)
            )
            .where(
                and_(
                    self.model.id == post_id,
                    self.model.organization_id == organization_id,
                    self.model.is_deleted == False
                )
            )
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def soft_delete(
        self,
        db: AsyncSession,
        post_id: UUID,
        organization_id: UUID
    ) -> bool:
        """Soft delete a post."""
        post = await db.execute(
            select(self.model).where(
                and_(
                    self.model.id == post_id,
                    self.model.organization_id == organization_id
                )
            )
        )
        post = post.scalar_one_or_none()
        
        if not post:
            return False
            
        post.is_deleted = True
        await db.commit()
        
        # Update topic post count
        topic_crud = CRUDForumTopic(ForumTopic)
        topic = await topic_crud.get(db, post.topic_id)
        if topic:
            topic.posts_count = max(0, topic.posts_count - 1)
            await db.commit()
        
        return True


class CRUDForumLike(CRUDBase[ForumTopicLike, None, None]):
    """CRUD operations for forum likes."""
    
    async def toggle_topic_like(
        self,
        db: AsyncSession,
        topic_id: UUID,
        user_id: UUID,
        organization_id: UUID
    ) -> tuple[bool, int]:
        """Toggle like on a topic. Returns (liked_status, new_like_count)."""
        
        # Check if already liked
        existing_like = await db.execute(
            select(ForumTopicLike).where(
                and_(
                    ForumTopicLike.topic_id == topic_id,
                    ForumTopicLike.user_id == user_id
                )
            )
        )
        existing_like = existing_like.scalar_one_or_none()
        
        topic_crud = CRUDForumTopic(ForumTopic)
        topic = await topic_crud.get(db, topic_id)
        
        if existing_like:
            # Unlike
            await db.delete(existing_like)
            if topic:
                topic.likes_count = max(0, topic.likes_count - 1)
            liked = False
        else:
            # Like
            new_like = ForumTopicLike(
                topic_id=topic_id,
                user_id=user_id,
                organization_id=organization_id
            )
            db.add(new_like)
            if topic:
                topic.likes_count += 1
            liked = True
        
        await db.commit()
        
        return liked, topic.likes_count if topic else 0
    
    async def toggle_post_like(
        self,
        db: AsyncSession,
        post_id: UUID,
        user_id: UUID,
        organization_id: UUID
    ) -> tuple[bool, int]:
        """Toggle like on a post. Returns (liked_status, new_like_count)."""
        
        # Check if already liked
        existing_like = await db.execute(
            select(ForumPostLike).where(
                and_(
                    ForumPostLike.post_id == post_id,
                    ForumPostLike.user_id == user_id
                )
            )
        )
        existing_like = existing_like.scalar_one_or_none()
        
        post_crud = CRUDForumPost(ForumPost)
        post = await post_crud.get(db, post_id)
        
        if existing_like:
            # Unlike
            await db.delete(existing_like)
            if post:
                post.likes_count = max(0, post.likes_count - 1)
            liked = False
        else:
            # Like
            new_like = ForumPostLike(
                post_id=post_id,
                user_id=user_id,
                organization_id=organization_id
            )
            db.add(new_like)
            if post:
                post.likes_count += 1
            liked = True
        
        await db.commit()
        
        return liked, post.likes_count if post else 0


# Create instances of CRUD classes
forum_category = CRUDForumCategory(ForumCategory)
forum_topic = CRUDForumTopic(ForumTopic)
forum_post = CRUDForumPost(ForumPost)
forum_like = CRUDForumLike(ForumTopicLike)