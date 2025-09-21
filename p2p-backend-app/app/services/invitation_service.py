"""
Invitation service for managing member invitations
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import EmailStr
from beanie import PydanticObjectId

from app.models.mongo_models import Invitation
from app.services.email_service import send_invitation_email
from app.core.config import settings

def generate_invite_token() -> str:
    """Generate a secure random token for invitation"""
    return secrets.token_urlsafe(32)

async def create_invitation(
    email: EmailStr,
    invited_by: Dict[str, Any],
    website_url: Optional[str] = None
) -> Invitation:
    """
    Create a new invitation and send email
    
    Args:
        email: Email address to invite
        invited_by: Dictionary with user info (id, email, name)
        website_url: Base URL for the signup link
    
    Returns:
        Created invitation document
    """
    # Generate unique token
    token = generate_invite_token()
    
    # Set expiration to 7 days from now
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    # Create invitation document
    invitation = Invitation(
        email=email,
        token=token,
        invited_by_id=invited_by["id"],
        invited_by_email=invited_by["email"],
        invited_by_name=invited_by.get("name", invited_by["email"]),
        expires_at=expires_at,
        used=False,
        created_at=datetime.utcnow()
    )
    
    # Save to database
    await invitation.create()

    # ALWAYS use production URL for invitation links
    # Hardcode the production IP for emails
    invite_link = f"http://15.185.167.236:5173/join?token={token}&email={email}"

    # Also generate localhost link for development testing (console only)
    localhost_link = f"http://localhost:5173/join?token={token}&email={email}"

    # Send invitation email
    try:
        await send_invitation_email(
            recipient_email=email,
            recipient_name="",  # We don't have the name yet
            invited_by_name=invited_by.get("name", invited_by["email"]),
            company_name=invited_by.get("company", "the organization"),
            invite_link=invite_link,
            expires_at=expires_at
        )
        print(f"✅ Invitation email sent successfully to {email} (redirected to test email in TEST MODE)")
        print(f"📧 Production link: {invite_link}")
        print(f"🔧 Development link (localhost): {localhost_link}")
    except Exception as e:
        print(f"⚠️ Failed to send email: {str(e)}")
        print(f"📧 Production link for {email}: {invite_link}")
        print(f"🔧 Development link (localhost): {localhost_link}")
    
    return invitation

async def validate_invitation(token: str) -> Optional[Invitation]:
    """
    Validate an invitation token
    
    Args:
        token: Invitation token to validate
    
    Returns:
        Invitation if valid and not expired, None otherwise
    """
    # Find invitation by token
    invitation = await Invitation.find_one(Invitation.token == token)
    
    if not invitation:
        return None
    
    # Check if already used
    if invitation.used:
        return None
    
    # Check if expired
    if datetime.utcnow() > invitation.expires_at:
        return None
    
    return invitation

async def mark_invitation_used(token: str) -> bool:
    """
    Mark an invitation as used
    
    Args:
        token: Invitation token
    
    Returns:
        True if successfully marked, False otherwise
    """
    invitation = await Invitation.find_one(Invitation.token == token)
    
    if not invitation:
        return False
    
    invitation.used = True
    invitation.used_at = datetime.utcnow()
    await invitation.save()
    
    return True

async def get_pending_invitations(invited_by_id: str) -> List[Invitation]:
    """
    Get all pending invitations sent by a user
    
    Args:
        invited_by_id: ID of the user who sent invitations
    
    Returns:
        List of pending invitations
    """
    invitations = await Invitation.find(
        Invitation.invited_by_id == invited_by_id,
        Invitation.used == False
    ).to_list()
    
    # Filter out expired invitations
    current_time = datetime.utcnow()
    valid_invitations = [
        inv for inv in invitations 
        if inv.expires_at > current_time
    ]
    
    return valid_invitations

async def get_all_invitations(invited_by_id: Optional[str] = None) -> List[Invitation]:
    """
    Get all invitations, optionally filtered by sender
    
    Args:
        invited_by_id: Optional ID to filter by sender
    
    Returns:
        List of all invitations
    """
    if invited_by_id:
        return await Invitation.find(
            Invitation.invited_by_id == invited_by_id
        ).sort("-created_at").to_list()
    
    return await Invitation.find_all().sort("-created_at").to_list()

async def cancel_invitation(invitation_id: str, user_id: str) -> bool:
    """
    Cancel (delete) an invitation
    
    Args:
        invitation_id: ID of the invitation to cancel
        user_id: ID of the user trying to cancel (must be the sender)
    
    Returns:
        True if successfully cancelled, False otherwise
    """
    try:
        invitation = await Invitation.get(invitation_id)
        
        if not invitation:
            return False
        
        # Check if user is the sender
        if invitation.invited_by_id != user_id:
            return False
        
        # Delete the invitation
        await invitation.delete()
        return True
        
    except Exception:
        return False