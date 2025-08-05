"""Test endpoints for authentication flows."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.logging import get_logger
from app.db.session import get_db
from app.services.auth import auth_service
from app.models.enums import IndustryType

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