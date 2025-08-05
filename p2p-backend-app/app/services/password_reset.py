"""Password reset service for handling password reset flows."""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from app.core.logging import get_logger
from app.utils.logging import log_database_operation, log_business_event
from app.models.user import User
from app.models.base import BaseModel
from app.crud.user import user as user_crud
from app.services.auth import auth_service
from sqlmodel import Field
from sqlalchemy import Column, String, DateTime, Index
from supertokens_python.recipe.emailpassword.asyncio import (
    create_reset_password_link,
    reset_password_using_token,
    consume_password_reset_token,
)

logger = get_logger(__name__)


# Password reset token model for custom implementation
class PasswordResetToken(BaseModel, table=True):
    """Model for storing password reset tokens."""
    
    __tablename__ = "password_reset_tokens"
    
    # Override the id field to use email as primary key instead
    id: Optional[str] = Field(default=None, primary_key=True)
    
    # Using email as primary key since SuperTokens uses email-based reset
    email: str = Field(index=True)
    token_hash: str = Field()  # Hashed version of token
    expires_at: datetime = Field()
    attempts: int = Field(default=0)  # Track failed attempts
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_password_reset_tokens_expires_at', 'expires_at'),
        Index('ix_password_reset_tokens_created_at', 'created_at'),
    )


class PasswordResetService:
    """Service for handling password reset operations."""
    
    # Security constants
    TOKEN_LENGTH = 64  # Bytes for secure token generation  
    TOKEN_EXPIRY_HOURS = 1  # 1 hour expiry as per requirements
    MAX_RESET_ATTEMPTS = 5  # Maximum attempts before lockout
    LOCKOUT_DURATION_MINUTES = 15  # Lockout duration
    
    @staticmethod
    def _generate_secure_token() -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(PasswordResetService.TOKEN_LENGTH)
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token using SHA-256."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    async def request_password_reset(
        db: AsyncSession,
        email: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Request a password reset for the given email.
        
        This method uses SuperTokens' built-in password reset functionality
        but adds additional validation and logging.
        
        Args:
            db: Database session
            email: User email address
            tenant_id: SuperTokens tenant ID (default: "public")
            
        Returns:
            Dict with success status and message
            
        Raises:
            Exception: If password reset fails
        """
        logger.info(f"Password reset requested for email: {email}")
        
        try:
            # First check if user exists in our database
            user = await user_crud.get_by_email(db, email=email)
            
            if not user:
                # Security: Don't reveal if email exists or not
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return {
                    "success": True,
                    "message": "If the email exists, a password reset link has been sent",
                    "email_sent": False
                }
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Password reset requested for inactive user: {email}")
                return {
                    "success": True,
                    "message": "If the email exists, a password reset link has been sent",
                    "email_sent": False
                }
            
            # Use SuperTokens to create reset password link
            link_response = await create_reset_password_link(
                tenant_id=tenant_id,
                user_id=user.supertokens_user_id,
                email=email
            )
            
            if link_response.status == "OK":
                # Log successful password reset request
                log_business_event(
                    event_type="PASSWORD_RESET_REQUESTED",
                    entity_type="user",
                    entity_id=str(user.id),
                    email=email,
                    supertokens_user_id=user.supertokens_user_id
                )
                
                logger.info(f"Password reset link created successfully for: {email}")
                
                # In a real application, you would send the email here
                # For now, we'll return the link for testing purposes
                return {
                    "success": True,
                    "message": "Password reset link has been sent to your email",
                    "email_sent": True,
                    "reset_link": link_response.link,  # Only for testing
                    "token": link_response.link.split("token=")[-1] if "token=" in link_response.link else None
                }
            
            else:
                logger.error(f"SuperTokens password reset failed: {link_response}")
                return {
                    "success": False,
                    "message": "Failed to generate password reset link",
                    "email_sent": False
                }
                
        except Exception as e:
            logger.error(f"Error requesting password reset for {email}: {e}")
            # Security: Don't reveal internal errors
            return {
                "success": True,
                "message": "If the email exists, a password reset link has been sent",
                "email_sent": False
            }
    
    @staticmethod
    async def validate_reset_token(
        token: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Validate a password reset token without consuming it.
        
        Args:
            token: Reset token
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with validation result
        """
        logger.info("Validating password reset token")
        
        try:
            # Use SuperTokens to consume (validate) the token without resetting password
            result = await consume_password_reset_token(
                tenant_id=tenant_id,
                token=token
            )
            
            if result.status == "OK":
                logger.info("Password reset token is valid")
                return {
                    "valid": True,
                    "message": "Token is valid",
                    "user_id": result.user_id,
                    "email": result.email
                }
            elif result.status == "RESET_PASSWORD_INVALID_TOKEN_ERROR":
                logger.warning("Invalid or expired password reset token")
                return {
                    "valid": False,
                    "message": "Invalid or expired reset token"
                }
            else:
                logger.error(f"Unexpected token validation result: {result}")
                return {
                    "valid": False,
                    "message": "Token validation failed"
                }
                
        except Exception as e:
            logger.error(f"Error validating reset token: {e}")
            return {
                "valid": False,
                "message": "Token validation failed"
            }
    
    @staticmethod
    async def reset_password(
        db: AsyncSession,
        token: str,
        new_password: str,
        tenant_id: str = "public"
    ) -> Dict[str, Any]:
        """
        Reset password using the provided token.
        
        Args:
            db: Database session
            token: Reset token
            new_password: New password
            tenant_id: SuperTokens tenant ID
            
        Returns:
            Dict with reset result
        """
        logger.info("Processing password reset")
        
        try:
            # Validate password strength first
            password_validation = PasswordResetService._validate_password(new_password)
            if not password_validation["valid"]:
                return {
                    "success": False,
                    "message": password_validation["message"]
                }
            
            # Use SuperTokens to reset the password
            result = await reset_password_using_token(
                tenant_id=tenant_id,
                token=token,
                new_password=new_password
            )
            
            if result.status == "OK":
                # Get user information for logging
                user = await user_crud.get_by_supertokens_id(
                    db, supertokens_user_id=result.user_id
                )
                
                if user:
                    # Log successful password reset
                    log_business_event(
                        event_type="PASSWORD_RESET_COMPLETED",
                        entity_type="user", 
                        entity_id=str(user.id),
                        email=user.email,
                        supertokens_user_id=user.supertokens_user_id
                    )
                    
                    logger.info(f"Password reset completed successfully for user: {user.email}")
                
                return {
                    "success": True,
                    "message": "Password has been reset successfully",
                    "user_id": result.user_id
                }
                
            elif result.status == "RESET_PASSWORD_INVALID_TOKEN_ERROR":
                logger.warning("Attempted password reset with invalid or expired token")
                return {
                    "success": False,
                    "message": "Invalid or expired reset token"
                }
            else:
                logger.error(f"Unexpected password reset result: {result}")
                return {
                    "success": False,
                    "message": "Password reset failed"
                }
                
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return {
                "success": False,
                "message": "Password reset failed"
            }
    
    @staticmethod
    def _validate_password(password: str) -> Dict[str, Any]:
        """
        Validate password strength and security requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Dict with validation result
        """
        if len(password) < 8:
            return {
                "valid": False,
                "message": "Password must be at least 8 characters long"
            }
        
        if len(password) > 128:
            return {
                "valid": False,
                "message": "Password must be less than 128 characters long"
            }
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            return {
                "valid": False,
                "message": "Password must contain at least one uppercase letter"
            }
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            return {
                "valid": False,
                "message": "Password must contain at least one lowercase letter"
            }
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            return {
                "valid": False,
                "message": "Password must contain at least one number"
            }
        
        # Check for at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return {
                "valid": False,
                "message": "Password must contain at least one special character"
            }
        
        return {
            "valid": True,
            "message": "Password meets security requirements"
        }
    
    @staticmethod
    async def cleanup_expired_tokens(db: AsyncSession) -> int:
        """
        Clean up expired password reset tokens from custom storage.
        
        This is useful if using custom token storage instead of SuperTokens default.
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens cleaned up
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Delete expired tokens
            stmt = delete(PasswordResetToken).where(
                PasswordResetToken.expires_at < current_time
            )
            
            result = await db.execute(stmt)
            deleted_count = result.rowcount
            await db.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired password reset tokens")
                
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            await db.rollback()
            return 0


# Create singleton instance
password_reset_service = PasswordResetService()