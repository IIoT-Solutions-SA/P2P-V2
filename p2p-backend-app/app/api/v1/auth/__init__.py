"""
Authentication API endpoints with SuperTokens integration.

This module bridges the frontend auth requests with SuperTokens
and handles organization-based user creation.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
import uuid

from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import UserRole, UserStatus, OrganizationStatus, IndustryType
from app.crud.organization import organization as organization_crud
from app.crud.user import user as user_crud
from app.core.logging import get_logger
from app.schemas.user import User as UserResponse
from app.schemas.organization import Organization as OrganizationResponse
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session as st_verify_session

logger = get_logger(__name__)

auth_router = APIRouter()


class SignupRequest(BaseModel):
    """Request model for organization-based signup."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    organizationName: str = Field(..., min_length=1, max_length=200)
    organizationSize: str = Field(..., pattern="^(startup|small|medium|large|enterprise)$")
    industry: str
    country: str = Field(default="Saudi Arabia")
    city: str = Field(..., min_length=1, max_length=100)


class SignupResponse(BaseModel):
    """Response model for signup."""
    user: UserResponse
    organization: OrganizationResponse
    message: str = "Organization and user created successfully"


class LoginRequest(BaseModel):
    """Request model for login."""
    email: EmailStr
    password: str


@auth_router.post("/signup", response_model=SignupResponse)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
) -> SignupResponse:
    """
    Create a new organization and admin user.
    
    This endpoint is called by the frontend during signup to create
    the organization and user records in our database. The actual
    authentication user will be created by SuperTokens on the frontend.
    
    Process:
    1. Check if organization/user already exists
    2. Create organization record
    3. Create admin user record
    4. Return created entities
    
    Note: Password is not stored here - it's handled by SuperTokens
    """
    try:
        logger.info(f"Signup request for email: {request.email}, org: {request.organizationName}")
        
        # Check if user already exists
        existing_user = await user_crud.get_by_email(db, email=request.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
        
        # Map industry string to enum (you may need to adjust this based on your industry types)
        try:
            industry_type = IndustryType(request.industry.upper().replace(" ", "_"))
        except ValueError:
            # Default to a generic industry if not found
            industry_type = IndustryType.TECHNOLOGY
        
        # Create organization
        # Convert country name to ISO 2-letter code
        country_code = "SA" if request.country == "Saudi Arabia" else "SA"  # Default to SA
        
        org_data = {
            "name": request.organizationName,
            "email": request.email,
            "industry_type": industry_type,
            "company_size": request.organizationSize,
            "country": country_code,
            "city": request.city,
            "status": OrganizationStatus.TRIAL,
            "subscription_tier": "basic",
            "max_users": 10,
            "max_use_cases": 50,
            "max_storage_gb": 10,
            "allow_public_use_cases": True,
            "require_use_case_approval": False,
        }
        
        organization = await organization_crud.create(db, obj_in=org_data)
        logger.info(f"Created organization: {organization.id}")
        
        # Create admin user
        user_data = {
            "email": request.email,
            "first_name": request.firstName,
            "last_name": request.lastName,
            "organization_id": organization.id,
            "role": UserRole.ADMIN,
            "status": UserStatus.ACTIVE,
            "supertokens_user_id": f"st_{request.email.replace('@', '_').replace('.', '_')}",  # Temporary ID
            "email_notifications_enabled": True,
            "forum_notifications_enabled": True,
            "message_notifications_enabled": True,
        }
        
        user = await user_crud.create(db, obj_in=user_data)
        logger.info(f"Created admin user: {user.id} for organization: {organization.id}")
        
        return SignupResponse(
            user=UserResponse.model_validate(user),
            organization=OrganizationResponse.model_validate(organization)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create organization and user")


@auth_router.post("/signin")
async def signin(
    request: LoginRequest = Body(...),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate user signin.
    
    This endpoint is called to validate that a user exists in our database
    before SuperTokens handles the actual authentication.
    
    Note: Password validation is done by SuperTokens, not here.
    """
    try:
        logger.info(f"Signin request for email: {request.email}")
        
        # Check if user exists in our database
        user = await user_crud.get_by_email(db, email=request.email)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail="User account is not active"
            )
        
        # Return success (actual auth handled by SuperTokens)
        return {
            "status": "OK",
            "message": "User validated successfully",
            "user_id": str(user.id),
            "organization_id": str(user.organization_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@auth_router.post("/signout")
async def signout() -> Dict[str, str]:
    """
    Handle signout.
    
    This endpoint is called during signout. The actual session
    invalidation is handled by SuperTokens on the frontend.
    """
    logger.info("Signout request received")
    return {"status": "OK", "message": "Signed out successfully"}


@auth_router.get("/session/verify")
async def verify_session(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify if the current session is valid.
    
    This is a placeholder endpoint. With SuperTokens properly integrated,
    session verification would be handled by the SuperTokens middleware.
    """
    # This would normally check the SuperTokens session
    # For now, return a mock response
    return {
        "status": "OK",
        "session_valid": True,
        "message": "Session verification will be handled by SuperTokens"
    }


@auth_router.post("/refresh")
async def refresh_session() -> Dict[str, str]:
    """
    Refresh the current session.
    
    This is handled automatically by SuperTokens interceptors,
    but we provide this endpoint for completeness.
    """
    return {
        "status": "OK",
        "message": "Session refresh is handled by SuperTokens"
    }


@auth_router.get("/me")
async def get_current_user(
    session: SessionContainer = Depends(st_verify_session()),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user profile with organization details.
    
    This endpoint requires a valid SuperTokens session and returns
    the user's full profile including organization information.
    """
    try:
        user_id = session.get_user_id()
        logger.info(f"Fetching profile for SuperTokens user: {user_id}")
        
        # Get user from database by SuperTokens ID
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.supertokens_user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Try by email if SuperTokens ID doesn't match
            # This handles legacy users or mismatched IDs
            user_info = session.get_session_data_from_database()
            if user_info and "email" in user_info:
                result = await db.execute(
                    select(User).where(User.email == user_info["email"])
                )
                user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found in database: {user_id}")
            return {
                "status": "ERROR",
                "message": "User profile not found",
                "user": None
            }
        
        # Get organization
        from sqlalchemy import select
        org_result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = org_result.scalar_one_or_none()
        
        return {
            "status": "OK",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
                "isActive": user.status == UserStatus.ACTIVE,
                "createdAt": user.created_at.isoformat() if user.created_at else None,
            },
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "size": organization.company_size,
                "industry": organization.industry_type.value if hasattr(organization.industry_type, 'value') else organization.industry_type,
                "country": organization.country,
                "city": organization.city,
            } if organization else None
        }
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}", exc_info=True)
        return {
            "status": "ERROR",
            "message": "Failed to fetch user profile",
            "error": str(e)
        }


# Export the router
__all__ = ["auth_router"]