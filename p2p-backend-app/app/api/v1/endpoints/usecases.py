"""
Use Cases API endpoints
Provides use cases, categories, stats, and contributors
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from app.models.mongo_models import UseCase, User as MongoUser, UserActivity, UserBookmark
from typing import List, Optional
import logging
from bson import ObjectId
from beanie.odm.enums import SortDirection
from beanie.operators import In
from app.schemas.usecase import UseCaseCreate
from app.services.usecase_service import UseCaseSubmissionService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database_service import UserService
from app.services.user_activity_service import UserActivityService
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# This is the main endpoint for listing use cases
@router.get("/")
async def get_use_cases(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, description="Number of use cases to return"),
    sort_by: str = Query("newest", description="Sort by: newest, most_viewed, most_liked"),
    session: SessionContainer = Depends(verify_session())
):
    try:
        query = {"published": True, "is_detailed_version": {"$ne": True}}
        if category and category != "all":
            category_map = { "automation": "Factory Automation", "quality": "Quality Control", "maintenance": "Predictive Maintenance", "efficiency": "Process Optimization", "innovation": "Innovation & R&D", "sustainability": "Sustainability" }
            if category in category_map: query["category"] = category_map[category]
        
        if search:
            query["$or"] = [ {"title": {"$regex": search, "$options": "i"}}, {"factory_name": {"$regex": search, "$options": "i"}} ]
        
        sort_map = { "newest": ("_id", SortDirection.DESCENDING), "most_viewed": ("view_count", SortDirection.DESCENDING), "most_liked": ("like_count", SortDirection.DESCENDING) }
        sort_field, sort_direction = sort_map.get(sort_by, ("_id", SortDirection.DESCENDING))

        use_cases = await UseCase.find(query).sort((sort_field, sort_direction)).limit(limit).to_list()
        
        user_ids = {ObjectId(case.submitted_by) for case in use_cases if case.submitted_by}
        user_map = {}
        if user_ids:
            users_list = await MongoUser.find(In(MongoUser.id, list(user_ids))).to_list()
            user_map = {str(user.id): user for user in users_list}

        response_data = []
        for case in use_cases:
            submitter = user_map.get(case.submitted_by)

            # Derive optional image and benefits list for map/frontend usage
            image_url = None
            try:
                images_field = getattr(case, 'images', None)
                if isinstance(images_field, list) and len(images_field) > 0:
                    image_url = images_field[0]
            except Exception:
                image_url = None
            if not image_url:
                # Safe placeholder
                image_url = "https://images.unsplash.com/photo-1581090700227-1e37b190418e?w=1200&auto=format&fit=crop&q=60"

            impact_metrics = getattr(case, 'impact_metrics', {}) or {}
            benefits_raw = impact_metrics.get('benefits')
            benefits_list = []
            if isinstance(benefits_raw, str):
                benefits_list = [b.strip() for b in benefits_raw.split(';') if b.strip()]

            # Extract coordinates if available
            lat = None
            lng = None
            try:
                location = getattr(case, 'location', None)
                if isinstance(location, dict):
                    lat = location.get('lat')
                    lng = location.get('lng')
            except Exception:
                lat = None
                lng = None

            response_data.append({
                "id": str(case.id),
                "title": case.title,
                "title_slug": case.title_slug,
                "company_slug": case.company_slug,
                "company": getattr(case, 'factory_name', "Unknown"),
                "industry": getattr(submitter, 'industry_sector', "Manufacturing") if submitter else "Manufacturing",
                "category": getattr(case, 'category', "General"),
                "description": getattr(case, 'problem_statement', ""),
                "results": impact_metrics,
                "timeframe": getattr(case, 'implementation_time', "N/A"),
                "views": getattr(case, 'view_count', 0),
                "likes": getattr(case, 'like_count', 0),
                "saves": getattr(case, 'bookmark_count', 0),
                "verified": getattr(case, 'status', "") == "verified",
                "featured": getattr(case, 'featured', False),
                "tags": getattr(case, 'industry_tags', []),
                "publishedBy": getattr(submitter, 'name', case.factory_name or "Anonymous") if submitter else (getattr(case, 'factory_name', None) or "Anonymous"),
                "publisherTitle": getattr(submitter, 'title', "Contributor") if submitter else "Contributor",
                "publishedDate": "2 weeks ago",
                # Extra fields helpful for the map
                "region": getattr(case, 'region', None),
                "latitude": lat,
                "longitude": lng,
                "image": image_url,
                "benefits_list": benefits_list,
            })
        return response_data

    except Exception as e:
        logger.error(f"Error getting use cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to get use cases")


@router.post("/", status_code=201)
async def submit_new_use_case(
    use_case_data: UseCaseCreate,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_supertokens_id = session.get_user_id()
        new_use_case = await UseCaseSubmissionService.create_use_case(db, user_supertokens_id, use_case_data)
        return {"status": "success", "id": str(new_use_case.id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting use case: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit use case")

@router.get("/{company_slug}/{title_slug}")
async def get_use_case_by_slug(
    company_slug: str,
    title_slug: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db),
):
    try:
        use_case = await UseCase.find_one(
            UseCase.company_slug == company_slug, 
            UseCase.title_slug == title_slug
        )
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        # Increment view count once per user per time window (prevents React StrictMode double fetch bumps)
        try:
            supertokens_user_id = session.get_user_id()
            pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
            mongo_user = None
            if pg_user and pg_user.email:
                mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)

            should_increment = True
            if mongo_user:
                user_id_str = str(mongo_user.id)
                # Check if user has EVER viewed this use case (realistic view counting)
                recent_view = await UserActivity.find_one(
                    UserActivity.user_id == user_id_str,
                    UserActivity.activity_type == "view",
                    UserActivity.target_id == str(use_case.id),
                )
                if recent_view:
                    should_increment = False

            if should_increment:
                use_case.view_count = (getattr(use_case, 'view_count', 0) or 0) + 1
                await use_case.save()
                # Log the view activity (lightweight)
                if mongo_user:
                    await UserActivityService.log_activity(
                        user_id=str(mongo_user.id),
                        activity_type="view",
                        target_id=str(use_case.id),
                        target_title=use_case.title,
                        target_category=use_case.category,
                        description=f"Viewed use case: {use_case.title}",
                    )
        except Exception:
            # Non-fatal
            pass
        if use_case.has_detailed_view and use_case.detailed_version_id:
            detailed_use_case = await UseCase.get(use_case.detailed_version_id)
            if detailed_use_case:
                return detailed_use_case
            logger.warning(f"Detailed use case ID {use_case.detailed_version_id} not found for basic case {use_case.id}")
        return use_case
    except Exception as e:
        logger.error(f"Error getting use case by slug '{company_slug}/{title_slug}': {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve use case")


@router.post("/{company_slug}/{title_slug}/like")
async def like_use_case(
    company_slug: str,
    title_slug: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db),
):
    try:
        use_case = await UseCase.find_one(
            UseCase.company_slug == company_slug,
            UseCase.title_slug == title_slug
        )
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")

        # Resolve user (session -> PG -> Mongo)
        supertokens_user_id = session.get_user_id()
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        # Toggle like using UserActivity collection (no liked_by field on UseCase)
        existing_like = await UserActivity.find_one(
            UserActivity.user_id == user_id_str,
            UserActivity.activity_type == "like",
            UserActivity.target_id == str(use_case.id),
        )
        if existing_like:
            # Unlike: delete activity and decrement like_count
            await existing_like.delete()
            try:
                use_case.like_count = max(0, (getattr(use_case, 'like_count', 0) or 0) - 1)
                # Maintain liked_by set as well
                try:
                    if user_id_str in getattr(use_case, 'liked_by', []):
                        use_case.liked_by.remove(user_id_str)
                except Exception:
                    pass
                await use_case.save()
            except Exception:
                pass
            return {"liked": False, "likes": getattr(use_case, 'like_count', 0)}

        # Like: log activity and increment like_count
        await UserActivityService.log_activity(
            user_id=user_id_str,
            activity_type="like",
            target_id=str(use_case.id),
            target_title=use_case.title,
            target_category=use_case.category,
            description=f"Liked use case: {use_case.title}",
        )
        try:
            use_case.like_count = (getattr(use_case, 'like_count', 0) or 0) + 1
            # Maintain liked_by set as well
            try:
                if gettatr := getattr:  # guard to avoid syntax error in accidental code
                    pass
            except Exception:
                pass
            if getattr(use_case, 'liked_by', None) is None:
                use_case.liked_by = []
            if user_id_str not in use_case.liked_by:
                use_case.liked_by.append(user_id_str)
            await use_case.save()
        except Exception:
            pass
        return {"liked": True, "likes": getattr(use_case, 'like_count', 0)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling like for use case {company_slug}/{title_slug}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update like")


@router.post("/{company_slug}/{title_slug}/bookmark")
async def bookmark_use_case(
    company_slug: str,
    title_slug: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db),
):
    try:
        use_case = await UseCase.find_one(
            UseCase.company_slug == company_slug,
            UseCase.title_slug == title_slug
        )
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")

        # Resolve user
        supertokens_user_id = session.get_user_id()
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        existing = await UserBookmark.find_one(
            UserBookmark.user_id == user_id_str,
            UserBookmark.target_id == str(use_case.id),
        )
        if existing:
            # Unbookmark: delete doc and decrement counter
            await existing.delete()
            try:
                use_case.bookmark_count = max(0, (getattr(use_case, 'bookmark_count', 0) or 0) - 1)
                await use_case.save()
            except Exception:
                pass
            return {"bookmarked": False, "bookmarks": getattr(use_case, 'bookmark_count', 0)}

        # Bookmark and log activity via service
        await UserActivityService.add_bookmark(
            user_id=user_id_str,
            target_type="use_case",
            target_id=str(use_case.id),
            target_title=use_case.title,
            target_category=use_case.category,
        )
        try:
            use_case.bookmark_count = (getattr(use_case, 'bookmark_count', 0) or 0) + 1
            await use_case.save()
        except Exception:
            pass
        return {"bookmarked": True, "bookmarks": getattr(use_case, 'bookmark_count', 0)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling bookmark for use case {company_slug}/{title_slug}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bookmark")


@router.get("/bookmarks")
async def get_use_case_bookmarks(
    limit: int = Query(20, description="Max bookmarks to return"),
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Resolve user
        supertokens_user_id = session.get_user_id()
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")
        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)
        bookmarks = await UserBookmark.find(
            UserBookmark.user_id == user_id_str,
            UserBookmark.target_type == "use_case",
        ).sort(-UserBookmark.created_at).limit(limit).to_list()

        if not bookmarks:
            return []

        from bson import ObjectId
        target_ids = []
        for b in bookmarks:
            try:
                target_ids.append(ObjectId(b.target_id))
            except Exception:
                continue

        if not target_ids:
            return []

        cases = await UseCase.find(In(UseCase.id, target_ids)).to_list()
        case_map = {str(c.id): c for c in cases}
        response = []
        for b in bookmarks:
            uc = case_map.get(b.target_id)
            if not uc:
                # Fallback: return bookmark meta only
                response.append({
                    "id": b.target_id,
                    "title": b.target_title,
                    "category": b.target_category,
                    "created_at": getattr(b, 'created_at', None),
                })
                continue
            response.append({
                "id": str(uc.id),
                "title": uc.title,
                "company": getattr(uc, 'factory_name', None),
                "category": getattr(uc, 'category', None),
                "views": getattr(uc, 'view_count', 0),
                "likes": getattr(uc, 'like_count', 0),
                "saves": getattr(uc, 'bookmark_count', 0),
                "title_slug": uc.title_slug,
                "company_slug": uc.company_slug,
                "created_at": getattr(b, 'created_at', None),
            })

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bookmarks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bookmarks")


@router.get("/categories")
async def get_use_case_categories(session: SessionContainer = Depends(verify_session())):
    try:
        pipeline = [
            {"$match": {"published": True, "is_detailed_version": {"$ne": True}}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_counts_cursor = UseCase.aggregate(pipeline)
        category_counts_list = await category_counts_cursor.to_list(length=100)
        
        category_counts = {item['_id']: item['count'] for item in category_counts_list if item['_id']}
        total_cases = await UseCase.find({"published": True, "is_detailed_version": {"$ne": True}}).count()

        category_definitions = [
            {"id": "automation", "name": "Factory Automation"},
            {"id": "quality", "name": "Quality Control"},
            {"id": "maintenance", "name": "Predictive Maintenance"},
            {"id": "efficiency", "name": "Process Optimization"},
            {"id": "innovation", "name": "Innovation & R&D"},
            {"id": "sustainability", "name": "Sustainability"}
        ]

        categories_response = [{"id": "all", "name": "All Use Cases", "count": total_cases}]
        for cat_def in category_definitions:
            count = category_counts.get(cat_def["name"], 0)
            if count > 0:
                categories_response.append({
                    "id": cat_def["id"],
                    "name": cat_def["name"],
                    "count": count
                })

        return categories_response
    except Exception as e:
        logger.error(f"Error getting use case categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get use case categories")

@router.get("/stats")
async def get_use_case_stats(session: SessionContainer = Depends(verify_session())):
    try:
        total_use_cases = await UseCase.find({"published": True, "is_detailed_version": {"$ne": True}}).count()
        pipeline = [
            {"$match": {"published": True, "factory_name": {"$ne": None}}},
            {"$group": {"_id": "$factory_name"}},
            {"$count": "unique_companies"}
        ]
        companies_cursor = UseCase.aggregate(pipeline)
        companies_result = await companies_cursor.to_list(length=1)
        contributing_companies = companies_result[0]['unique_companies'] if companies_result else 0
        success_stories = await UseCase.find({"published": True, "featured": True}).count()
        
        return {
            "totalUseCases": total_use_cases,
            "contributingCompanies": contributing_companies,
            "successStories": success_stories
        }
    except Exception as e:
        logger.error(f"Error getting use case stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get use case stats")

@router.get("/contributors")
async def get_top_contributors(
    limit: int = Query(3, description="Number of top contributors to return"),
    session: SessionContainer = Depends(verify_session())
):
    try:
        pipeline = [
            {"$match": {"published": True, "factory_name": {"$ne": None}}},
            {"$group": {"_id": "$factory_name", "cases": {"$sum": 1}}},
            {"$sort": {"cases": -1}},
            {"$limit": limit}
        ]
        contributors_cursor = UseCase.aggregate(pipeline)
        top_contributors_list = await contributors_cursor.to_list(length=limit)

        contributors_response = []
        for contributor in top_contributors_list:
            company_name = contributor['_id']
            contributors_response.append({
                "name": company_name,
                "cases": contributor['cases'],
                "avatar": company_name[0].upper() if company_name else "U"
            })

        return contributors_response
    except Exception as e:
        logger.error(f"Error getting top contributors: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top contributors")
