"""Email verification API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.email_verification import email_verification_service
from app.core.rbac import get_current_user_with_permissions
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# Request/Response schemas
class SendVerificationEmailRequest(BaseModel):
    """Request schema for sending verification email."""
    email: EmailStr
    user_id: str


class VerifyEmailRequest(BaseModel):
    """Request schema for verifying email with token."""
    token: str


class CheckVerificationRequest(BaseModel):
    """Request schema for checking verification status."""
    email: EmailStr
    user_id: str


class RevokeTokensRequest(BaseModel):
    """Request schema for revoking verification tokens."""
    email: EmailStr
    user_id: str


class UnverifyEmailRequest(BaseModel):
    """Request schema for unverifying email."""
    email: EmailStr
    user_id: str


@router.post("/send-verification")
async def send_verification_email(
    request: SendVerificationEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_with_permissions)
) -> Dict[str, Any]:
    """
    Send email verification link to user's email address.
    
    Requires user to be authenticated.
    """
    logger.info(f"Email verification requested for user: {request.user_id}")
    
    try:
        # Users can only request verification for their own email
        # Admins can request verification for any user
        if (current_user["supertokens_user_id"] != request.user_id and 
            "MANAGE_USERS" not in current_user.get("permissions", [])):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to send verification email for this user"
            )
        
        result = await email_verification_service.send_verification_email(
            db=db,
            user_id=request.user_id,
            email=request.email
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "email_sent": result.get("email_sent", False),
                "already_verified": result.get("already_verified", False),
                # Include verification link and token for testing (remove in production)
                "verification_link": result.get("verification_link"),
                "token": result.get("token")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send verification email endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify")
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify email address using verification token.
    
    This endpoint does not require authentication as the token provides authorization.
    """
    logger.info("Email verification with token requested")
    
    try:
        result = await email_verification_service.verify_email_token(
            db=db,
            token=request.token
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "user_id": result.get("user_id"),
                "email": result.get("email")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify email endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/check-status")
async def check_verification_status(
    request: CheckVerificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_with_permissions)
) -> Dict[str, Any]:
    """
    Check email verification status for a user.
    
    Requires user to be authenticated.
    """
    logger.info(f"Email verification status check for user: {request.user_id}")
    
    try:
        # Users can only check their own verification status
        # Admins can check any user's status
        if (current_user["supertokens_user_id"] != request.user_id and 
            "VIEW_USERS" not in current_user.get("permissions", [])):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to check verification status for this user"
            )
        
        result = await email_verification_service.check_verification_status(
            user_id=request.user_id,
            email=request.email
        )
        
        if result["success"]:
            return {
                "success": True,
                "is_verified": result["is_verified"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check verification status endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/resend")
async def resend_verification_email(
    request: SendVerificationEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_with_permissions)
) -> Dict[str, Any]:
    """
    Resend email verification link to user's email address.
    
    This revokes any existing tokens and sends a new verification email.
    """
    logger.info(f"Email verification resend requested for user: {request.user_id}")
    
    try:
        # Users can only resend verification for their own email
        # Admins can resend verification for any user
        if (current_user["supertokens_user_id"] != request.user_id and 
            "MANAGE_USERS" not in current_user.get("permissions", [])):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to resend verification email for this user"
            )
        
        result = await email_verification_service.resend_verification_email(
            db=db,
            user_id=request.user_id,
            email=request.email
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "email_sent": result.get("email_sent", False),
                "already_verified": result.get("already_verified", False),
                # Include verification link and token for testing (remove in production)
                "verification_link": result.get("verification_link"),
                "token": result.get("token")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resend verification email endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/revoke-tokens")
async def revoke_verification_tokens(
    request: RevokeTokensRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_with_permissions)
) -> Dict[str, Any]:
    """
    Revoke all email verification tokens for a user's email.
    
    Requires admin permissions or user must be requesting for their own account.
    """
    logger.info(f"Email verification token revocation requested for user: {request.user_id}")
    
    try:
        # Users can only revoke tokens for their own email
        # Admins can revoke tokens for any user
        if (current_user["supertokens_user_id"] != request.user_id and 
            "MANAGE_USERS" not in current_user.get("permissions", [])):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to revoke verification tokens for this user"
            )
        
        result = await email_verification_service.revoke_verification_tokens(
            user_id=request.user_id,
            email=request.email
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in revoke verification tokens endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/unverify")
async def unverify_email(
    request: UnverifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_with_permissions)
) -> Dict[str, Any]:
    """
    Mark an email as unverified (admin action).
    
    Requires MANAGE_USERS permission.
    """
    logger.info(f"Email unverification requested for user: {request.user_id}")
    
    try:
        # Only admins can unverify emails
        if "MANAGE_USERS" not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to unverify user emails"
            )
        
        result = await email_verification_service.unverify_email(
            db=db,
            user_id=request.user_id,
            email=request.email
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in unverify email endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requirements")
async def get_verification_requirements() -> Dict[str, Any]:
    """
    Get email verification requirements and information.
    
    This endpoint provides information about the email verification process.
    """
    return {
        "verification_process": {
            "description": "Email verification ensures user email addresses are valid and accessible",
            "steps": [
                "1. User requests email verification",
                "2. Verification link is sent to user's email",
                "3. User clicks verification link",
                "4. Email is marked as verified"
            ],
            "security_features": [
                "Secure token generation",
                "Token expiration for security",
                "Single-use tokens",
                "Email ownership validation"
            ]
        },
        "token_properties": {
            "expiry_time": "24 hours",
            "single_use": True,
            "secure_generation": True
        },
        "requirements": {
            "authentication": "Required for sending verification emails",
            "authorization": "Users can verify their own emails, admins can manage all verifications",
            "rate_limiting": "Recommended in production"
        },
        "endpoints": {
            "send_verification": "POST /send-verification - Send verification email",
            "verify": "POST /verify - Verify email with token",
            "check_status": "POST /check-status - Check verification status",
            "resend": "POST /resend - Resend verification email",
            "revoke_tokens": "POST /revoke-tokens - Revoke verification tokens",
            "unverify": "POST /unverify - Mark email as unverified (admin only)"
        }
    }