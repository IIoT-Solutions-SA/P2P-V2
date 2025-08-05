from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.core.database import get_db
from app.services.database_service import UserService
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
        
        # Generate organization data from email domain
        domain = user.email.split('@')[1]
        # Convert domain to company name (e.g., "advanced-electronics.com" → "Advanced Electronics")
        company_name = domain.replace('.com', '').replace('-', ' ').title()
        
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
            "email": user.email,
            "firstName": user.name.split(' ')[0] if user.name else "",
            "lastName": " ".join(user.name.split(' ')[1:]) if len(user.name.split(' ')) > 1 else "",
            "role": user.role,
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