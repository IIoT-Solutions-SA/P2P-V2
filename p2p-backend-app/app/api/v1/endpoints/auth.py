"""Authentication endpoints for user management."""

from fastapi import APIRouter, Depends, HTTPException
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import UserProfile
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile with organization details."""
    try:
        user_id = session.get_user_id()
        logger.info(f"Fetching profile for user: {user_id}")
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.supertokens_user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found in database: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get organization
        org_result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = org_result.scalar_one_or_none()
        
        return UserProfile(
            id=str(user.id),
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            role=user.role,
            organization={
                "id": str(organization.id),
                "name": organization.name,
                "size": organization.size,
                "industry": organization.industry,
                "country": organization.country,
                "city": organization.city,
            } if organization else None,
            isActive=user.is_active,
            createdAt=user.created_at.isoformat(),
        )
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")


@router.post("/session/refresh")
async def refresh_session(session: SessionContainer = Depends(verify_session())):
    """Refresh the user session."""
    try:
        # SuperTokens handles session refresh automatically
        return {"status": "OK", "message": "Session refreshed"}
    except Exception as e:
        logger.error(f"Session refresh error: {e}")
        raise HTTPException(status_code=401, detail="Session refresh failed")