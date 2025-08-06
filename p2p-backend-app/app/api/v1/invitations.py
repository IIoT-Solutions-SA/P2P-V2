"""User invitation system API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
# Temporarily use mock authentication
from app.api.v1.users import get_current_user, get_mock_admin_user
from app.models.user import User
from app.models.organization import Organization
from app.models.invitation import UserInvitation
from app.models.enums import InvitationStatus, UserRole
from app.schemas.invitation import (
    InvitationCreate,
    InvitationSend,
    InvitationResponse,
    InvitationAccept,
    InvitationListResponse,
    InvitationStats,
    InvitationToken,
    BulkInvitationCreate,
    BulkInvitationResponse
)
from app.schemas.user import UserCreateInternal, User as UserResponse
from app.crud.invitation import invitation
from app.crud.user import user
from app.services.email import email_service
from app.services.token import token_service
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/send",
    response_model=InvitationResponse,
    status_code=201,
    summary="Send user invitation",
    description="Send an invitation to join the organization (admin only)"
)
async def send_invitation(
    invitation_data: InvitationSend = Body(...),
    current_user: User = Depends(get_mock_admin_user),
    db: AsyncSession = Depends(get_db)
) -> InvitationResponse:
    """Send an invitation to a user to join the organization.
    
    Only organization admins can send invitations.
    The invitation will be sent to the specified email address with a secure token.
    
    **Restrictions:**
    - Only admins can send invitations
    - Cannot invite existing users
    - Cannot invite to different organizations
    - Email must be unique within the organization
    """
    try:
        # Check if user already exists
        existing_user = await user.get_by_email(db, email=invitation_data.email)
        if existing_user:
            # Check if in same organization
            if existing_user.organization_id == current_user.organization_id:
                raise HTTPException(
                    status_code=400, 
                    detail="User is already a member of this organization"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="User already exists on the platform"
                )
        
        # Check for existing pending invitation
        existing_invitation = await invitation.check_duplicate_invitation(
            db, invitation_data.email, current_user.organization_id
        )
        if existing_invitation:
            if existing_invitation.is_pending:
                raise HTTPException(
                    status_code=400,
                    detail="A pending invitation already exists for this email address"
                )
        
        # Generate secure invitation token
        token = token_service.generate_invitation_token(
            email=invitation_data.email,
            organization_id=str(current_user.organization_id),
            expires_in_days=invitation_data.expires_in_days
        )
        
        # Create invitation record
        invitation_record = await invitation.create_invitation(
            db,
            email=invitation_data.email,
            organization_id=current_user.organization_id,
            invited_by=current_user.id,
            token=token,
            invitation_data={
                "invited_role": invitation_data.invited_role,
                "first_name": invitation_data.first_name,
                "last_name": invitation_data.last_name,
                "job_title": invitation_data.job_title,
                "department": invitation_data.department,
                "personal_message": invitation_data.personal_message,
                "expires_in_days": invitation_data.expires_in_days
            }
        )
        
        # Send invitation email if requested
        if invitation_data.send_welcome_email:
            # Get organization details
            org_result = await db.execute(
                select(Organization).where(Organization.id == current_user.organization_id)
            )
            organization = org_result.scalar_one()
            
            # Generate invitation URL
            invitation_url = f"{settings.FRONTEND_URL}/accept-invitation?token={token}"
            
            # Send email
            email_sent = await email_service.send_invitation_email(
                invitation=invitation_record,
                organization=organization,
                inviter=current_user,
                invitation_url=invitation_url
            )
            
            if not email_sent:
                logger.warning(f"Failed to send invitation email to {invitation_data.email}")
        
        logger.info(
            f"Admin {current_user.id} sent invitation to {invitation_data.email} "
            f"for role {invitation_data.invited_role}"
        )
        
        # Create response with computed properties
        return InvitationResponse(
            id=invitation_record.id,
            email=invitation_record.email,
            token=invitation_record.token,
            organization_id=invitation_record.organization_id,
            invited_role=invitation_record.invited_role,
            invited_by=invitation_record.invited_by,
            status=invitation_record.status,
            first_name=invitation_record.first_name,
            last_name=invitation_record.last_name,
            job_title=invitation_record.job_title,
            department=invitation_record.department,
            personal_message=invitation_record.personal_message,
            expires_at=invitation_record.expires_at,
            accepted_at=invitation_record.accepted_at,
            created_at=invitation_record.created_at,
            updated_at=invitation_record.updated_at,
            is_expired=invitation_record.is_expired,
            is_pending=invitation_record.is_pending,
            days_until_expiry=invitation_record.days_until_expiry
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending invitation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send invitation")


@router.get(
    "/validate/{token}",
    response_model=InvitationToken,
    summary="Validate invitation token",
    description="Validate an invitation token and return invitation details"
)
async def validate_invitation_token(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> InvitationToken:
    """Validate an invitation token.
    
    This endpoint is public (no authentication required) to allow
    users to check invitation validity before account creation.
    """
    try:
        # Validate token format and signature
        token_payload = token_service.validate_invitation_token(token)
        if not token_payload:
            return InvitationToken(
                token=token,
                is_valid=False,
                error_message="Invalid or malformed token"
            )
        
        # Get invitation from database
        invitation_record = await invitation.get_by_token(db, token)
        if not invitation_record:
            return InvitationToken(
                token=token,
                is_valid=False,
                error_message="Invitation not found"
            )
        
        # Check if invitation is still valid
        if not invitation_record.is_pending:
            status_messages = {
                InvitationStatus.ACCEPTED: "This invitation has already been accepted",
                InvitationStatus.EXPIRED: "This invitation has expired",
                InvitationStatus.CANCELLED: "This invitation has been cancelled"
            }
            return InvitationToken(
                token=token,
                is_valid=False,
                error_message=status_messages.get(
                    invitation_record.status, 
                    "This invitation is no longer valid"
                )
            )
        
        # Create successful response
        invitation_response = InvitationResponse(
            id=invitation_record.id,
            email=invitation_record.email,
            token=invitation_record.token,
            organization_id=invitation_record.organization_id,
            invited_role=invitation_record.invited_role,
            invited_by=invitation_record.invited_by,
            status=invitation_record.status,
            first_name=invitation_record.first_name,
            last_name=invitation_record.last_name,
            job_title=invitation_record.job_title,
            department=invitation_record.department,
            personal_message=invitation_record.personal_message,
            expires_at=invitation_record.expires_at,
            accepted_at=invitation_record.accepted_at,
            created_at=invitation_record.created_at,
            updated_at=invitation_record.updated_at,
            is_expired=invitation_record.is_expired,
            is_pending=invitation_record.is_pending,
            days_until_expiry=invitation_record.days_until_expiry
        )
        
        return InvitationToken(
            token=token,
            is_valid=True,
            invitation=invitation_response
        )
        
    except Exception as e:
        logger.error(f"Error validating invitation token: {str(e)}")
        return InvitationToken(
            token=token,
            is_valid=False,
            error_message="Error validating invitation"
        )


@router.post(
    "/accept",
    response_model=UserResponse,
    status_code=201,
    summary="Accept invitation",
    description="Accept an invitation and create user account"
)
async def accept_invitation(
    acceptance_data: InvitationAccept = Body(...),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Accept an invitation and create a new user account.
    
    This endpoint is public (no authentication required) as it's used
    by new users who don't have accounts yet.
    
    The process:
    1. Validates the invitation token
    2. Creates the user account with SuperTokens
    3. Creates the user record in database
    4. Marks invitation as accepted
    5. Sends welcome email
    """
    try:
        # Validate token
        token_payload = token_service.validate_invitation_token(acceptance_data.token)
        if not token_payload:
            raise HTTPException(status_code=400, detail="Invalid or expired invitation token")
        
        # Get invitation from database
        invitation_record = await invitation.get_by_token(db, acceptance_data.token)
        if not invitation_record or not invitation_record.is_pending:
            raise HTTPException(status_code=400, detail="Invitation is no longer valid")
        
        # Check if user already exists
        existing_user = await user.get_by_email(db, email=invitation_record.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User account already exists")
        
        # TODO: Create user account with SuperTokens
        # For now, create a mock SuperTokens user ID
        mock_supertokens_id = f"mock_st_{invitation_record.email.replace('@', '_').replace('.', '_')}"
        
        # Prepare user data
        user_data = UserCreateInternal(
            email=invitation_record.email,
            first_name=acceptance_data.first_name or invitation_record.first_name or "",
            last_name=acceptance_data.last_name or invitation_record.last_name or "",
            phone_number=acceptance_data.phone_number,
            bio=acceptance_data.bio,
            job_title=acceptance_data.job_title or invitation_record.job_title,
            department=acceptance_data.department or invitation_record.department,
            organization_id=invitation_record.organization_id,
            role=invitation_record.invited_role,
            supertokens_user_id=mock_supertokens_id,
            status="active"  # User is active once they accept invitation
        )
        
        # Create user in database
        new_user = await user.create(db, obj_in=user_data.model_dump())
        
        # Mark invitation as accepted
        await invitation.mark_as_accepted(db, invitation_record.id, new_user.id)
        
        # Send welcome email
        org_result = await db.execute(
            select(Organization).where(Organization.id == new_user.organization_id)
        )
        organization = org_result.scalar_one()
        
        await email_service.send_welcome_email(new_user, organization)
        
        logger.info(
            f"User {new_user.id} created via invitation acceptance. "
            f"Email: {new_user.email}, Organization: {organization.name}"
        )
        
        return UserResponse.model_validate(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to accept invitation")


@router.get(
    "/",
    response_model=InvitationListResponse,
    summary="List organization invitations",
    description="List invitations for the current organization (admin only)"
)
async def list_invitations(
    status: Optional[InvitationStatus] = Query(None, description="Filter by invitation status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_mock_admin_user),
    db: AsyncSession = Depends(get_db)
) -> InvitationListResponse:
    """List invitations for the current organization.
    
    Only admins can view organization invitations.
    """
    try:
        skip = (page - 1) * page_size
        
        # Get invitations
        invitations = await invitation.get_organization_invitations(
            db,
            current_user.organization_id,
            status=status,
            skip=skip,
            limit=page_size
        )
        
        # Get total count
        total = await invitation.count_organization_invitations(
            db, current_user.organization_id, status=status
        )
        
        # Convert to response format
        invitation_responses = [
            InvitationResponse(
                id=inv.id,
                email=inv.email,
                token=inv.token,
                organization_id=inv.organization_id,
                invited_role=inv.invited_role,
                invited_by=inv.invited_by,
                status=inv.status,
                first_name=inv.first_name,
                last_name=inv.last_name,
                job_title=inv.job_title,
                department=inv.department,
                personal_message=inv.personal_message,
                expires_at=inv.expires_at,
                accepted_at=inv.accepted_at,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                is_expired=inv.is_expired,
                is_pending=inv.is_pending,
                days_until_expiry=inv.days_until_expiry
            )
            for inv in invitations
        ]
        
        total_pages = (total + page_size - 1) // page_size
        
        return InvitationListResponse(
            invitations=invitation_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing invitations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list invitations")


@router.get(
    "/stats",
    response_model=InvitationStats,
    summary="Get invitation statistics",
    description="Get invitation statistics for the organization (admin only)"
)
async def get_invitation_stats(
    current_user: User = Depends(get_mock_admin_user),
    db: AsyncSession = Depends(get_db)
) -> InvitationStats:
    """Get invitation statistics for the organization."""
    try:
        stats = await invitation.get_invitation_stats(db, current_user.organization_id)
        
        # Convert recent invitations to response format
        recent_responses = [
            InvitationResponse(
                id=inv.id,
                email=inv.email,
                token=inv.token,
                organization_id=inv.organization_id,
                invited_role=inv.invited_role,
                invited_by=inv.invited_by,
                status=inv.status,
                first_name=inv.first_name,
                last_name=inv.last_name,
                job_title=inv.job_title,
                department=inv.department,
                personal_message=inv.personal_message,
                expires_at=inv.expires_at,
                accepted_at=inv.accepted_at,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                is_expired=inv.is_expired,
                is_pending=inv.is_pending,
                days_until_expiry=inv.days_until_expiry
            )
            for inv in stats["recent_invitations"]
        ]
        
        return InvitationStats(
            total_sent=stats["total_sent"],
            pending=stats["pending"],
            accepted=stats["accepted"],
            expired=stats["expired"],
            cancelled=stats["cancelled"],
            acceptance_rate=stats["acceptance_rate"],
            recent_invitations=recent_responses
        )
        
    except Exception as e:
        logger.error(f"Error getting invitation stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get invitation statistics")


@router.post(
    "/{invitation_id}/cancel",
    response_model=InvitationResponse,
    summary="Cancel invitation",
    description="Cancel a pending invitation (admin only)"
)
async def cancel_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_mock_admin_user),
    db: AsyncSession = Depends(get_db)
) -> InvitationResponse:
    """Cancel a pending invitation."""
    try:
        # Get invitation
        invitation_record = await invitation.get(db, id=invitation_id)
        if not invitation_record:
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        # Verify admin can only cancel invitations from their organization
        if invitation_record.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot cancel invitations from other organizations"
            )
        
        # Cancel invitation
        cancelled_invitation = await invitation.cancel_invitation(
            db, invitation_id, current_user.id
        )
        
        if not cancelled_invitation:
            raise HTTPException(status_code=400, detail="Cannot cancel this invitation")
        
        logger.info(f"Admin {current_user.id} cancelled invitation {invitation_id}")
        
        return InvitationResponse(
            id=cancelled_invitation.id,
            email=cancelled_invitation.email,
            token=cancelled_invitation.token,
            organization_id=cancelled_invitation.organization_id,
            invited_role=cancelled_invitation.invited_role,
            invited_by=cancelled_invitation.invited_by,
            status=cancelled_invitation.status,
            first_name=cancelled_invitation.first_name,
            last_name=cancelled_invitation.last_name,
            job_title=cancelled_invitation.job_title,
            department=cancelled_invitation.department,
            personal_message=cancelled_invitation.personal_message,
            expires_at=cancelled_invitation.expires_at,
            accepted_at=cancelled_invitation.accepted_at,
            created_at=cancelled_invitation.created_at,
            updated_at=cancelled_invitation.updated_at,
            is_expired=cancelled_invitation.is_expired,
            is_pending=cancelled_invitation.is_pending,
            days_until_expiry=cancelled_invitation.days_until_expiry
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling invitation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel invitation")


@router.post(
    "/{invitation_id}/resend",
    response_model=InvitationResponse,
    summary="Resend invitation",
    description="Resend an invitation email (admin only)"
)
async def resend_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_mock_admin_user),
    db: AsyncSession = Depends(get_db)
) -> InvitationResponse:
    """Resend an invitation email and extend expiry."""
    try:
        # Get invitation
        invitation_record = await invitation.get(db, id=invitation_id)
        if not invitation_record:
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        # Verify organization
        if invitation_record.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot resend invitations from other organizations"
            )
        
        # Resend invitation (extends expiry)
        updated_invitation = await invitation.resend_invitation(db, invitation_id)
        if not updated_invitation:
            raise HTTPException(status_code=400, detail="Cannot resend this invitation")
        
        # Send email
        org_result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = org_result.scalar_one()
        
        invitation_url = f"{settings.FRONTEND_URL}/accept-invitation?token={updated_invitation.token}"
        
        await email_service.send_invitation_email(
            invitation=updated_invitation,
            organization=organization,
            inviter=current_user,
            invitation_url=invitation_url
        )
        
        logger.info(f"Admin {current_user.id} resent invitation {invitation_id}")
        
        return InvitationResponse(
            id=updated_invitation.id,
            email=updated_invitation.email,
            token=updated_invitation.token,
            organization_id=updated_invitation.organization_id,
            invited_role=updated_invitation.invited_role,
            invited_by=updated_invitation.invited_by,
            status=updated_invitation.status,
            first_name=updated_invitation.first_name,
            last_name=updated_invitation.last_name,
            job_title=updated_invitation.job_title,
            department=updated_invitation.department,
            personal_message=updated_invitation.personal_message,
            expires_at=updated_invitation.expires_at,
            accepted_at=updated_invitation.accepted_at,
            created_at=updated_invitation.created_at,
            updated_at=updated_invitation.updated_at,
            is_expired=updated_invitation.is_expired,
            is_pending=updated_invitation.is_pending,
            days_until_expiry=updated_invitation.days_until_expiry
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending invitation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resend invitation")