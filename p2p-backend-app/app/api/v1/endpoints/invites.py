"""
API endpoints for invitation system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import EmailStr

from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationValidation,
    InvitationList
)
from app.services import invitation_service
from app.api.v1.endpoints.auth import get_current_user
from app.models.mongo_models import Invitation

router = APIRouter()

@router.post("/send", response_model=InvitationResponse)
async def send_invitation(
    invitation: InvitationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Send an invitation to a new member (admin only)
    """
    # Check if user is admin
    user_data = current_user.get("user", {})
    if user_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can send invitations"
        )
    
    # Check if email is already invited or exists
    existing = await Invitation.find_one(
        Invitation.email == invitation.email,
        Invitation.used == False
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email has already been invited"
        )
    
    # Create invitation
    try:
        user_data = current_user.get("user", {})

        # Get inviter's MongoDB profile to fetch company name and user's actual name
        from app.models.mongo_models import User as MongoUser
        inviter = await MongoUser.find_one(MongoUser.email == user_data.get("email", ""))

        company_name = "Company"  # Default
        inviter_name = user_data.get("email", "Admin")  # Default to email if no name found

        if inviter:
            # Get company name from MongoDB profile
            if hasattr(inviter, 'company') and inviter.company:
                company_name = inviter.company

            # Get the actual name from MongoDB profile
            if hasattr(inviter, 'name') and inviter.name:
                inviter_name = inviter.name

        invited_by = {
            "id": user_data.get("id", ""),
            "email": user_data.get("email", ""),
            "name": inviter_name,
            "company": company_name
        }

        # Use environment variable for website URL (dynamic based on environment)
        from app.core.config import settings
        website_url = settings.WEBSITE_DOMAIN

        result = await invitation_service.create_invitation(
            email=invitation.email,
            invited_by=invited_by,
            website_url=website_url
        )
        
        return InvitationResponse(
            id=str(result.id),
            email=result.email,
            token=result.token,
            invited_by_id=result.invited_by_id,
            invited_by_email=result.invited_by_email,
            invited_by_name=result.invited_by_name,
            expires_at=result.expires_at,
            used=result.used,
            used_at=result.used_at,
            created_at=result.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invitation: {str(e)}"
        )

@router.get("/validate/{token}", response_model=InvitationValidation)
async def validate_invitation(token: str):
    """
    Validate an invitation token and return organization data
    """
    invitation = await invitation_service.validate_invitation(token)
    
    if invitation:
        # Get the inviter's profile to fetch organization data
        from app.models.mongo_models import User as MongoUser
        inviter = await MongoUser.find_one(MongoUser.email == invitation.invited_by_email)
        
        # Default organization data
        organization_name = "Organization"
        industry = "Manufacturing"
        organization_size = "medium"
        city = "Riyadh"
        country = "Saudi Arabia"
        
        # Get actual organization data from inviter's profile
        if inviter:
            organization_name = inviter.company if hasattr(inviter, 'company') and inviter.company else organization_name
            industry = inviter.industry_sector if hasattr(inviter, 'industry_sector') and inviter.industry_sector else industry
            organization_size = inviter.company_size if hasattr(inviter, 'company_size') and inviter.company_size else organization_size
            city = inviter.location if hasattr(inviter, 'location') and inviter.location else city
            # Note: country is stored separately in some cases
            
        return InvitationValidation(
            valid=True,
            email=invitation.email,
            invited_by_name=invitation.invited_by_name,
            expires_at=invitation.expires_at,
            organization_name=organization_name,
            industry=industry,
            organization_size=organization_size,
            city=city,
            country=country
        )
    else:
        return InvitationValidation(
            valid=False,
            error="Invalid or expired invitation token"
        )

@router.get("/all", response_model=InvitationList)
async def get_all_invitations(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all invitations (admin only shows all, users show their own)
    """
    user_data = current_user.get("user", {})
    if user_data.get("role") == "admin":
        invitations = await invitation_service.get_all_invitations()
    else:
        invitations = await invitation_service.get_all_invitations(
            invited_by_id=user_data.get("id", "")
        )
    
    return InvitationList(
        invitations=[
            InvitationResponse(
                id=str(inv.id),
                email=inv.email,
                token=inv.token,
                invited_by_id=inv.invited_by_id,
                invited_by_email=inv.invited_by_email,
                invited_by_name=inv.invited_by_name,
                expires_at=inv.expires_at,
                used=inv.used,
                used_at=inv.used_at,
                created_at=inv.created_at
            )
            for inv in invitations
        ],
        total=len(invitations)
    )

@router.get("/pending", response_model=InvitationList)
async def get_pending_invitations(
    current_user: dict = Depends(get_current_user)
):
    """
    Get pending invitations sent by the current user
    """
    user_data = current_user.get("user", {})
    invitations = await invitation_service.get_pending_invitations(
        invited_by_id=user_data.get("id", "")
    )
    
    return InvitationList(
        invitations=[
            InvitationResponse(
                id=str(inv.id),
                email=inv.email,
                token=inv.token,
                invited_by_id=inv.invited_by_id,
                invited_by_email=inv.invited_by_email,
                invited_by_name=inv.invited_by_name,
                expires_at=inv.expires_at,
                used=inv.used,
                used_at=inv.used_at,
                created_at=inv.created_at
            )
            for inv in invitations
        ],
        total=len(invitations)
    )

@router.post("/mark-used/{token}")
async def mark_invitation_used(token: str):
    """
    Mark an invitation as used after successful signup
    """
    success = await invitation_service.mark_invitation_used(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already used"
        )
    
    return {"message": "Invitation marked as used"}

@router.delete("/{invitation_id}")
async def cancel_invitation(
    invitation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an invitation (only by the sender or admin)
    """
    user_data = current_user.get("user", {})
    success = await invitation_service.cancel_invitation(
        invitation_id=invitation_id,
        user_id=user_data.get("id", "")
    )
    
    if not success:
        # If user is admin, try to delete anyway
        if user_data.get("role") == "admin":
            try:
                invitation = await Invitation.get(invitation_id)
                if invitation:
                    await invitation.delete()
                    return {"message": "Invitation cancelled successfully"}
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or you don't have permission to cancel it"
        )
    
    return {"message": "Invitation cancelled successfully"}