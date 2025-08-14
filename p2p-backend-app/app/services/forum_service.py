from datetime import datetime
from typing import Dict

from bson import ObjectId
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.mongo_models import ForumPost, ForumReply, User as MongoUser
from app.services.database_service import UserService
from app.services.user_activity_service import UserActivityService


class ForumService:
    @staticmethod
    async def create_reply(
        user_supertokens_id: str,
        post_id: str,
        content: str,
        parent_reply_id: str | None,
        db: AsyncSession,
    ) -> ForumReply:
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise ValueError("User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise ValueError("User profile not found")

        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        if not post:
            raise ValueError("Post not found")

        reply = ForumReply(
            post_id=post_id,
            author_id=str(mongo_user.id),
            content=content,
            parent_reply_id=parent_reply_id,
            upvotes=0,
            is_best_answer=False,
        )
        await reply.insert()

        # increment reply count on parent
        post.reply_count += 1
        await post.save()

        # Log activity (dashboard feed + stats)
        await UserActivityService.log_activity(
            user_id=str(mongo_user.id),
            activity_type="comment",
            target_id=str(post.id),
            target_title=post.title,
            target_category=post.category,
            description=f"Replied: {post.title}",
        )

        return reply

    @staticmethod
    async def toggle_like(
        user_supertokens_id: str,
        document_id: str,
        doc_type: str,
        db: AsyncSession,
    ) -> Dict[str, object]:
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise ValueError("User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise ValueError("User profile not found")

        Model = ForumPost if doc_type == "post" else ForumReply
        try:
            document = await Model.find_one(Model.id == ObjectId(document_id))
        except Exception:
            document = None
        if not document:
            raise ValueError(f"{doc_type.capitalize()} not found")

        user_id_str = str(mongo_user.id)
        if user_id_str in document.liked_by:
            # unlike
            document.liked_by.remove(user_id_str)
            document.upvotes = max(0, document.upvotes - 1)
            await document.save()
            return {"liked": False, "likes": document.upvotes}
        else:
            document.liked_by.append(user_id_str)
            document.upvotes += 1
            await document.save()
            return {"liked": True, "likes": document.upvotes}

    @staticmethod
    async def update_post(
        user_supertokens_id: str,
        post_id: str,
        update_data: dict,
        db: AsyncSession,
    ) -> ForumPost:
        """Update a forum post with authorization check"""
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # AUTHORIZATION CHECK - only author can edit their post
        if post.author_id != str(mongo_user.id):
            raise HTTPException(status_code=403, detail="User not authorized to edit this post")

        # Update the post with edited timestamp
        update_query = {"$set": {**update_data, "edited_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        await post.update(update_query)
        
        # Return the updated post
        return await ForumPost.find_one(ForumPost.id == ObjectId(post_id))

    @staticmethod
    async def delete_post(
        user_supertokens_id: str,
        post_id: str,
        db: AsyncSession,
    ) -> dict:
        """Soft delete a forum post with authorization check"""
        pg_user = await UserService.get_user_by_supertokens_id(db, user_supertokens_id)
        if not pg_user:
            raise HTTPException(status_code=404, detail="User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        try:
            post = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
        except Exception:
            post = None
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # AUTHORIZATION CHECK - only author can delete their post
        if post.author_id != str(mongo_user.id):
            raise HTTPException(status_code=403, detail="User not authorized to delete this post")

        # SOFT DELETE: Update status instead of permanently deleting
        await post.update({"$set": {"status": "deleted", "updated_at": datetime.utcnow()}})
        
        # Update user stats to reflect the deletion
        await UserActivityService.recalculate_user_stats(str(mongo_user.id))
        
        return {"status": "deleted"}


