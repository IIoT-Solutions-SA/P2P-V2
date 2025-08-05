"""Test endpoints for authentication flows."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.logging import get_logger
from app.db.session import get_db
from app.services.auth import auth_service
from app.models.enums import IndustryType
from supertokens_python.recipe.session.asyncio import create_new_session, revoke_session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

logger = get_logger(__name__)
router = APIRouter()


class TestSignupRequest(BaseModel):
    """Test signup request schema."""
    email: EmailStr
    first_name: str
    last_name: str
    organization_name: str = None
    industry_type: IndustryType = IndustryType.OTHER


class TestSignupResponse(BaseModel):
    """Test signup response schema."""
    success: bool
    message: str
    user_id: str = None
    organization_id: str = None
    supertokens_user_id: str = None


class TestSigninRequest(BaseModel):
    """Test signin request schema."""
    email: EmailStr
    password: str


class TestSigninResponse(BaseModel):
    """Test signin response schema."""
    success: bool
    message: str
    user_id: str = None
    organization_id: str = None
    organization_name: str = None
    user_role: str = None


@router.post("/test-signup", response_model=TestSignupResponse)
async def test_signup_flow(
    signup_data: TestSignupRequest,
    db: AsyncSession = Depends(get_db)
) -> TestSignupResponse:
    """
    Test the signup flow without SuperTokens API validation.
    
    This endpoint directly tests our organization creation logic.
    """
    logger.info(f"Testing signup flow for: {signup_data.email}")
    
    try:
        # Generate a mock SuperTokens user ID for testing
        mock_supertokens_id = f"mock_st_{signup_data.email.replace('@', '_').replace('.', '_')}"
        
        # Generate organization name if not provided
        if not signup_data.organization_name:
            org_name = auth_service.extract_organization_name_from_email(signup_data.email)
        else:
            org_name = signup_data.organization_name
        
        # Create organization and user
        user, organization = await auth_service.create_organization_and_admin_user(
            db,
            supertokens_user_id=mock_supertokens_id,
            email=signup_data.email,
            first_name=signup_data.first_name,
            last_name=signup_data.last_name,
            organization_name=org_name,
            industry_type=signup_data.industry_type
        )
        
        logger.info(f"Test signup successful: User {user.id} in org {organization.id}")
        
        return TestSignupResponse(
            success=True,
            message="Signup flow completed successfully",
            user_id=str(user.id),
            organization_id=str(organization.id),
            supertokens_user_id=mock_supertokens_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in test signup: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in test signup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/test-signin", response_model=TestSigninResponse)
async def test_signin_flow(
    signin_data: TestSigninRequest,
    db: AsyncSession = Depends(get_db)
) -> TestSigninResponse:
    """
    Test the signin flow by directly calling auth service.
    
    This endpoint tests our signin logic by retrieving user/org data.
    """
    logger.info(f"Testing signin flow for: {signin_data.email}")
    
    try:
        # Get user with organization data by email
        user_data = await auth_service.get_user_by_email_with_organization(
            db, email=signin_data.email
        )
        
        if not user_data:
            logger.warning(f"No user found for email: {signin_data.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = user_data["user"]
        organization = user_data["organization"]
        
        # In a real implementation, we'd verify the password here
        # For now, we'll just simulate successful signin
        logger.info(f"Test signin successful: User {user.id} in org {organization.id}")
        
        return TestSigninResponse(
            success=True,
            message="Signin flow completed successfully",
            user_id=str(user.id),
            organization_id=str(organization.id),
            organization_name=organization.name,
            user_role=user.role
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in test signin: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session-info")
async def get_session_info(db: AsyncSession = Depends(get_db)):
    """
    Get current session information including user and organization data.
    
    This endpoint demonstrates session validation and data retrieval.
    """
    try:
        # For testing purposes, use a mock SuperTokens user ID
        # In real implementation, this would come from session
        supertokens_user_id = "mock_st_test_login_company_sa"
        logger.info(f"Session info demo for SuperTokens user: {supertokens_user_id}")
        
        # Get user with organization data
        user_data = await auth_service.get_user_with_organization(
            db, supertokens_user_id=supertokens_user_id
        )
        
        if not user_data:
            logger.warning(f"No user data found for SuperTokens ID: {supertokens_user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_data["user"]
        organization = user_data["organization"]
        permissions = user_data["permissions"]
        
        return {
            "session_valid": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "status": user.status
            },
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "status": organization.status,
                "industry_type": organization.industry_type
            },
            "permissions": permissions
        }
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout_user(session: SessionContainer = Depends(verify_session())):
    """
    Logout endpoint that revokes the current session.
    
    This endpoint demonstrates session cleanup and logout functionality.
    """
    try:
        # Get user info before logout for logging
        supertokens_user_id = session.get_user_id()
        session_handle = session.get_handle()
        
        logger.info(f"Logout requested for SuperTokens user: {supertokens_user_id}")
        
        # Revoke the current session
        await revoke_session(session_handle)
        
        logger.info(f"Session {session_handle} revoked successfully")
        
        return {
            "success": True,
            "message": "Logout successful",
            "session_revoked": True
        }
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/protected")
async def protected_endpoint(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Protected endpoint that requires valid session.
    
    This endpoint demonstrates session validation for protected routes.
    """
    try:
        # Get SuperTokens user ID from session
        supertokens_user_id = session.get_user_id()
        logger.info(f"Protected endpoint accessed by SuperTokens user: {supertokens_user_id}")
        
        # Get user with organization data
        user_data = await auth_service.get_user_with_organization(
            db, supertokens_user_id=supertokens_user_id
        )
        
        if not user_data:
            logger.warning(f"No user data found for SuperTokens ID: {supertokens_user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_data["user"]
        organization = user_data["organization"]
        
        return {
            "message": "Access granted to protected resource",
            "user_email": user.email,
            "organization_name": organization.name,
            "user_role": user.role,
            "session_valid": True
        }
        
    except Exception as e:
        logger.error(f"Error in protected endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")