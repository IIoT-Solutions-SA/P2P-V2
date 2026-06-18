"""
Use Cases API endpoints
Provides use cases, categories, stats, and contributors
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from app.models.mongo_models import UseCase, User as MongoUser, UserActivity, UserBookmark, UseCaseDraft
from typing import List, Optional
import logging
import re
from bson import ObjectId
from beanie.odm.enums import SortDirection
from beanie.operators import In
from app.schemas.usecase import (
    UseCaseCreate,
    UseCaseDraftCreate,
    UseCaseDraftResponse,
    UseCaseDraftListItem,
    UseCaseDraftPublishValidation,
    TeamMember,
    ProjectPhase
)
from app.services.usecase_service import UseCaseSubmissionService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database_service import UserService
from app.services.user_activity_service import UserActivityService
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from app.core.input_validation import check_safe_text, check_safe_tag, ALLOWED_USECASE_CATEGORIES, ALLOWED_USECASE_CATEGORIES_STR

logger = logging.getLogger(__name__)
router = APIRouter()


class QuantitativeResultUpdate(BaseModel):
    metric: Optional[Annotated[str, Field(min_length=5, max_length=200)]] = None
    baseline: Optional[Annotated[str, Field(min_length=1, max_length=200)]] = None
    current: Optional[Annotated[str, Field(min_length=1, max_length=200)]] = None
    improvement: Optional[Annotated[str, Field(min_length=2, max_length=200)]] = None

    @field_validator('metric', 'baseline', 'current', 'improvement')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v) if v is not None else v

class ChallengeSolutionUpdate(BaseModel):
    challenge: Optional[Annotated[str, Field(min_length=10, max_length=300)]] = None
    description: Optional[Annotated[str, Field(min_length=20, max_length=1000)]] = None
    solution: Optional[Annotated[str, Field(min_length=20, max_length=1000)]] = None
    outcome: Optional[Annotated[str, Field(min_length=10, max_length=500)]] = None

    @field_validator('challenge')
    @classmethod
    def validate_safe_challenge(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'solution', 'outcome')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v

class UseCaseUpdate(BaseModel):
    # Basic Information
    title: Optional[Annotated[str, Field(min_length=10, max_length=100)]] = None
    subtitle: Optional[Annotated[str, Field(min_length=10, max_length=150)]] = None
    description: Optional[Annotated[str, Field(min_length=50, max_length=5000)]] = None  # Executive summary
    category: Optional[str] = None
    factoryName: Optional[Annotated[str, Field(min_length=2, max_length=80)]] = None

    # Location
    city: Optional[Annotated[str, Field(min_length=2, max_length=50)]] = None
    latitude: Optional[Annotated[float, Field(ge=-90, le=90)]] = None
    longitude: Optional[Annotated[float, Field(ge=-180, le=180)]] = None

    # Business Challenge
    industryContext: Optional[Annotated[str, Field(min_length=50, max_length=5000)]] = None
    specificProblems: Optional[Annotated[List[Annotated[str, Field(min_length=10, max_length=500)]], Field(min_length=2, max_length=5)]] = None
    financialLoss: Optional[Annotated[str, Field(min_length=5, max_length=500)]] = None

    # Solution Overview
    selectionCriteria: Optional[Annotated[List[Annotated[str, Field(min_length=10, max_length=500)]], Field(min_length=2, max_length=5)]] = None
    selectedVendor: Optional[Annotated[str, Field(min_length=2, max_length=120)]] = None
    technologyComponents: Optional[Annotated[List[Annotated[str, Field(min_length=20, max_length=500)]], Field(min_length=1, max_length=15)]] = None

    # Implementation
    implementationTime: Optional[Annotated[str, Field(min_length=3, max_length=120)]] = None
    totalBudget: Optional[Annotated[str, Field(min_length=3, max_length=120)]] = None
    methodology: Optional[Annotated[str, Field(min_length=20, max_length=5000)]] = None

    # Results
    quantitativeResults: Optional[Annotated[List[QuantitativeResultUpdate], Field(min_length=2, max_length=4)]] = None
    roiPercentage: Optional[Annotated[str, Field(max_length=100)]] = None
    annualSavings: Optional[Annotated[str, Field(max_length=100)]] = None

    # Challenges & Solutions
    challengesSolutions: Optional[Annotated[List[ChallengeSolutionUpdate], Field(min_length=1, max_length=4)]] = None

    # Contact & Media
    contactPerson: Optional[Annotated[str, Field(max_length=120)]] = None
    contactTitle: Optional[Annotated[str, Field(max_length=120)]] = None
    images: Optional[Annotated[List[str], Field(max_length=5)]] = None

    # Additional optional fields
    industryTags: Optional[Annotated[List[str], Field(max_length=10)]] = None
    technologyTags: Optional[Annotated[List[str], Field(max_length=10)]] = None
    vendorProcess: Optional[Annotated[str, Field(max_length=2000)]] = None
    vendorSelectionReasons: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    projectTeamInternal: Optional[List[TeamMember]] = None
    projectTeamVendor: Optional[List[TeamMember]] = None
    phases: Optional[List[ProjectPhase]] = None
    qualitativeImpacts: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    roiTotalInvestment: Optional[Annotated[str, Field(max_length=100)]] = None
    roiThreeYearRoi: Optional[Annotated[str, Field(max_length=100)]] = None

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None and v not in ALLOWED_USECASE_CATEGORIES:
            raise ValueError(f"Please select a valid category from: {ALLOWED_USECASE_CATEGORIES_STR}")
        return v

    @field_validator(
        'title', 'subtitle', 'factoryName', 'city', 
        'financialLoss', 'selectedVendor',
        'implementationTime', 'totalBudget',
        'roiPercentage', 'annualSavings', 'contactPerson', 'contactTitle',
        'roiTotalInvestment', 'roiThreeYearRoi'
    )
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'industryContext', 'methodology', 'vendorProcess')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v

    @field_validator(
        'specificProblems', 'selectionCriteria', 'technologyComponents',
        'vendorSelectionReasons', 'qualitativeImpacts'
    )
    @classmethod
    def validate_safe_string_lists(cls, v):
        if v is not None:
            for item in v:
                check_safe_text(item)
        return v

    @field_validator('industryTags', 'technologyTags')
    @classmethod
    def validate_safe_tags(cls, v):
        if v is not None:
            for item in v:
                check_safe_tag(item)
        return v

# Get use case by ID for editing
@router.get("/by-id/{use_case_id}")
async def get_use_case_by_id(
    use_case_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Get a specific use case by its MongoDB ID for editing purposes"""
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(use_case_id):
            raise HTTPException(status_code=400, detail="Invalid use case ID format")
        
        # Find the use case
        use_case = await UseCase.find_one(UseCase.id == ObjectId(use_case_id))
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        
        # Convert to dict and return - this will include all nested fields needed for editing
        use_case_dict = use_case.model_dump()
        use_case_dict["_id"] = str(use_case.id)
        
        return use_case_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching use case by ID {use_case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# This is the main endpoint for listing use cases
@router.get("/")
async def get_use_cases(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, max_length=100, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Number of use cases to return"),
    skip: int = Query(0, ge=0, le=10000, description="Number of use cases to skip for pagination"),
    sort_by: str = Query("newest", description="Sort by: newest, most_viewed, most_liked"),
    session: SessionContainer = Depends(verify_session())
):
    # Validate search separately from normal content fields:
    # short legitimate manufacturing terms such as "AI" are allowed, but
    # security payloads/URLs are still rejected and the value is escaped before
    # being used in Mongo regex queries.
    escaped_search = None
    if search:
        search = re.sub(r'\s+', ' ', search.strip())
        try:
            if not search:
                escaped_search = None
            elif re.search(r"<\s*script|javascript\s*:|on(error|load|click|mouseover|keydown|submit|focus|blur|change)\s*=|\.\./|\.\.\\|/etc/passwd|oastify\.com|<!--#\w+|[\x00]", search, re.IGNORECASE):
                raise ValueError("Search query contains disallowed characters or patterns")
            elif re.search(r"https?://|www\.", search, re.IGNORECASE):
                raise ValueError("URLs and links are not allowed in search")
            elif len(re.findall(r'[\w\u0600-\u06FF]', search)) < 2:
                raise ValueError("Search query must contain at least 2 letters or numbers")
            else:
                escaped_search = re.escape(search)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid search query: {e}")

    # Validate sort_by
    if sort_by not in {"newest", "most_viewed", "most_liked"}:
        raise HTTPException(status_code=400, detail="Invalid sort_by parameter")
        
    try:
        query = {"published": True, "is_detailed_version": {"$ne": True}, "status": {"$ne": "deleted"}}
        if category and category != "all":
            category_map = { "automation": "Factory Automation", "quality": "Quality Control", "maintenance": "Predictive Maintenance", "efficiency": "Process Optimization", "innovation": "Innovation & R&D", "sustainability": "Sustainability" }
            if category not in category_map:
                raise HTTPException(status_code=400, detail="Invalid category parameter")
            query["category"] = category_map[category]
        
        if escaped_search:
            query["$or"] = [ {"title": {"$regex": escaped_search, "$options": "i"}}, {"factory_name": {"$regex": escaped_search, "$options": "i"}} ]
        
        sort_map = { "newest": ("_id", SortDirection.DESCENDING), "most_viewed": ("view_count", SortDirection.DESCENDING), "most_liked": ("like_count", SortDirection.DESCENDING) }
        sort_field, sort_direction = sort_map.get(sort_by, ("_id", SortDirection.DESCENDING))

        # Get total count for pagination
        total_count = await UseCase.find(query).count()

        # Get paginated results
        use_cases = await UseCase.find(query).sort((sort_field, sort_direction)).skip(skip).limit(limit).to_list()
        
        # Handle both old MongoDB ObjectIds and new SuperTokens IDs
        user_map = {}
        for case in use_cases:
            if case.submitted_by and case.submitted_by not in user_map:
                try:
                    # First try as MongoDB ObjectId (for existing use cases)
                    if ObjectId.is_valid(case.submitted_by):
                        mongo_user = await MongoUser.find_one(MongoUser.id == ObjectId(case.submitted_by))
                        if mongo_user:
                            user_map[case.submitted_by] = mongo_user
                    else:
                        # Try as SuperTokens ID (for new use cases)
                        pg_user = await UserService.get_user_by_supertokens_id(db, case.submitted_by)
                        if pg_user:
                            mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
                            if mongo_user:
                                user_map[case.submitted_by] = mongo_user
                except Exception:
                    pass  # Will use fallback values in response

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
        # Return with pagination metadata
        return {
            "items": response_data,
            "total": total_count,
            "limit": limit,
            "skip": skip,
            "has_more": skip + limit < total_count
        }

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

@router.post("/drafts", status_code=201)
async def save_draft(
    draft_data: dict,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Save or update a use case draft
    If draftId provided: updates that specific draft
    If NO draftId: creates a new draft (allows multiple drafts per user)
    """
    try:
        # Get authenticated user
        supertokens_user_id = session.get_user_id()

        # Resolve to MongoDB user
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        # Check if updating an existing draft (draftId provided)
        existing_draft = None
        draft_id_val = draft_data.get("draftId")
        if draft_id_val:
            # Validate draft ID format
            if not ObjectId.is_valid(draft_id_val):
                raise HTTPException(status_code=400, detail="Invalid draft ID format")

            # Find the specific draft
            existing_draft = await UseCaseDraft.find_one(UseCaseDraft.id == ObjectId(draft_id_val))

            # Verify ownership
            if existing_draft and existing_draft.user_id != user_id_str:
                raise HTTPException(status_code=403, detail="Not authorized to update this draft")

        if existing_draft:
            # Update existing draft
            update_dict = draft_data.copy()
            # Remove draftId from update_dict since it's only used for lookup
            update_dict.pop('draftId', None)

            # Update fields
            for field, value in update_dict.items():
                # Map camelCase to snake_case for MongoDB fields
                if field == "factoryName":
                    existing_draft.factory_name = value
                elif field == "currentStep":
                    existing_draft.current_step = value
                elif field == "description":
                    # Map description to multiple fields for compatibility
                    existing_draft.problem_statement = value
                    existing_draft.executive_summary = value
                    existing_draft.solution_description = value
                elif field == "industryContext":
                    if value is not None:
                        if existing_draft.business_challenge is None:
                            existing_draft.business_challenge = {}
                        existing_draft.business_challenge["industry_context"] = value
                elif field == "specificProblems":
                    if value is not None:
                        if existing_draft.business_challenge is None:
                            existing_draft.business_challenge = {}
                        existing_draft.business_challenge["specific_problems"] = value
                elif field == "financialLoss":
                    if value is not None:
                        if existing_draft.business_challenge is None:
                            existing_draft.business_challenge = {}
                        existing_draft.business_challenge["financial_loss"] = value
                elif field == "selectionCriteria":
                    if value is not None:
                        if existing_draft.solution_details is None:
                            existing_draft.solution_details = {}
                        existing_draft.solution_details["selection_criteria"] = value
                elif field == "selectedVendor":
                    if existing_draft.vendor_info is None:
                        existing_draft.vendor_info = {}
                    existing_draft.vendor_info["selected_vendor"] = value if value else None
                elif field == "technologyComponents":
                    if value is not None:
                        if existing_draft.solution_details is None:
                            existing_draft.solution_details = {}
                        existing_draft.solution_details["technology_components"] = value
                elif field == "totalBudget":
                    if value is not None:
                        if existing_draft.implementation_details is None:
                            existing_draft.implementation_details = {}
                        existing_draft.implementation_details["total_budget"] = value
                elif field == "methodology":
                    if value is not None:
                        if existing_draft.implementation_details is None:
                            existing_draft.implementation_details = {}
                        existing_draft.implementation_details["methodology"] = value
                elif field == "quantitativeResults":
                    if value is not None:
                        if existing_draft.results is None:
                            existing_draft.results = {}
                        existing_draft.results["quantitative_metrics"] = [r.dict() if hasattr(r, 'dict') else r for r in value]
                elif field == "annualSavings":
                    if value is not None:
                        if existing_draft.results is None:
                            existing_draft.results = {}
                        existing_draft.results["annual_savings"] = value
                elif field == "challengesSolutions":
                    existing_draft.challenges_and_solutions = [c.dict() if hasattr(c, 'dict') else c for c in value] if value else None
                elif field == "description":
                    # Map description to both executive_summary and problem_statement
                    existing_draft.executive_summary = value
                    existing_draft.problem_statement = value
                elif field == "city":
                    # Store city in location dict or region
                    existing_draft.region = value
                elif field == "latitude" and value is not None:
                    if existing_draft.location is None:
                        existing_draft.location = {}
                    existing_draft.location["lat"] = value
                elif field == "longitude" and value is not None:
                    if existing_draft.location is None:
                        existing_draft.location = {}
                    existing_draft.location["lng"] = value
                elif field == "contactPerson":
                    existing_draft.contact_person = value
                elif field == "contactTitle":
                    existing_draft.contact_title = value
                elif field == "implementationTime":
                    existing_draft.implementation_time = value
                elif field == "roiPercentage":
                    existing_draft.roi_percentage = value
                elif field == "industryTags":
                    existing_draft.industry_tags = value
                elif field == "technologyTags":
                    existing_draft.technology_tags = value
                elif field == "vendorProcess":
                    if existing_draft.vendor_info is None:
                        existing_draft.vendor_info = {}
                    existing_draft.vendor_info["vendor_process"] = value if value else None
                elif field == "vendorSelectionReasons":
                    if value is not None:
                        if existing_draft.vendor_info is None:
                            existing_draft.vendor_info = {}
                        existing_draft.vendor_info["selection_reasons"] = value
                elif field == "projectTeamInternal":
                    if value is not None:
                        if existing_draft.implementation_details is None:
                            existing_draft.implementation_details = {}
                        existing_draft.implementation_details["project_team_internal"] = value
                elif field == "projectTeamVendor":
                    if value is not None:
                        if existing_draft.implementation_details is None:
                            existing_draft.implementation_details = {}
                        existing_draft.implementation_details["project_team_vendor"] = value
                elif field == "phases":
                    if value is not None:
                        if existing_draft.implementation_details is None:
                            existing_draft.implementation_details = {}
                        existing_draft.implementation_details["phases"] = value
                elif field == "qualitativeImpacts":
                    if value is not None:
                        if existing_draft.results is None:
                            existing_draft.results = {}
                        existing_draft.results["qualitative_impacts"] = value
                elif field == "roiTotalInvestment":
                    if value is not None:
                        if existing_draft.results is None:
                            existing_draft.results = {}
                        existing_draft.results["roi_total_investment"] = value
                elif field == "roiThreeYearRoi":
                    if value is not None:
                        if existing_draft.results is None:
                            existing_draft.results = {}
                        existing_draft.results["roi_three_year_roi"] = value
                else:
                    # Direct mapping for fields that match
                    setattr(existing_draft, field, value)

            existing_draft.updated_at = datetime.utcnow()
            await existing_draft.save()

            logger.info(f"Updated draft {existing_draft.id} for user {user_id_str}")
            return {
                "success": True,
                "draft_id": str(existing_draft.id),
                "message": "Draft updated successfully"
            }
        else:
            # Create new draft
            draft_dict = draft_data.copy()

            # Map frontend fields to MongoDB model fields
            new_draft = UseCaseDraft(
                user_id=user_id_str,
                current_step=draft_dict.get("currentStep", 1),
                title=draft_dict.get("title"),
                subtitle=draft_dict.get("subtitle"),
                problem_statement=draft_dict.get("description"),  # Executive summary
                executive_summary=draft_dict.get("description"),
                solution_description=draft_dict.get("description"),
                category=draft_dict.get("category"),
                factory_name=draft_dict.get("factoryName"),
                region=draft_dict.get("city"),
                implementation_time=draft_dict.get("implementationTime"),
                roi_percentage=draft_dict.get("roiPercentage"),
                contact_person=draft_dict.get("contactPerson"),
                contact_title=draft_dict.get("contactTitle"),
                images=draft_dict.get("images"),
                industry_tags=draft_dict.get("industryTags"),
                technology_tags=draft_dict.get("technologyTags"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Handle location
            lat = draft_dict.get("latitude")
            lng = draft_dict.get("longitude")
            if lat is not None and lng is not None:
                new_draft.location = {"lat": lat, "lng": lng}

            # Handle nested objects
            if draft_dict.get("industryContext") or draft_dict.get("specificProblems") or draft_dict.get("financialLoss"):
                new_draft.business_challenge = {
                    "industry_context": draft_dict.get("industryContext"),
                    "specific_problems": draft_dict.get("specificProblems"),
                    "financial_loss": draft_dict.get("financialLoss")
                }

            if draft_dict.get("selectionCriteria") or draft_dict.get("technologyComponents"):
                new_draft.solution_details = {
                    "selection_criteria": draft_dict.get("selectionCriteria"),
                    "technology_components": draft_dict.get("technologyComponents")
                }

            if draft_dict.get("selectedVendor") or draft_dict.get("vendorProcess") or draft_dict.get("vendorSelectionReasons"):
                new_draft.vendor_info = {
                    "selected_vendor": draft_dict.get("selectedVendor"),
                    "vendor_process": draft_dict.get("vendorProcess"),
                    "selection_reasons": draft_dict.get("vendorSelectionReasons")
                }

            if draft_dict.get("totalBudget") or draft_dict.get("methodology") or draft_dict.get("projectTeamInternal") or draft_dict.get("projectTeamVendor") or draft_dict.get("phases"):
                new_draft.implementation_details = {
                    "total_budget": draft_dict.get("totalBudget"),
                    "methodology": draft_dict.get("methodology"),
                    "project_team_internal": draft_dict.get("projectTeamInternal"),
                    "project_team_vendor": draft_dict.get("projectTeamVendor"),
                    "phases": draft_dict.get("phases")
                }

            if draft_dict.get("quantitativeResults") or draft_dict.get("annualSavings") or draft_dict.get("qualitativeImpacts") or draft_dict.get("roiTotalInvestment") or draft_dict.get("roiThreeYearRoi"):
                new_draft.results = {}
                if draft_dict.get("quantitativeResults"):
                    new_draft.results["quantitative_metrics"] = [r.dict() if hasattr(r, 'dict') else r for r in draft_dict["quantitativeResults"]]
                if draft_dict.get("annualSavings"):
                    new_draft.results["annual_savings"] = draft_dict["annualSavings"]
                if draft_dict.get("qualitativeImpacts"):
                    new_draft.results["qualitative_impacts"] = draft_dict["qualitativeImpacts"]
                if draft_dict.get("roiTotalInvestment"):
                    new_draft.results["roi_total_investment"] = draft_dict["roiTotalInvestment"]
                if draft_dict.get("roiThreeYearRoi"):
                    new_draft.results["roi_three_year_roi"] = draft_dict["roiThreeYearRoi"]

            if draft_dict.get("challengesSolutions"):
                new_draft.challenges_and_solutions = [c.dict() if hasattr(c, 'dict') else c for c in draft_dict["challengesSolutions"]]

            if draft_dict.get("technical_architecture"):
                new_draft.technical_architecture = draft_dict["technical_architecture"]

            if draft_dict.get("future_roadmap"):
                new_draft.future_roadmap = [f.dict() if hasattr(f, 'dict') else f for f in draft_dict["future_roadmap"]]

            if draft_dict.get("lessons_learned"):
                new_draft.lessons_learned = [l.dict() if hasattr(l, 'dict') else l for l in draft_dict["lessons_learned"]]

            await new_draft.create()

            logger.info(f"Created new draft {new_draft.id} for user {user_id_str}")
            return {
                "success": True,
                "draft_id": str(new_draft.id),
                "message": "Draft created successfully"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving draft: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save draft")


@router.get("/drafts", response_model=List[UseCaseDraftListItem])
async def list_user_drafts(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all drafts for the authenticated user
    Returns lightweight list for dashboard display
    """
    try:
        # Get authenticated user
        supertokens_user_id = session.get_user_id()

        # Resolve to MongoDB user
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        # Fetch user's drafts, sorted by most recently updated
        drafts = await UseCaseDraft.find(
            UseCaseDraft.user_id == user_id_str
        ).sort(-UseCaseDraft.updated_at).to_list()

        # Convert to response format
        response = []
        for draft in drafts:
            response.append({
                "id": str(draft.id),
                "title": draft.title or "Untitled Draft",
                "subtitle": draft.subtitle,
                "description": draft.executive_summary or draft.problem_statement,
                "category": draft.category,
                "current_step": draft.current_step,
                "created_at": draft.created_at.isoformat(),
                "updated_at": draft.updated_at.isoformat()
            })

        logger.info(f"Retrieved {len(response)} drafts for user {user_id_str}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing drafts: {e}")
        raise HTTPException(status_code=500, detail="Failed to list drafts")


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific draft by ID
    Returns complete draft data for editing
    """
    try:
        # Validate draft ID format
        if not ObjectId.is_valid(draft_id):
            raise HTTPException(status_code=400, detail="Invalid draft ID format")

        # Get authenticated user
        supertokens_user_id = session.get_user_id()

        # Resolve to MongoDB user
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        # Fetch draft
        draft = await UseCaseDraft.find_one(UseCaseDraft.id == ObjectId(draft_id))
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")

        # Verify ownership
        if draft.user_id != user_id_str:
            raise HTTPException(status_code=403, detail="Not authorized to access this draft")

        # Prepare response with mapped fields (camelCase for frontend)
        response = {
            "id": str(draft.id),
            "user_id": draft.user_id,
            "currentStep": draft.current_step,
            "title": draft.title,
            "subtitle": draft.subtitle,
            "description": draft.executive_summary or draft.problem_statement,
            "category": draft.category,
            "factoryName": draft.factory_name,
            "city": draft.region,
            "images": draft.images or [],
            "contactPerson": draft.contact_person,
            "contactTitle": draft.contact_title,
            "implementationTime": draft.implementation_time,
            "roiPercentage": draft.roi_percentage,
            "industryTags": draft.industry_tags or [],
            "technologyTags": draft.technology_tags or [],
            "created_at": draft.created_at.isoformat(),
            "updated_at": draft.updated_at.isoformat()
        }

        # Extract location
        if draft.location:
            response["latitude"] = draft.location.get("lat")
            response["longitude"] = draft.location.get("lng")

        # Extract business challenge fields
        if draft.business_challenge:
            response["industryContext"] = draft.business_challenge.get("industry_context")
            response["specificProblems"] = draft.business_challenge.get("specific_problems") or []
            response["financialLoss"] = draft.business_challenge.get("financial_loss")

        # Extract solution details
        if draft.solution_details:
            response["selectionCriteria"] = draft.solution_details.get("selection_criteria") or []
            response["technologyComponents"] = draft.solution_details.get("technology_components") or []

        # Extract vendor info
        if draft.vendor_info:
            response["selectedVendor"] = draft.vendor_info.get("selected_vendor")
            response["vendorProcess"] = draft.vendor_info.get("vendor_process")
            response["vendorSelectionReasons"] = draft.vendor_info.get("selection_reasons") or []

        # Extract implementation details
        if draft.implementation_details:
            response["totalBudget"] = draft.implementation_details.get("total_budget")
            response["methodology"] = draft.implementation_details.get("methodology")
            response["projectTeamInternal"] = draft.implementation_details.get("project_team_internal") or []
            response["projectTeamVendor"] = draft.implementation_details.get("project_team_vendor") or []
            response["phases"] = draft.implementation_details.get("phases") or []

        # Extract results
        if draft.results:
            response["quantitativeResults"] = draft.results.get("quantitative_metrics") or []
            response["annualSavings"] = draft.results.get("annual_savings")
            response["qualitativeImpacts"] = draft.results.get("qualitative_impacts") or []
            response["roiTotalInvestment"] = draft.results.get("roi_total_investment")
            response["roiThreeYearRoi"] = draft.results.get("roi_three_year_roi")

        # Extract challenges & solutions
        if draft.challenges_and_solutions:
            response["challengesSolutions"] = draft.challenges_and_solutions

        # Extract extended sections
        if draft.technical_architecture:
            response["technical_architecture"] = draft.technical_architecture
        if draft.future_roadmap:
            response["future_roadmap"] = draft.future_roadmap
        if draft.lessons_learned:
            response["lessons_learned"] = draft.lessons_learned

        logger.info(f"Retrieved draft {draft_id} for user {user_id_str}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error getting draft {draft_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the draft. Please try again.")


@router.delete("/drafts/{draft_id}", status_code=204)
async def delete_draft(
    draft_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a draft
    Only the draft owner can delete it
    """
    try:
        # Validate draft ID format
        if not ObjectId.is_valid(draft_id):
            raise HTTPException(status_code=400, detail="Invalid draft ID format")

        # Get authenticated user
        supertokens_user_id = session.get_user_id()

        # Resolve to MongoDB user
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        # Fetch draft
        draft = await UseCaseDraft.find_one(UseCaseDraft.id == ObjectId(draft_id))
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")

        # Verify ownership
        if draft.user_id != user_id_str:
            raise HTTPException(status_code=403, detail="Not authorized to delete this draft")

        # Delete draft
        await draft.delete()

        logger.info(f"Deleted draft {draft_id} for user {user_id_str}")
        from fastapi import Response
        return Response(status_code=204)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting draft {draft_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete draft")


@router.post("/drafts/{draft_id}/publish")
async def publish_draft(
    draft_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Convert a draft to a published use case
    Validates required fields and creates a UseCase from the draft
    Deletes the draft after successful publication
    """
    try:
        # Validate draft ID format
        if not ObjectId.is_valid(draft_id):
            raise HTTPException(status_code=400, detail="Invalid draft ID format")

        # Get authenticated user
        supertokens_user_id = session.get_user_id()

        # Resolve to MongoDB user
        pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not pg_user:
            raise HTTPException(status_code=401, detail="Invalid session user")

        mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)
        if not mongo_user:
            raise HTTPException(status_code=404, detail="User profile not found")

        user_id_str = str(mongo_user.id)

        # Fetch draft
        draft = await UseCaseDraft.find_one(UseCaseDraft.id == ObjectId(draft_id))
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")

        # Verify ownership
        if draft.user_id != user_id_str:
            raise HTTPException(status_code=403, detail="Not authorized to publish this draft")

        # Validate required fields for publication
        missing_fields = []
        if not draft.title:
            missing_fields.append("title")
        if not draft.subtitle:
            missing_fields.append("subtitle")
        if not draft.category:
            missing_fields.append("category")
        if not draft.factory_name:
            missing_fields.append("factoryName")
        if not draft.region:
            missing_fields.append("city")
        if not draft.location or not draft.location.get("lat") or not draft.location.get("lng"):
            missing_fields.append("location")
        if not draft.business_challenge or not draft.business_challenge.get("industry_context"):
            missing_fields.append("industryContext")
        if not draft.business_challenge or not draft.business_challenge.get("specific_problems"):
            missing_fields.append("specificProblems")
        if not draft.solution_details or not draft.solution_details.get("selection_criteria"):
            missing_fields.append("selectionCriteria")
        if not draft.implementation_details or not draft.implementation_details.get("total_budget"):
            missing_fields.append("totalBudget")
        if not draft.implementation_details or not draft.implementation_details.get("methodology"):
            missing_fields.append("methodology")

        if missing_fields:
            return {
                "success": False,
                "can_publish": False,
                "missing_fields": missing_fields,
                "message": f"Cannot publish: missing required fields"
            }

        # Create UseCase from draft
        use_case = UseCase(
            submitted_by=user_id_str,
            title=draft.title,
            subtitle=draft.subtitle,
            problem_statement=draft.problem_statement or draft.executive_summary,
            executive_summary=draft.executive_summary or draft.problem_statement,
            solution_description=draft.solution_description or "",
            category=draft.category,
            factory_name=draft.factory_name,
            region=draft.region,
            location=draft.location,
            business_challenge=draft.business_challenge,
            solution_details=draft.solution_details,
            vendor_info=draft.vendor_info,
            implementation_details=draft.implementation_details,
            results=draft.results,
            challenges_and_solutions=draft.challenges_and_solutions or [],
            technical_architecture=draft.technical_architecture,
            future_roadmap=draft.future_roadmap or [],
            lessons_learned=draft.lessons_learned or [],
            implementation_time=draft.implementation_time,
            roi_percentage=draft.roi_percentage,
            contact_person=draft.contact_person,
            contact_title=draft.contact_title,
            images=draft.images or [],
            industry_tags=draft.industry_tags or [],
            technology_tags=draft.technology_tags or [],
            published=True,
            status="published",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        await use_case.create()

        # Log activity
        await UserActivityService.log_activity(
            user_id=user_id_str,
            activity_type="usecase",
            target_id=str(use_case.id),
            target_title=use_case.title,
            target_category=use_case.category,
            description=f"Published use case: {use_case.title}"
        )

        # Delete the draft after successful publication
        await draft.delete()

        logger.info(f"Published draft {draft_id} as use case {use_case.id} for user {user_id_str}")

        return {
            "success": True,
            "can_publish": True,
            "use_case_id": str(use_case.id),
            "message": "Draft published successfully",
            "use_case": {
                "id": str(use_case.id),
                "title": use_case.title,
                "slug": use_case.title_slug
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing draft {draft_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to publish draft")
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

        cases = await UseCase.find(In(UseCase.id, target_ids), {"status": {"$ne": "deleted"}}).to_list()
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
            {"$match": {"published": True, "is_detailed_version": {"$ne": True}, "status": {"$ne": "deleted"}}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_counts_cursor = UseCase.aggregate(pipeline)
        category_counts_list = await category_counts_cursor.to_list(length=100)
        
        category_counts = {item['_id']: item['count'] for item in category_counts_list if item['_id']}
        total_cases = await UseCase.find({"published": True, "is_detailed_version": {"$ne": True}, "status": {"$ne": "deleted"}}).count()

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
        total_use_cases = await UseCase.find({"published": True, "is_detailed_version": {"$ne": True}, "status": {"$ne": "deleted"}}).count()
        pipeline = [
            {"$match": {"published": True, "factory_name": {"$ne": None}, "status": {"$ne": "deleted"}}},
            {"$group": {"_id": "$factory_name"}},
            {"$count": "unique_companies"}
        ]
        companies_cursor = UseCase.aggregate(pipeline)
        companies_result = await companies_cursor.to_list(length=1)
        contributing_companies = companies_result[0]['unique_companies'] if companies_result else 0
        success_stories = await UseCase.find({"published": True, "featured": True, "status": {"$ne": "deleted"}}).count()
        
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


@router.put("/{use_case_id}")
async def update_use_case(
    use_case_id: str,
    update_data: UseCaseUpdate,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Update a use case (only by author)"""
    try:
        supertokens_user_id = session.get_user_id()
        
        updated_use_case = await UseCaseSubmissionService.update_use_case(
            db=db,
            user_supertokens_id=supertokens_user_id,
            use_case_id=use_case_id,
            update_data=update_data.dict(exclude_unset=True)
        )
        return {"success": True, "use_case": {"id": str(updated_use_case.id), "title": updated_use_case.title}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating use case {use_case_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update use case")


@router.delete("/{use_case_id}", status_code=204)
async def delete_use_case(
    use_case_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Delete a use case (only by author) - soft delete"""
    try:
        supertokens_user_id = session.get_user_id()
        result = await UseCaseSubmissionService.delete_use_case(
            db=db,
            user_supertokens_id=supertokens_user_id,
            use_case_id=use_case_id
        )
        # Return 204 No Content on successful delete (no response body)
        from fastapi import Response
        return Response(status_code=204)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting use case {use_case_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete use case")


# ===== DRAFT ENDPOINTS =====

