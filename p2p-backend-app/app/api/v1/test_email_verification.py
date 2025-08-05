"""Test endpoints for email verification functionality."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.email_verification import email_verification_service
from app.crud.user import user as user_crud
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class TestEmailVerificationRequest(BaseModel):
    """Request schema for testing email verification."""
    email: EmailStr


class TestVerifyTokenRequest(BaseModel):
    """Request schema for testing token verification."""
    token: str


@router.get("/info")
async def get_email_verification_info() -> Dict[str, Any]:
    """
    Get information about email verification testing endpoints.
    
    This endpoint provides documentation for all available test endpoints.
    """
    return {
        "message": "Email Verification Test Endpoints",
        "description": "Test endpoints for validating email verification functionality",
        "available_endpoints": {
            "GET /info": "Get information about test endpoints",
            "POST /send-test-verification": "Send verification email for test user",
            "GET /test-users": "Get list of test users for verification testing",
            "POST /verify-test-token": "Verify email using token (for testing)",
            "POST /check-test-status": "Check verification status for test user",
            "POST /resend-test-verification": "Resend verification for test user",
            "POST /revoke-test-tokens": "Revoke verification tokens for test user",
            "GET /verification-flow-test": "Complete verification flow test"
        },
        "test_users": [
            {
                "email": "test.login@company.sa",
                "description": "Main test user for verification"
            },
            {
                "email": "admin.test@company.sa", 
                "description": "Admin test user"
            }
        ],
        "security_notes": [
            "Test endpoints should be disabled in production",
            "These endpoints bypass normal authentication for testing",
            "Verification links and tokens are returned for testing purposes"
        ]
    }


@router.get("/test-users")
async def get_test_users_for_verification(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get list of test users available for email verification testing.
    """
    logger.info("Retrieving test users for email verification")
    
    try:
        # Get test users from database
        test_emails = [
            "test.login@company.sa",
            "admin.test@company.sa"
        ]
        
        users_info = []
        for email in test_emails:
            user = await user_crud.get_by_email(db, email=email)
            if user:
                users_info.append({
                    "id": str(user.id),
                    "email": user.email,
                    "supertokens_user_id": user.supertokens_user_id,
                    "email_verified": user.email_verified,
                    "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
                    "role": user.role,
                    "is_active": user.is_active
                })
        
        return {
            "success": True,
            "message": f"Found {len(users_info)} test users",
            "test_users": users_info
        }
        
    except Exception as e:
        logger.error(f"Error retrieving test users: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving test users")


@router.post("/send-test-verification")
async def send_test_verification_email(
    request: TestEmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send verification email for test user (bypasses normal auth).
    
    This endpoint is for testing purposes only.
    """
    logger.info(f"Sending test verification email for: {request.email}")
    
    try:
        # Get user by email
        user = await user_crud.get_by_email(db, email=request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Test user not found")
        
        # Send verification email
        result = await email_verification_service.send_verification_email(
            db=db,
            user_id=user.supertokens_user_id,
            email=request.email
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "test_user_id": str(user.id),
            "supertokens_user_id": user.supertokens_user_id,
            "email_sent": result.get("email_sent", False),
            "already_verified": result.get("already_verified", False),
            "verification_link": result.get("verification_link"),
            "token": result.get("token"),
            "testing_note": "This is a test endpoint - verification link and token are included for testing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test verification email: {e}")
        raise HTTPException(status_code=500, detail="Error sending test verification email")


@router.post("/verify-test-token")
async def verify_test_token(
    request: TestVerifyTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify email using token (test endpoint).
    
    This endpoint provides detailed response for testing verification.
    """
    logger.info("Processing test email verification with token")
    
    try:
        # Verify the token
        result = await email_verification_service.verify_email_token(
            db=db,
            token=request.token
        )
        
        if result["success"]:
            # Get updated user info
            user = await user_crud.get_by_supertokens_id(
                db, supertokens_user_id=result["user_id"]
            )
            
            user_info = None
            if user:
                user_info = {
                    "id": str(user.id),
                    "email": user.email,
                    "email_verified": user.email_verified,
                    "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
                    "role": user.role
                }
        
        return {
            "success": result["success"],
            "message": result["message"],
            "supertokens_user_id": result.get("user_id"),
            "verified_email": result.get("email"),
            "user_info": user_info,
            "testing_note": "This is a test endpoint - detailed user info included for testing"
        }
        
    except Exception as e:
        logger.error(f"Error verifying test token: {e}")
        raise HTTPException(status_code=500, detail="Error verifying test token")


@router.post("/check-test-status")
async def check_test_verification_status(
    request: TestEmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check verification status for test user.
    """
    logger.info(f"Checking test verification status for: {request.email}")
    
    try:
        # Get user by email
        user = await user_crud.get_by_email(db, email=request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Test user not found")
        
        # Check verification status
        result = await email_verification_service.check_verification_status(
            user_id=user.supertokens_user_id,
            email=request.email
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "is_verified": result.get("is_verified", False),
            "test_user_id": str(user.id),
            "supertokens_user_id": user.supertokens_user_id,
            "database_verified": user.email_verified,
            "database_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
            "testing_note": "Comparison between SuperTokens and database verification status"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking test verification status: {e}")
        raise HTTPException(status_code=500, detail="Error checking test verification status")


@router.post("/resend-test-verification")
async def resend_test_verification_email(
    request: TestEmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Resend verification email for test user.
    """
    logger.info(f"Resending test verification email for: {request.email}")
    
    try:
        # Get user by email
        user = await user_crud.get_by_email(db, email=request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Test user not found")
        
        # Resend verification email
        result = await email_verification_service.resend_verification_email(
            db=db,
            user_id=user.supertokens_user_id,
            email=request.email
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "test_user_id": str(user.id),
            "supertokens_user_id": user.supertokens_user_id,
            "email_sent": result.get("email_sent", False),
            "already_verified": result.get("already_verified", False),
            "verification_link": result.get("verification_link"),
            "token": result.get("token"),
            "testing_note": "Previous tokens were revoked, new verification link generated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending test verification email: {e}")
        raise HTTPException(status_code=500, detail="Error resending test verification email")


@router.post("/revoke-test-tokens")
async def revoke_test_verification_tokens(
    request: TestEmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Revoke verification tokens for test user.
    """
    logger.info(f"Revoking test verification tokens for: {request.email}")
    
    try:
        # Get user by email
        user = await user_crud.get_by_email(db, email=request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Test user not found")
        
        # Revoke verification tokens
        result = await email_verification_service.revoke_verification_tokens(
            user_id=user.supertokens_user_id,
            email=request.email
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "test_user_id": str(user.id),
            "supertokens_user_id": user.supertokens_user_id,
            "testing_note": "All verification tokens for this user have been revoked"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking test verification tokens: {e}")
        raise HTTPException(status_code=500, detail="Error revoking test verification tokens")


@router.get("/verification-flow-test")
async def complete_verification_flow_test(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Complete email verification flow test with multiple scenarios.
    
    This endpoint runs through the entire verification process for testing.
    """
    logger.info("Running complete email verification flow test")
    
    test_results = []
    test_email = "test.login@company.sa"
    
    try:
        # Get test user
        user = await user_crud.get_by_email(db, email=test_email)
        if not user:
            raise HTTPException(status_code=404, detail="Test user not found")
        
        # Test 1: Check initial verification status
        status_result = await email_verification_service.check_verification_status(
            user_id=user.supertokens_user_id,
            email=test_email
        )
        test_results.append({
            "test": "Initial verification status check",
            "success": status_result["success"],
            "result": status_result
        })
        
        # Test 2: Send verification email
        send_result = await email_verification_service.send_verification_email(
            db=db,
            user_id=user.supertokens_user_id,
            email=test_email
        )
        test_results.append({
            "test": "Send verification email",
            "success": send_result["success"],
            "result": send_result
        })
        
        verification_token = send_result.get("token")
        
        # Test 3: Verify email if token was generated
        if verification_token and send_result.get("email_sent"):
            verify_result = await email_verification_service.verify_email_token(
                db=db,
                token=verification_token
            )
            test_results.append({
                "test": "Verify email with token",
                "success": verify_result["success"],
                "result": verify_result
            })
            
            # Test 4: Check verification status after verification
            final_status_result = await email_verification_service.check_verification_status(
                user_id=user.supertokens_user_id,
                email=test_email
            )
            test_results.append({
                "test": "Final verification status check",
                "success": final_status_result["success"],
                "result": final_status_result
            })
        else:
            test_results.append({
                "test": "Verify email with token",
                "success": False,
                "result": {"message": "No token available for verification (email already verified or error)"}
            })
        
        # Test 5: Test invalid token
        invalid_token_result = await email_verification_service.verify_email_token(
            db=db,
            token="invalid_token_12345"
        )
        test_results.append({
            "test": "Verify with invalid token",
            "success": not invalid_token_result["success"],  # Success means it properly rejected invalid token
            "result": invalid_token_result
        })
        
        # Calculate overall success
        successful_tests = sum(1 for test in test_results if test["success"])
        total_tests = len(test_results)
        
        return {
            "overall_success": successful_tests == total_tests,
            "test_summary": f"{successful_tests}/{total_tests} tests passed",
            "test_user": {
                "id": str(user.id),
                "email": user.email,
                "supertokens_user_id": user.supertokens_user_id
            },
            "test_results": test_results,
            "testing_notes": [
                "This test runs through the complete verification flow",
                "Invalid token test should fail (which counts as success)",
                "Verification status is checked before and after verification",
                "Test includes both positive and negative scenarios"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in complete verification flow test: {e}")
        raise HTTPException(status_code=500, detail="Error running verification flow test")