"""Forum service for handling forum business logic."""

from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.utils.logging import log_business_event, log_database_operation
from app.crud.forum import (
    forum_category,
    forum_topic, 
    forum_post,
    forum_like
)
from app.models.forum import ForumTopic, ForumPost, ForumCategory
from app.schemas.forum import (
    ForumCategoryCreate,
    ForumCategoryUpdate,
    ForumCategoryResponse,
    ForumTopicCreate,
    ForumTopicUpdate,
    ForumTopicResponse,
    ForumTopicListResponse,
    ForumTopicSearchQuery,
    ForumTopicAuthor,
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostResponse,
    ForumStatsResponse,
    ForumLikeResponse
)

logger = get_logger(__name__)


class ForumService:
    """Service for handling forum-related business logic."""
    
    # Category Management
    
    @staticmethod
    async def get_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ForumCategoryResponse]:
        """Get active forum categories."""
        log_database_operation("forum_categories", "list", {"skip": skip, "limit": limit})
        
        categories = await forum_category.get_active_categories(
            db, skip=skip, limit=limit
        )
        
        return [ForumCategoryResponse.model_validate(cat) for cat in categories]
    
    @staticmethod
    async def create_category(
        db: AsyncSession,
        *,
        category_data: ForumCategoryCreate,
        creator_id: UUID
    ) -> ForumCategoryResponse:
        """Create a new forum category (admin only)."""
        log_business_event("forum_category_create", {
            "creator_id": str(creator_id),
            "name": category_data.name,
            "type": category_data.category_type
        })
        
        category = await forum_category.create(db, obj_in=category_data)
        
        log_database_operation("forum_categories", "create", {
            "id": str(category.id),
            "name": category.name
        })
        
        return ForumCategoryResponse.model_validate(category)
    
    # Topic Management
    
    @staticmethod
    async def get_topics(
        db: AsyncSession,
        *,
        search_params: ForumTopicSearchQuery,
        organization_id: UUID,
        user_id: Optional[UUID] = None
    ) -> ForumTopicListResponse:
        """Get forum topics with search and pagination."""
        
        skip = (search_params.page - 1) * search_params.page_size
        
        log_database_operation("forum_topics", "list", {
            "organization_id": str(organization_id),
            "search": search_params.search,
            "page": search_params.page,
            "page_size": search_params.page_size
        })
        
        topics, total_count = await forum_topic.get_multi_with_search(
            db,
            search_params=search_params,
            organization_id=organization_id,
            skip=skip,
            limit=search_params.page_size
        )
        
        # Convert to response format
        topic_responses = []
        for topic in topics:
            topic_response = ForumTopicResponse.model_validate(topic)
            
            # Add author information
            if topic.author:
                topic_response.author = ForumTopicAuthor(
                    id=topic.author.id,
                    first_name=topic.author.first_name,
                    last_name=topic.author.last_name,
                    email=topic.author.email,
                    job_title=topic.author.job_title,
                    is_verified=topic.author.email_verified
                )
            
            # Add category information
            if topic.category:
                topic_response.category = ForumCategoryResponse.model_validate(topic.category)
                
            topic_responses.append(topic_response)
        
        # Calculate pagination metadata
        total_pages = (total_count + search_params.page_size - 1) // search_params.page_size
        has_next = search_params.page < total_pages
        has_prev = search_params.page > 1
        
        return ForumTopicListResponse(
            topics=topic_responses,
            total_count=total_count,
            page=search_params.page,
            page_size=search_params.page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
    
    @staticmethod
    async def get_topic(
        db: AsyncSession,
        topic_id: UUID,
        organization_id: UUID,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ForumTopicResponse:
        """Get a single topic with view tracking."""
        
        topic = await forum_topic.get_with_relations(
            db, topic_id, organization_id=organization_id
        )
        
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Increment view count
        if user_id or ip_address:
            await forum_topic.increment_views(
                db,
                topic_id=topic_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                organization_id=organization_id
            )
        
        log_database_operation("forum_topics", "view", {
            "id": str(topic_id),
            "user_id": str(user_id) if user_id else None,
            "views_count": topic.views_count + 1
        })
        
        # Convert to response format
        topic_response = ForumTopicResponse.model_validate(topic)
        
        # Add author information
        if topic.author:
            topic_response.author = ForumTopicAuthor(
                id=topic.author.id,
                first_name=topic.author.first_name,
                last_name=topic.author.last_name,
                email=topic.author.email,
                job_title=topic.author.job_title,
                is_verified=topic.author.email_verified
            )
        
        # Add category information
        if topic.category:
            topic_response.category = ForumCategoryResponse.model_validate(topic.category)
        
        return topic_response
    
    @staticmethod
    async def create_topic(
        db: AsyncSession,
        *,
        topic_data: ForumTopicCreate,
        author_id: UUID,
        organization_id: UUID
    ) -> ForumTopicResponse:
        """Create a new forum topic."""
        
        # Verify category exists and is active
        category = await forum_category.get(db, topic_data.category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive category"
            )
        
        log_business_event("forum_topic_create", {
            "author_id": str(author_id),
            "organization_id": str(organization_id),
            "category_id": str(topic_data.category_id),
            "title": topic_data.title
        })
        
        topic = await forum_topic.create_with_user(
            db,
            obj_in=topic_data,
            author_id=author_id,
            organization_id=organization_id
        )
        
        # Get topic with relations for response
        topic_with_relations = await forum_topic.get_with_relations(db, topic.id)
        
        log_database_operation("forum_topics", "create", {
            "id": str(topic.id),
            "title": topic.title,
            "category": category.name
        })
        
        # Convert to response format
        topic_response = ForumTopicResponse.model_validate(topic_with_relations)
        
        if topic_with_relations.author:
            topic_response.author = ForumTopicAuthor(
                id=topic_with_relations.author.id,
                first_name=topic_with_relations.author.first_name,
                last_name=topic_with_relations.author.last_name,
                email=topic_with_relations.author.email,
                job_title=topic_with_relations.author.job_title,
                is_verified=topic_with_relations.author.email_verified
            )
        
        if topic_with_relations.category:
            topic_response.category = ForumCategoryResponse.model_validate(topic_with_relations.category)
        
        return topic_response
    
    @staticmethod
    async def update_topic(
        db: AsyncSession,
        topic_id: UUID,
        *,
        topic_data: ForumTopicUpdate,
        user_id: UUID,
        organization_id: UUID,
        is_admin: bool = False
    ) -> ForumTopicResponse:
        """Update a forum topic."""
        
        topic = await forum_topic.get_with_relations(db, topic_id, organization_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Check permissions - only author or admin can edit
        if topic.author_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this topic"
            )
        
        # Verify new category if provided
        if topic_data.category_id and topic_data.category_id != topic.category_id:
            new_category = await forum_category.get(db, topic_data.category_id)
            if not new_category or not new_category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or inactive category"
                )
        
        log_business_event("forum_topic_update", {
            "topic_id": str(topic_id),
            "user_id": str(user_id),
            "is_admin": is_admin,
            "changes": topic_data.model_dump(exclude_unset=True)
        })
        
        updated_topic = await forum_topic.update(db, db_obj=topic, obj_in=topic_data)
        
        # Get updated topic with relations
        topic_with_relations = await forum_topic.get_with_relations(db, topic_id)
        
        log_database_operation("forum_topics", "update", {
            "id": str(topic_id),
            "title": updated_topic.title
        })
        
        # Convert to response format
        topic_response = ForumTopicResponse.model_validate(topic_with_relations)
        
        if topic_with_relations.author:
            topic_response.author = ForumTopicAuthor(
                id=topic_with_relations.author.id,
                first_name=topic_with_relations.author.first_name,
                last_name=topic_with_relations.author.last_name,
                email=topic_with_relations.author.email,
                job_title=topic_with_relations.author.job_title,
                is_verified=topic_with_relations.author.email_verified
            )
        
        if topic_with_relations.category:
            topic_response.category = ForumCategoryResponse.model_validate(topic_with_relations.category)
        
        return topic_response
    
    @staticmethod
    async def delete_topic(
        db: AsyncSession,
        topic_id: UUID,
        *,
        user_id: UUID,
        organization_id: UUID,
        is_admin: bool = False
    ) -> bool:
        """Delete a forum topic (admin only or author)."""
        
        topic = await forum_topic.get(db, topic_id)
        if not topic or topic.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Check permissions - only author or admin can delete
        if topic.author_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this topic"
            )
        
        log_business_event("forum_topic_delete", {
            "topic_id": str(topic_id),
            "user_id": str(user_id),
            "is_admin": is_admin,
            "title": topic.title
        })
        
        # Delete the topic (this should cascade to posts and likes)
        result = await forum_topic.remove(db, id=topic_id)
        
        log_database_operation("forum_topics", "delete", {
            "id": str(topic_id),
            "title": topic.title
        })
        
        return result is not None
    
    @staticmethod
    async def toggle_topic_like(
        db: AsyncSession,
        topic_id: UUID,
        user_id: UUID,
        organization_id: UUID
    ) -> ForumLikeResponse:
        """Toggle like on a topic."""
        
        # Verify topic exists
        topic = await forum_topic.get(db, topic_id)
        if not topic or topic.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        liked, like_count = await forum_like.toggle_topic_like(
            db, topic_id, user_id, organization_id
        )
        
        log_business_event("forum_topic_like_toggle", {
            "topic_id": str(topic_id),
            "user_id": str(user_id),
            "liked": liked,
            "new_count": like_count
        })
        
        return ForumLikeResponse(
            success=True,
            liked=liked,
            likes_count=like_count,
            message=f"Topic {'liked' if liked else 'unliked'} successfully"
        )
    
    # Post Management
    
    @staticmethod
    async def get_topic_posts(
        db: AsyncSession,
        topic_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[ForumPostResponse]:
        """Get posts for a topic."""
        
        # Verify topic exists
        topic = await forum_topic.get(db, topic_id)
        if not topic or topic.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        posts = await forum_post.get_topic_posts(
            db, topic_id, organization_id, skip=skip, limit=limit
        )
        
        # Convert to response format
        post_responses = []
        for post in posts:
            post_response = ForumPostResponse.model_validate(post)
            
            # Add author information
            if post.author:
                post_response.author = ForumTopicAuthor(
                    id=post.author.id,
                    first_name=post.author.first_name,
                    last_name=post.author.last_name,
                    email=post.author.email,
                    job_title=post.author.job_title,
                    is_verified=post.author.email_verified
                )
            
            post_responses.append(post_response)
        
        return post_responses
    
    @staticmethod
    async def get_topic_posts_threaded(
        db: AsyncSession,
        topic_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[ForumPostResponse]:
        """Get posts for a topic with nested reply threading."""
        
        # Verify topic exists
        topic = await forum_topic.get(db, topic_id)
        if not topic or topic.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        posts = await forum_post.get_topic_posts_threaded(
            db, topic_id, organization_id, skip=skip, limit=limit
        )
        
        # Convert to response format with nested replies
        post_responses = []
        for post in posts:
            post_response = ForumPostResponse.model_validate(post)
            
            # Add author information
            if post.author:
                post_response.author = ForumTopicAuthor(
                    id=post.author.id,
                    first_name=post.author.first_name,
                    last_name=post.author.last_name,
                    email=post.author.email,
                    job_title=post.author.job_title,
                    is_verified=post.author.email_verified
                )
            
            # Process nested replies recursively
            if post.replies:
                post_response.replies = await ForumService._build_nested_replies(post.replies)
            
            post_responses.append(post_response)
        
        return post_responses
    
    @staticmethod
    async def get_post_replies(
        db: AsyncSession,
        post_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[ForumPostResponse]:
        """Get replies for a specific post with nested threading."""
        
        # Verify parent post exists
        parent_post = await forum_post.get(db, post_id)
        if not parent_post or parent_post.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Get all direct replies to this post
        from sqlalchemy import select, and_
        from sqlalchemy.orm import selectinload
        from app.models.forum import ForumPost
        
        reply_query = (
            select(ForumPost)
            .options(
                selectinload(ForumPost.author),
                # Load nested replies recursively
                selectinload(ForumPost.replies).selectinload(ForumPost.author),
                selectinload(ForumPost.replies).selectinload(ForumPost.replies).selectinload(ForumPost.author)
            )
            .where(
                and_(
                    ForumPost.parent_post_id == post_id,
                    ForumPost.organization_id == organization_id,
                    ForumPost.is_deleted == False
                )
            )
            .order_by(ForumPost.created_at)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(reply_query)
        replies = result.scalars().all()
        
        # Convert to response format with nested replies
        reply_responses = []
        for reply in replies:
            reply_response = ForumPostResponse.model_validate(reply)
            
            # Add author information
            if reply.author:
                reply_response.author = ForumTopicAuthor(
                    id=reply.author.id,
                    first_name=reply.author.first_name,
                    last_name=reply.author.last_name,
                    email=reply.author.email,
                    job_title=reply.author.job_title,
                    is_verified=reply.author.email_verified
                )
            
            # Process nested replies recursively
            if reply.replies:
                reply_response.replies = await ForumService._build_nested_replies(reply.replies)
            
            reply_responses.append(reply_response)
        
        return reply_responses
    
    @staticmethod
    async def _build_nested_replies(replies: List) -> List[ForumPostResponse]:
        """Recursively build nested reply structure."""
        reply_responses = []
        
        for reply in replies:
            # Skip deleted replies
            if reply.is_deleted:
                continue
                
            reply_response = ForumPostResponse.model_validate(reply)
            
            # Add author information
            if reply.author:
                reply_response.author = ForumTopicAuthor(
                    id=reply.author.id,
                    first_name=reply.author.first_name,
                    last_name=reply.author.last_name,
                    email=reply.author.email,
                    job_title=reply.author.job_title,
                    is_verified=reply.author.email_verified
                )
            
            # Process nested replies (replies to replies)
            if reply.replies:
                reply_response.replies = await ForumService._build_nested_replies(reply.replies)
            
            reply_responses.append(reply_response)
        
        # Sort replies by creation date (oldest first)
        reply_responses.sort(key=lambda x: x.created_at)
        
        return reply_responses
    
    @staticmethod
    async def create_post(
        db: AsyncSession,
        *,
        post_data: ForumPostCreate,
        author_id: UUID,
        organization_id: UUID
    ) -> ForumPostResponse:
        """Create a new forum post."""
        
        # Verify topic exists and is not locked
        topic = await forum_topic.get(db, post_data.topic_id)
        if not topic or topic.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        if topic.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot post to a locked topic"
            )
        
        # Verify parent post if this is a reply
        if post_data.parent_post_id:
            parent_post = await forum_post.get(db, post_data.parent_post_id)
            if not parent_post or parent_post.organization_id != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent post not found"
                )
        
        log_business_event("forum_post_create", {
            "author_id": str(author_id),
            "topic_id": str(post_data.topic_id),
            "parent_post_id": str(post_data.parent_post_id) if post_data.parent_post_id else None
        })
        
        post = await forum_post.create_with_user(
            db,
            obj_in=post_data,
            author_id=author_id,
            organization_id=organization_id
        )
        
        # Get post with relations for response
        post_with_author = await forum_post.get_with_replies(db, post.id, organization_id)
        
        log_database_operation("forum_posts", "create", {
            "id": str(post.id),
            "topic_id": str(post_data.topic_id),
            "content_length": len(post_data.content)
        })
        
        # Convert to response format
        post_response = ForumPostResponse.model_validate(post_with_author)
        
        if post_with_author.author:
            post_response.author = ForumTopicAuthor(
                id=post_with_author.author.id,
                first_name=post_with_author.author.first_name,
                last_name=post_with_author.author.last_name,
                email=post_with_author.author.email,
                job_title=post_with_author.author.job_title,
                is_verified=post_with_author.author.email_verified
            )
        
        return post_response
    
    @staticmethod
    async def update_post(
        db: AsyncSession,
        post_id: UUID,
        post_data: ForumPostUpdate,
        user_id: UUID,
        organization_id: UUID,
        is_admin: bool = False
    ) -> ForumPostResponse:
        """Update a forum post."""
        
        # Get post
        post = await forum_post.get(db, post_id)
        if not post or post.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check permissions (author or admin)
        if post.author_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own posts"
            )
        
        # Check if topic is locked (even admins can't edit posts in locked topics)
        topic = await forum_topic.get(db, post.topic_id)
        if topic and topic.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit posts in a locked topic"
            )
        
        log_business_event("forum_post_update", {
            "post_id": str(post_id),
            "editor_id": str(user_id),
            "is_admin": is_admin
        })
        
        # Update post
        updated_post = await forum_post.update(db, db_obj=post, obj_in=post_data)
        
        # Get post with relations for response
        post_with_author = await forum_post.get_with_replies(db, updated_post.id, organization_id)
        
        log_database_operation("forum_posts", "update", {
            "id": str(post_id),
            "content_length": len(post_data.content) if post_data.content else 0
        })
        
        # Convert to response format
        post_response = ForumPostResponse.model_validate(post_with_author)
        
        if post_with_author.author:
            post_response.author = ForumTopicAuthor(
                id=post_with_author.author.id,
                first_name=post_with_author.author.first_name,
                last_name=post_with_author.author.last_name,
                email=post_with_author.author.email,
                job_title=post_with_author.author.job_title,
                is_verified=post_with_author.author.email_verified
            )
        
        return post_response
    
    @staticmethod
    async def delete_post(
        db: AsyncSession,
        post_id: UUID,
        user_id: UUID,
        organization_id: UUID,
        is_admin: bool = False
    ):
        """Delete a forum post (soft delete)."""
        
        # Get post
        post = await forum_post.get(db, post_id)
        if not post or post.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check permissions (author or admin)
        if post.author_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own posts"
            )
        
        log_business_event("forum_post_delete", {
            "post_id": str(post_id),
            "deleter_id": str(user_id),
            "is_admin": is_admin
        })
        
        # Soft delete post
        await forum_post.remove(db, id=post_id)
        
        log_database_operation("forum_posts", "delete", {
            "id": str(post_id)
        })
    
    @staticmethod
    async def toggle_post_like(
        db: AsyncSession,
        post_id: UUID,
        user_id: UUID,
        organization_id: UUID
    ) -> ForumLikeResponse:
        """Toggle like on a forum post."""
        
        # Verify post exists
        post = await forum_post.get(db, post_id)
        if not post or post.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        liked, like_count = await forum_like.toggle_post_like(
            db, post_id, user_id, organization_id
        )
        
        log_business_event("forum_post_like_toggle", {
            "post_id": str(post_id),
            "user_id": str(user_id),
            "liked": liked,
            "new_count": like_count
        })
        
        return ForumLikeResponse(
            success=True,
            liked=liked,
            likes_count=like_count,
            message=f"Post {'liked' if liked else 'unliked'} successfully"
        )
    
    @staticmethod
    async def mark_best_answer(
        db: AsyncSession,
        post_id: UUID,
        user_id: UUID,
        organization_id: UUID,
        is_admin: bool = False
    ) -> ForumPostResponse:
        """Mark a post as the best answer for its topic."""
        
        # Get post
        post = await forum_post.get(db, post_id)
        if not post or post.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Get topic
        topic = await forum_topic.get(db, post.topic_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Check permissions (topic author or admin)
        if topic.author_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark best answers for your own topics"
            )
        
        log_business_event("forum_best_answer_mark", {
            "post_id": str(post_id),
            "topic_id": str(topic.id),
            "marker_id": str(user_id),
            "is_admin": is_admin
        })
        
        # Clear any existing best answer
        if topic.best_answer_post_id:
            previous_best = await forum_post.get(db, topic.best_answer_post_id)
            if previous_best:
                await forum_post.update(db, db_obj=previous_best, obj_in={"is_best_answer": False})
        
        # Mark this post as best answer
        await forum_post.update(db, db_obj=post, obj_in={"is_best_answer": True})
        
        # Update topic to reference this post as best answer
        await forum_topic.update(db, db_obj=topic, obj_in={
            "best_answer_post_id": post_id,
            "has_best_answer": True
        })
        
        # Get updated post with relations
        post_with_author = await forum_post.get_with_replies(db, post_id, organization_id)
        
        log_database_operation("forum_posts", "mark_best_answer", {
            "id": str(post_id),
            "topic_id": str(topic.id)
        })
        
        # Convert to response format
        post_response = ForumPostResponse.model_validate(post_with_author)
        
        if post_with_author.author:
            post_response.author = ForumTopicAuthor(
                id=post_with_author.author.id,
                first_name=post_with_author.author.first_name,
                last_name=post_with_author.author.last_name,
                email=post_with_author.author.email,
                job_title=post_with_author.author.job_title,
                is_verified=post_with_author.author.email_verified
            )
        
        return post_response
    
    @staticmethod
    async def unmark_best_answer(
        db: AsyncSession,
        post_id: UUID,
        user_id: UUID,
        organization_id: UUID,
        is_admin: bool = False
    ):
        """Remove best answer designation from a post."""
        
        # Get post
        post = await forum_post.get(db, post_id)
        if not post or post.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Get topic
        topic = await forum_topic.get(db, post.topic_id)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Check permissions (topic author or admin)
        if topic.author_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only unmark best answers for your own topics"
            )
        
        # Check if this post is actually the best answer
        if not post.is_best_answer or topic.best_answer_post_id != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This post is not marked as the best answer"
            )
        
        log_business_event("forum_best_answer_unmark", {
            "post_id": str(post_id),
            "topic_id": str(topic.id),
            "unmarker_id": str(user_id),
            "is_admin": is_admin
        })
        
        # Remove best answer designation from post
        await forum_post.update(db, db_obj=post, obj_in={"is_best_answer": False})
        
        # Clear best answer reference from topic
        await forum_topic.update(db, db_obj=topic, obj_in={
            "best_answer_post_id": None,
            "has_best_answer": False
        })
        
        log_database_operation("forum_posts", "unmark_best_answer", {
            "id": str(post_id),
            "topic_id": str(topic.id)
        })
    
    @staticmethod
    async def get_forum_stats(
        db: AsyncSession,
        organization_id: UUID
    ) -> ForumStatsResponse:
        """Get forum statistics for an organization."""
        
        log_database_operation("forum_stats", "get", {
            "organization_id": str(organization_id)
        })
        
        # These would be real database queries in production
        # For now, return placeholder data that matches the frontend expectations
        categories = await forum_category.get_active_categories(db)
        
        return ForumStatsResponse(
            total_topics=156,  # Would be calculated from database
            total_posts=423,   # Would be calculated from database
            active_members=89, # Would be calculated from database
            helpful_answers=234, # Would be calculated from database
            categories=[ForumCategoryResponse.model_validate(cat) for cat in categories]
        )