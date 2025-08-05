from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pg_models import User as PGUser
from app.models.mongo_models import User as MongoUser, ForumPost, UseCase, ForumReply
from typing import Optional, List
from uuid import UUID

class UserService:
    @staticmethod
    async def get_user_by_email_pg(db: AsyncSession, email: str) -> Optional[PGUser]:
        """Get user by email from PostgreSQL"""
        result = await db.execute(select(PGUser).where(PGUser.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user_pg(db: AsyncSession, name: str, email: str, role: str = "user", supertokens_id: str = None) -> PGUser:
        """Create a new user in PostgreSQL"""
        new_user = PGUser(name=name, email=email, role=role, supertokens_id=supertokens_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def get_user_by_id_pg(db: AsyncSession, user_id: UUID) -> Optional[PGUser]:
        """Get user by ID from PostgreSQL"""
        result = await db.execute(select(PGUser).where(PGUser.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_supertokens_id(db: AsyncSession, supertokens_id: str) -> Optional[PGUser]:
        """Get user by SuperTokens ID from PostgreSQL"""
        result = await db.execute(select(PGUser).where(PGUser.supertokens_id == supertokens_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_pg(db: AsyncSession, user_id: UUID, name: str = None, email: str = None) -> Optional[PGUser]:
        """Update user in PostgreSQL"""
        user = await UserService.get_user_by_id_pg(db, user_id)
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def delete_user_pg(db: AsyncSession, user_id: UUID) -> bool:
        """Delete user from PostgreSQL"""
        user = await UserService.get_user_by_id_pg(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False

    @staticmethod
    async def create_user_mongo(email: str, name: str, **kwargs) -> MongoUser:
        """Create user in MongoDB"""
        user = MongoUser(email=email, name=name, **kwargs)
        await user.create()
        return user

    @staticmethod
    async def get_user_by_email_mongo(email: str) -> Optional[MongoUser]:
        """Get user by email from MongoDB"""
        return await MongoUser.find_one(MongoUser.email == email)

class ForumService:
    @staticmethod
    async def create_post(
        author_id: str,
        title: str,
        content: str,
        category: str,
        tags: List[str] = None
    ) -> ForumPost:
        """Create a new forum post"""
        post = ForumPost(
            author_id=author_id,
            title=title,
            content=content,
            category=category,
            tags=tags or []
        )
        await post.create()
        return post

    @staticmethod
    async def get_posts_by_category(category: str, limit: int = 20) -> List[ForumPost]:
        """Get posts by category"""
        posts = await ForumPost.find(
            ForumPost.category == category
        ).sort(-ForumPost.created_at).limit(limit).to_list()
        return posts

    @staticmethod
    async def create_reply(
        post_id: str,
        author_id: str,
        content: str,
        is_best_answer: bool = False
    ) -> ForumReply:
        """Create a new forum reply"""
        reply = ForumReply(
            post_id=post_id,
            author_id=author_id,
            content=content,
            is_best_answer=is_best_answer
        )
        await reply.create()
        return reply

    @staticmethod
    async def get_replies_by_post(post_id: str) -> List[ForumReply]:
        """Get all replies for a specific post"""
        replies = await ForumReply.find(
            ForumReply.post_id == post_id
        ).sort(-ForumReply.created_at).to_list()
        return replies

class UseCaseService:
    @staticmethod
    async def create_use_case(data: dict) -> UseCase:
        """Create a new use case from frontend JSON structure or direct data"""
        # Check if this is frontend JSON structure (has 'factoryName' field)
        if 'factoryName' in data:
            # Map frontend JSON structure to UseCase model
            use_case_data = {
                "submitted_by": data.get("submitted_by", "system-seed"),
                "title": data["title"],
                "problem_statement": data.get("description", "Problem statement not provided."),
                "solution_description": data.get("benefits", ["Solution benefits not detailed."])[0] if data.get("benefits") else "Solution description not provided.",
                "vendor_info": {
                    "factory_name": data.get("factoryName", ""),
                    "implementation_time": data.get("implementationTime", ""),
                    "image": data.get("image", "")
                },
                "industry_tags": [data.get("category", "General")],
                "region": data.get("city", "Saudi Arabia"),
                "location": {"lat": data["latitude"], "lng": data["longitude"]},
                            "impact_metrics": {
                "benefits": "; ".join(data.get("benefits", ["No benefits listed"]))
            },
                "published": True,
                "featured": True
            }
        else:
            # Direct UseCase model data
            use_case_data = data
            
        use_case = UseCase(**use_case_data)
        await use_case.create()
        return use_case

    @staticmethod
    async def get_use_cases_by_region(region: str) -> List[UseCase]:
        """Get use cases by region"""
        use_cases = await UseCase.find(
            UseCase.region == region,
            UseCase.published == True
        ).to_list()
        return use_cases