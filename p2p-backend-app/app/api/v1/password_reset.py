"""Password reset API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field

from app.core.logging import get_logger
from app.db.session import get_db
from app.services.password_reset import password_reset_service
from app.core.rbac import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address to send reset link to")


class PasswordResetRequestResponse(BaseModel):
    """Response schema for password reset request."""
    success: bool
    message: str
    email_sent: bool = False


class ValidateTokenSchema(BaseModel):
    """Schema for token validation request."""
    token: str = Field(..., description="Password reset token to validate")


class ValidateTokenResponse(BaseModel):
    """Response schema for token validation."""
    valid: bool
    message: str
    email: Optional[str] = None


class ResetPasswordSchema(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="New password (8-128 characters, must include uppercase, lowercase, number, and special character)"
    )
    confirm_password: str = Field(..., description="Confirm new password")

    def validate_passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class ResetPasswordResponse(BaseModel):
    """Response schema for password reset confirmation."""
    success: bool
    message: str


class PasswordStrengthResponse(BaseModel):
    """Response schema for password strength validation."""
    valid: bool
    message: str
    requirements: dict = {
        "min_length": "At least 8 characters",
        "max_length": "Less than 128 characters", 
        "uppercase": "At least one uppercase letter",
        "lowercase": "At least one lowercase letter",
        "number": "At least one number",
        "special_char": "At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    }


@router.post("/request-reset", response_model=PasswordResetRequestResponse)
async def request_password_reset(
    request: PasswordResetRequestSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset link to be sent to the provided email address.
    
    This endpoint will always return success to prevent email enumeration attacks.
    If the email exists and the user is active, a reset link will be sent.
    """
    logger.info(f"Password reset requested for email: {request.email}")
    
    try:
        result = await password_reset_service.request_password_reset(
            db=db,
            email=request.email
        )
        
        return PasswordResetRequestResponse(
            success=result["success"],
            message=result["message"],
            email_sent=result.get("email_sent", False)
        )
        
    except Exception as e:
        logger.error(f"Error processing password reset request: {e}")
        # Return generic success message for security
        return PasswordResetRequestResponse(
            success=True,
            message="If the email exists, a password reset link has been sent",
            email_sent=False
        )


@router.post("/validate-token", response_model=ValidateTokenResponse)
async def validate_reset_token(request: ValidateTokenSchema):
    """
    Validate a password reset token without consuming it.
    
    This endpoint can be used to check if a token is valid before
    showing the password reset form.
    """
    logger.info("Validating password reset token")
    
    try:
        result = await password_reset_service.validate_reset_token(
            token=request.token
        )
        
        return ValidateTokenResponse(
            valid=result["valid"],
            message=result["message"],
            email=result.get("email")
        )
        
    except Exception as e:
        logger.error(f"Error validating reset token: {e}")
        return ValidateTokenResponse(
            valid=False,
            message="Token validation failed"
        )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using a valid reset token.
    
    This endpoint validates the token and updates the user's password
    if the token is valid and the new password meets security requirements.
    """
    logger.info("Processing password reset")
    
    # Validate passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    try:
        result = await password_reset_service.reset_password(
            db=db,
            token=request.token,
            new_password=request.new_password
        )
        
        if result["success"]:
            return ResetPasswordResponse(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/validate-password-strength", response_model=PasswordStrengthResponse)
async def validate_password_strength(password: str):
    """
    Validate password strength without storing it.
    
    This endpoint can be used by the frontend to provide real-time
    password strength feedback to users.
    """
    try:
        result = password_reset_service._validate_password(password)
        
        return PasswordStrengthResponse(
            valid=result["valid"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error(f"Error validating password strength: {e}")
        return PasswordStrengthResponse(
            valid=False,
            message="Password validation failed"
        )


@router.get("/password-requirements")
async def get_password_requirements():
    """
    Get password security requirements.
    
    This endpoint returns the current password requirements
    that users must meet when setting a new password.
    """
    return {
        "requirements": {
            "min_length": 8,
            "max_length": 128,
            "must_contain": [
                "At least one uppercase letter (A-Z)",
                "At least one lowercase letter (a-z)", 
                "At least one number (0-9)",
                "At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
            ]
        },
        "examples": {
            "valid": ["MySecure123!", "P@ssw0rd2024", "Strong#Pass1"],
            "invalid": [
                {"password": "password", "reason": "No uppercase, numbers, or special characters"},
                {"password": "PASSWORD", "reason": "No lowercase, numbers, or special characters"},
                {"password": "Pass123", "reason": "No special characters"},
                {"password": "Pass!", "reason": "No numbers"}
            ]
        }
    }


# Test endpoints for development (should be removed in production)
@router.post("/test-request-reset")
async def test_request_password_reset(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    """
    Test endpoint for password reset request - returns reset link.
    
    WARNING: This endpoint should only be used in development/testing.
    It exposes the reset link which should normally be sent via email.
    """
    logger.warning(f"TEST: Password reset requested for: {email}")
    
    result = await password_reset_service.request_password_reset(
        db=db,
        email=email
    )
    
    return {
        "success": result["success"],
        "message": result["message"],
        "email_sent": result.get("email_sent", False),
        "reset_link": result.get("reset_link"),  # Only in test mode
        "token": result.get("token")  # Only in test mode
    }


@router.get("/user-password-reset-status")
async def get_user_password_reset_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get password reset status for the current user.
    
    This endpoint provides information about recent password reset activity
    for the authenticated user.
    """
    logger.info(f"Getting password reset status for user: {current_user.email}")
    
    return {
        "user_email": current_user.email,
        "can_request_reset": True,
        "message": "User can request password reset",
        "last_password_change": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "account_status": current_user.status.value if current_user.status else "unknown"
    }