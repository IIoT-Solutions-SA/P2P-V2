"""
Use Cases API endpoints
Provides use cases, categories, stats, and contributors
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from app.models.mongo_models import UseCase, User as MongoUser
from typing import List, Optional
import logging
from bson import ObjectId
from beanie.odm.enums import SortDirection
from beanie.operators import In

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
            response_data.append({
                "id": str(case.id),
                "title": case.title,
                "title_slug": case.title_slug, # The missing field
                "company_slug": case.company_slug,
                "company": getattr(case, 'factory_name', "Unknown"),
                "industry": getattr(submitter, 'industry_sector', "Manufacturing") if submitter else "Manufacturing",
                "category": getattr(case, 'category', "General"),
                "description": getattr(case, 'problem_statement', ""),
                "results": getattr(case, 'impact_metrics', {}),
                "timeframe": getattr(case, 'implementation_time', "N/A"),
                "views": getattr(case, 'view_count', 0),
                "likes": getattr(case, 'like_count', 0),
                "saves": getattr(case, 'bookmark_count', 0),
                "verified": getattr(case, 'status', "") == "verified",
                "featured": getattr(case, 'featured', False),
                "tags": getattr(case, 'industry_tags', []),
                "publishedBy": getattr(submitter, 'name', "Anonymous") if submitter else "Anonymous",
                "publisherTitle": getattr(submitter, 'title', "Contributor") if submitter else "Contributor",
                "publishedDate": "2 weeks ago"
            })
        return response_data

    except Exception as e:
        logger.error(f"Error getting use cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to get use cases")

@router.get("/{company_slug}/{title_slug}")
async def get_use_case_by_slug(
    company_slug: str,
    title_slug: str,
    session: SessionContainer = Depends(verify_session())
):
    try:
        use_case = await UseCase.find_one(
            UseCase.company_slug == company_slug, 
            UseCase.title_slug == title_slug
        )
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        if use_case.has_detailed_view and use_case.detailed_version_id:
            detailed_use_case = await UseCase.get(use_case.detailed_version_id)
            if detailed_use_case:
                return detailed_use_case
            logger.warning(f"Detailed use case ID {use_case.detailed_version_id} not found for basic case {use_case.id}")
        return use_case
    except Exception as e:
        logger.error(f"Error getting use case by slug '{slug}': {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve use case")


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
