from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pg_models import User as PGUser
from app.models.mongo_models import User as MongoUser, ForumPost, UseCase, ForumReply, Organization
from typing import Optional, List, Dict
from uuid import UUID
import re

class UserService:
    @staticmethod
    async def create_user_with_profile(db: AsyncSession, supertokens_id: str, email: str, profile_data: Dict) -> PGUser:
        """
        Creates a new user in both PostgreSQL and MongoDB after SuperTokens sign-up.
        This is the primary function for creating a complete user record.
        
        Args:
            db: The async SQLAlchemy session.
            supertokens_id: The user ID from SuperTokens.
            email: The user's email.
            profile_data: A dictionary containing all profile and organization info.
            
        Returns:
            The created PostgreSQL user object.
        """
        # --- 1. Create Core User in PostgreSQL ---
        pg_user = PGUser(
            supertokens_id=supertokens_id,
            email=email,
            name=profile_data.get("name"),
            role=profile_data.get("role", "user")
        )
        db.add(pg_user)
        await db.commit()
        await db.refresh(pg_user)
        
        # --- 2. Create Extended Profile in MongoDB ---
        # Create or link Organization by domain inferred from email
        organization_id = None
        try:
            domain = email.split("@")[1]
            org_name = domain.split(".")[0].replace("-", " ").title()
            existing_org = await Organization.find_one(Organization.domain == domain)
            if existing_org:
                organization_id = str(existing_org.id)
            else:
                new_org = Organization(
                    name=org_name,
                    domain=domain,
                    industry_sector=profile_data.get("industry_sector"),
                    size=profile_data.get("company_size"),
                    country="Saudi Arabia",
                    city=profile_data.get("location"),
                    is_active=True,
                )
                await new_org.insert()
                organization_id = str(new_org.id)
        except Exception:
            organization_id = None

        mongo_user = MongoUser(
            email=email,
            name=profile_data.get("name"),
            organization_id=organization_id,
            company=profile_data.get("company"),
            industry_sector=profile_data.get("industry_sector"),
            title=profile_data.get("title"),
            # The mongo_models.py file expects company_size, but your prompt mentioned it.
            # I'll add it here assuming you will add it to the MongoUser model.
            # company_size=profile_data.get("company_size"), 
            location=profile_data.get("location"),
            role=profile_data.get("role", "user")
        )
        await mongo_user.create()
        
        return pg_user

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
        parent_reply_id: str = None,
        is_best_answer: bool = False
    ) -> ForumReply:
        """Create a new forum reply."""
        reply = ForumReply(
            post_id=post_id,
            author_id=author_id,
            content=content,
            parent_reply_id=parent_reply_id,
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

def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\(\)]", "", text)
    text = re.sub(r"[\s\W_]+", "-", text)
    text = text.strip("-")
    return text

class UseCaseService:
    @staticmethod
    async def create_use_case(data: dict) -> UseCase:
        """Create a new use case from frontend JSON structure or direct data"""
        if 'factoryName' in data:
            # Generate slugs for URL routing
            title_slug = _slugify(data.get("title", ""))
            company_slug = _slugify(data.get("factoryName", ""))
            
            use_case_data = {
                "submitted_by": data.get("submitted_by", "system-seed"),
                "title": data["title"],
                "problem_statement": data.get("description", "Problem statement not provided."),
                "solution_description": data.get("benefits", ["Solution benefits not detailed."])[0] if data.get("benefits") else "Solution description not provided.",
                # Slugs for URL routing
                "title_slug": title_slug,
                "company_slug": company_slug,
                # Top-level summary fields used by listing and detail pages
                "factory_name": data.get("factoryName", ""),
                "category": data.get("category", "General"),
                "implementation_time": data.get("implementationTime", ""),
                # Optional direct image list for gallery; fall back to single image if provided
                "images": [data.get("image")] if data.get("image") else [],
                # Location and meta
                "industry_tags": [data.get("category", "General")],
                "region": data.get("city", "Saudi Arabia"),
                "location": {"lat": data["latitude"], "lng": data["longitude"]},
                # Impact/benefits
                "impact_metrics": {
                    "benefits": "; ".join(data.get("benefits", ["No benefits listed"]))
                },
                # Optional contact (may be absent in JSON)
                "contact_person": data.get("contactPerson"),
                "contact_title": data.get("contactTitle"),
                # Flags
                "published": True,
                "featured": True
            }

            # Optional extended fields if present in JSON
            if data.get("roiPercentage"):
                use_case_data["roi_percentage"] = data.get("roiPercentage")
            if isinstance(data.get("images"), list) and data.get("images"):
                use_case_data["images"] = data.get("images")
            if data.get("executive_summary"):
                use_case_data["executive_summary"] = data.get("executive_summary")
            if data.get("business_challenge"):
                use_case_data["business_challenge"] = data.get("business_challenge")
            if data.get("solution_details"):
                use_case_data["solution_details"] = data.get("solution_details")
            if data.get("implementation_details"):
                use_case_data["implementation_details"] = data.get("implementation_details")
            if data.get("results"):
                use_case_data["results"] = data.get("results")
            if data.get("technical_architecture"):
                use_case_data["technical_architecture"] = data.get("technical_architecture")
            if data.get("future_roadmap"):
                use_case_data["future_roadmap"] = data.get("future_roadmap")
            if data.get("lessons_learned"):
                use_case_data["lessons_learned"] = data.get("lessons_learned")
            if data.get("industryTags"):
                use_case_data["industry_tags"] = data.get("industryTags")
            if data.get("technologyTags"):
                use_case_data["technology_tags"] = data.get("technologyTags")
            if data.get("subtitle"):
                use_case_data["subtitle"] = data.get("subtitle")
            if data.get("status"):
                use_case_data["status"] = data.get("status")
            if data.get("verified_by"):
                use_case_data["verified_by"] = data.get("verified_by")
            if data.get("read_time"):
                use_case_data["read_time"] = data.get("read_time")
            if data.get("downloads"):
                use_case_data["downloads"] = data.get("downloads")
            if data.get("views"):
                use_case_data["views"] = data.get("views")
        else:
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
