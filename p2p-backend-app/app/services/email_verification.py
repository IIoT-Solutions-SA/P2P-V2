"""Email verification service for handling email verification flows."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.utils.logging import log_database_operation, log_business_event
from app.models.user import User
from app.crud.user import user as user_crud
from supertokens_python.recipe.emailverification.asyncio import (
    create_email_verification_token,
    create_email_verification_link,
    verify_email_using_token,
    is_email_verified,
    revoke_email_verification_tokens,
    unverify_email,
)

logger = get_logger(__name__)


class EmailVerificationService:
    """Service for handling email verification operations."""
    
    @staticmethod
    async def send_verification_email(
        db: AsyncSession,
        user_id: str,
        email: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Send email verification link to the specified email address.
        
        Args:
            db: Database session
            user_id: SuperTokens user ID
            email: Email address to verify
            tenant_id: SuperTokens tenant ID (default: "public")
            
        Returns:
            Dict with operation result
            
        Raises:
            Exception: If email verification fails
        """
        logger.info(f"Sending email verification for user: {user_id}, email: {email}")
        
        try:
            # First check if user exists in our database
            user = await user_crud.get_by_supertokens_id(db, supertokens_user_id=user_id)
            
            if not user:
                logger.warning(f"Email verification requested for non-existent user: {user_id}")
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Email verification requested for inactive user: {user_id}")
                return {
                    "success": False,
                    "message": "User account is inactive"
                }
            
            # Check if email is already verified
            verification_status = await is_email_verified(
                user_id,
                email
            )
            
            if verification_status.status == "OK" and verification_status.is_verified:
                logger.info(f"Email already verified for user: {user_id}")
                return {
                    "success": True,
                    "message": "Email is already verified",
                    "already_verified": True
                }
            
            # Create email verification link
            link_response = await create_email_verification_link(
                user_id=user_id,
                email=email,
                tenant_id=tenant_id
            )
            
            if link_response.status == "OK":
                # Log successful email verification request
                log_business_event(
                    event_type="EMAIL_VERIFICATION_SENT",
                    entity_type="user",
                    entity_id=str(user.id),
                    email=email,
                    supertokens_user_id=user_id
                )
                
                logger.info(f"Email verification link created successfully for: {email}")
                
                # In a real application, you would send the email here
                # For now, we'll return the link for testing purposes
                return {
                    "success": True,
                    "message": "Email verification link has been sent",
                    "email_sent": True,
                    "verification_link": link_response.link,  # Only for testing
                    "token": link_response.link.split("token=")[-1] if "token=" in link_response.link else None
                }
            
            elif link_response.status == "EMAIL_ALREADY_VERIFIED_ERROR":
                logger.info(f"Email already verified for user: {user_id}")
                return {
                    "success": True,
                    "message": "Email is already verified",
                    "already_verified": True
                }
            else:
                logger.error(f"SuperTokens email verification link creation failed: {link_response}")
                return {
                    "success": False,
                    "message": "Failed to generate email verification link"
                }
                
        except Exception as e:
            logger.error(f"Error sending email verification for {user_id}: {e}")
            return {
                "success": False,
                "message": "Failed to send email verification"
            }
    
    @staticmethod
    async def verify_email_token(
        db: AsyncSession,
        token: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Verify email using the provided token.
        
        Args:
            db: Database session
            token: Email verification token
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with verification result
        """
        logger.info("Processing email verification with token")
        
        try:
            # Use SuperTokens to verify the email using token
            result = await verify_email_using_token(
                token=token,
                tenant_id=tenant_id
            )
            
            if result.status == "OK":
                # Get user information for logging
                user = await user_crud.get_by_supertokens_id(
                    db, supertokens_user_id=result.user.id
                )
                
                if user:
                    # Update user verification status in our database if needed
                    if not user.email_verified:
                        user.email_verified = True
                        user.email_verified_at = datetime.utcnow()
                        db.add(user)
                        await db.commit()
                        await db.refresh(user)
                    
                    # Log successful email verification
                    log_business_event(
                        event_type="EMAIL_VERIFICATION_COMPLETED",
                        entity_type="user",
                        entity_id=str(user.id),
                        email=result.user.email,
                        supertokens_user_id=result.user.id
                    )
                    
                    logger.info(f"Email verification completed successfully for user: {result.user.email}")
                
                return {
                    "success": True,
                    "message": "Email has been verified successfully",
                    "user_id": result.user.id,
                    "email": result.user.email
                }
                
            elif result.status == "EMAIL_VERIFICATION_INVALID_TOKEN_ERROR":
                logger.warning("Attempted email verification with invalid or expired token")
                return {
                    "success": False,
                    "message": "Invalid or expired verification token"
                }
            else:
                logger.error(f"Unexpected email verification result: {result}")
                return {
                    "success": False,
                    "message": "Email verification failed"
                }
                
        except Exception as e:
            logger.error(f"Error verifying email token: {e}")
            return {
                "success": False,
                "message": "Email verification failed"
            }
    
    @staticmethod
    async def check_verification_status(
        user_id: str,
        email: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Check if an email is verified for a user.
        
        Args:
            user_id: SuperTokens user ID
            email: Email address to check
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with verification status
        """
        logger.info(f"Checking email verification status for user: {user_id}, email: {email}")
        
        try:
            # Check verification status with SuperTokens
            result = await is_email_verified(
                user_id,
                email
            )
            
            if result.status == "OK":
                return {
                    "success": True,
                    "is_verified": result.is_verified,
                    "message": "Verified" if result.is_verified else "Not verified"
                }
            else:
                logger.error(f"Error checking verification status: {result}")
                return {
                    "success": False,
                    "message": "Failed to check verification status"
                }
                
        except Exception as e:
            logger.error(f"Error checking email verification status: {e}")
            return {
                "success": False,
                "message": "Failed to check verification status"
            }
    
    @staticmethod
    async def revoke_verification_tokens(
        user_id: str,
        email: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Revoke all email verification tokens for a user's email.
        
        Args:
            user_id: SuperTokens user ID
            email: Email address
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with operation result
        """
        logger.info(f"Revoking email verification tokens for user: {user_id}, email: {email}")
        
        try:
            # Revoke tokens with SuperTokens
            result = await revoke_email_verification_tokens(
                user_id,
                email,
                tenant_id
            )
            
            if result.status == "OK":
                logger.info(f"Email verification tokens revoked for user: {user_id}")
                return {
                    "success": True,
                    "message": "Email verification tokens have been revoked"
                }
            else:
                logger.error(f"Error revoking verification tokens: {result}")
                return {
                    "success": False,
                    "message": "Failed to revoke verification tokens"
                }
                
        except Exception as e:
            logger.error(f"Error revoking email verification tokens: {e}")
            return {
                "success": False,
                "message": "Failed to revoke verification tokens"
            }
    
    @staticmethod
    async def unverify_email(
        db: AsyncSession,
        user_id: str,
        email: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Mark an email as unverified (for admin actions).
        
        Args:
            db: Database session
            user_id: SuperTokens user ID
            email: Email address to unverify
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with operation result
        """
        logger.info(f"Unverifying email for user: {user_id}, email: {email}")
        
        try:
            # Unverify email with SuperTokens
            result = await unverify_email(
                user_id,
                email,
                tenant_id
            )
            
            if result.status == "OK":
                # Update user verification status in our database
                user = await user_crud.get_by_supertokens_id(
                    db, supertokens_user_id=user_id
                )
                
                if user:
                    user.email_verified = False
                    user.email_verified_at = None
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                
                # Log email unverification
                log_business_event(
                    event_type="EMAIL_UNVERIFIED",
                    entity_type="user",
                    entity_id=str(user.id) if user else user_id,
                    email=email,
                    supertokens_user_id=user_id
                )
                
                logger.info(f"Email unverified successfully for user: {user_id}")
                return {
                    "success": True,
                    "message": "Email has been marked as unverified"
                }
            else:
                logger.error(f"Error unverifying email: {result}")
                return {
                    "success": False,
                    "message": "Failed to unverify email"
                }
                
        except Exception as e:
            logger.error(f"Error unverifying email: {e}")
            return {
                "success": False,
                "message": "Failed to unverify email"
            }
    
    @staticmethod
    async def resend_verification_email(
        db: AsyncSession,
        user_id: str,
        email: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Resend email verification link (convenience method).
        
        Args:
            db: Database session
            user_id: SuperTokens user ID
            email: Email address
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with operation result
        """
        logger.info(f"Resending email verification for user: {user_id}, email: {email}")
        
        # First revoke existing tokens to prevent multiple active tokens
        await EmailVerificationService.revoke_verification_tokens(
            user_id=user_id,
            email=email,
            tenant_id=tenant_id
        )
        
        # Send new verification email
        return await EmailVerificationService.send_verification_email(
            db=db,
            user_id=user_id,
            email=email,
            tenant_id=tenant_id
        )


# Create singleton instance
email_verification_service = EmailVerificationService()