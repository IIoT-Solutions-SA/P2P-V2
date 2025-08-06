"""Token service for generating secure tokens for invitations and other purposes."""

import secrets
import hashlib
import hmac
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TokenService:
    """Service for generating and validating secure tokens."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
    
    def generate_invitation_token(
        self,
        email: str,
        organization_id: str,
        expires_in_days: int = 7
    ) -> str:
        """Generate a secure invitation token."""
        # Create payload with email, org, and expiry
        payload = {
            "email": email,
            "organization_id": str(organization_id),
            "expires_at": (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat(),
            "type": "invitation",
            "random": secrets.token_hex(16)  # Add randomness
        }
        
        # Convert to JSON and encode
        payload_json = json.dumps(payload, sort_keys=True)
        payload_bytes = payload_json.encode('utf-8')
        
        # Create signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).digest()
        
        # Combine payload and signature
        token_data = payload_bytes + b'.' + signature
        
        # Base64 encode for URL safety
        token = base64.urlsafe_b64encode(token_data).decode('utf-8').rstrip('=')
        
        logger.debug(f"Generated invitation token for {email}")
        return token
    
    def validate_invitation_token(
        self, 
        token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate an invitation token and return payload if valid."""
        try:
            # Add padding if needed
            token += '=' * (4 - len(token) % 4)
            
            # Decode from base64
            token_data = base64.urlsafe_b64decode(token.encode('utf-8'))
            
            # Split payload and signature
            parts = token_data.split(b'.')
            if len(parts) != 2:
                logger.warning("Invalid token format - missing signature")
                return None
            
            payload_bytes, signature = parts
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).digest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid token signature")
                return None
            
            # Parse payload
            payload_json = payload_bytes.decode('utf-8')
            payload = json.loads(payload_json)
            
            # Check token type
            if payload.get('type') != 'invitation':
                logger.warning(f"Invalid token type: {payload.get('type')}")
                return None
            
            # Check expiry
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.utcnow() > expires_at:
                logger.info("Token has expired")
                return None
            
            logger.debug(f"Token validated successfully for {payload['email']}")
            return payload
            
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return None
    
    def generate_simple_token(self, length: int = 32) -> str:
        """Generate a simple random token."""
        return secrets.token_urlsafe(length)
    
    def generate_numeric_token(self, length: int = 6) -> str:
        """Generate a numeric token (for phone verification, etc.)."""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    def hash_token(self, token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(
            (token + self.secret_key).encode('utf-8')
        ).hexdigest()
    
    def verify_hashed_token(self, token: str, hashed_token: str) -> bool:
        """Verify a token against its hash."""
        return hmac.compare_digest(
            self.hash_token(token),
            hashed_token
        )
    
    def generate_password_reset_token(
        self,
        user_id: str,
        email: str,
        expires_in_hours: int = 1
    ) -> str:
        """Generate a password reset token."""
        payload = {
            "user_id": str(user_id),
            "email": email,
            "expires_at": (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat(),
            "type": "password_reset",
            "random": secrets.token_hex(16)
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        payload_bytes = payload_json.encode('utf-8')
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).digest()
        
        token_data = payload_bytes + b'.' + signature
        token = base64.urlsafe_b64encode(token_data).decode('utf-8').rstrip('=')
        
        logger.debug(f"Generated password reset token for user {user_id}")
        return token
    
    def validate_password_reset_token(
        self, 
        token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate a password reset token."""
        payload = self.validate_invitation_token(token)  # Same validation logic
        
        if payload and payload.get('type') == 'password_reset':
            return payload
        
        return None
    
    def generate_api_key(self, prefix: str = "p2p") -> str:
        """Generate an API key with prefix."""
        key_part = secrets.token_urlsafe(32)
        return f"{prefix}_{key_part}"
    
    def is_token_format_valid(self, token: str) -> bool:
        """Check if token has valid format (basic check)."""
        try:
            # Should be base64-like string
            if not token or len(token) < 20:
                return False
            
            # Try to decode
            token += '=' * (4 - len(token) % 4)
            base64.urlsafe_b64decode(token.encode('utf-8'))
            return True
            
        except Exception:
            return False


# Create singleton instance
token_service = TokenService()