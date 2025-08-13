from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.core.database import get_db
from app.services.database_service import UserService
from app.models.mongo_models import Organization, User as MongoUser
from app.models.pg_models import User as PGUser

router = APIRouter()

@router.get("/me")
async def get_current_user(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user profile.
    Requires valid SuperTokens session.
    """
    try:
        # Get SuperTokens user ID from session
        supertokens_user_id = session.get_user_id()
        
        # Find user in our database by supertokens_id
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User profile not found. Please contact support."
            )
        
        # Resolve organization from Mongo profile if available; fallback to domain inference
        mongo_profile = await MongoUser.find_one(MongoUser.email == user.email)
        organization = None
        if mongo_profile and mongo_profile.organization_id:
            org = await Organization.find_one(Organization.id == mongo_profile.organization_id)
            if org:
                organization = {
                    "id": str(org.id),
                    "name": org.name,
                    "domain": org.domain,
                    "industry": org.industry_sector,
                    "size": org.size,
                    "country": org.country,
                    "city": org.city,
                    "isActive": org.is_active,
                    "createdAt": org.created_at,
                    "adminUserId": str(user.id)
                }
        if organization is None:
            domain = user.email.split('@')[1]
            company_name = domain.split('.')[0].replace('-', ' ').title()
            organization = {
                "id": f"org-{user.id}",
                "name": company_name,
                "domain": domain,
                "industry": "Technology",
                "size": "medium",
                "country": "Saudi Arabia",
                "city": "Riyadh",
                "isActive": True,
                "createdAt": user.created_at,
                "adminUserId": str(user.id)
            }
        
        # Format user response
        user_response = {
            "id": str(user.id),
            "mongo_id": str(mongo_profile.id) if mongo_profile else None,  # Add mongo_id for authorization checks
            "email": user.email,
            "firstName": user.name.split(' ')[0] if user.name else "",
            "lastName": " ".join(user.name.split(' ')[1:]) if len(user.name.split(' ')) > 1 else "",
            "role": user.role,
            "title": mongo_profile.title if mongo_profile and hasattr(mongo_profile, 'title') else "Team Member",
            "organizationId": organization["id"],  
            "isActive": user.is_active,
            "lastLogin": user.updated_at,  # Using updated_at as proxy for last login
            "createdAt": user.created_at
        }
        
        return {
            "user": user_response,
            "organization": organization
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching user profile: {str(e)}"
        )