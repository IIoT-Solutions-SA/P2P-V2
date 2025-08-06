"""Organizations API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
# Temporarily use mock authentication
from app.api.v1.users import get_current_user, get_mock_admin_user
from app.models.user import User
from app.models.organization import Organization
from app.schemas.organization import (
    Organization as OrganizationResponse,
    OrganizationUpdate,
    OrganizationBrief,
    OrganizationStats
)
from app.crud.organization import organization as organization_crud
from app.services.file_storage import file_storage_service
from app.core.logging import get_logger

logger = get_logger(__name__)

organizations_router = APIRouter()


@organizations_router.get(
    "/me", 
    response_model=OrganizationResponse,
    summary="Get current organization",
    description="Get detailed information about the current user's organization"
)
async def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OrganizationResponse:
    """Get the current user's organization details.
    
    Returns comprehensive organization information including:
    - Basic details (name, description, contact info)
    - Address and business information
    - Branding (logo, banner)
    - Subscription and usage limits
    - Settings and preferences
    """
    try:
        # Get organization with fresh data
        organization = await organization_crud.get(db, id=current_user.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404, 
                detail="Organization not found"
            )
        
        logger.info(f"Retrieved organization {organization.id} for user {current_user.id}")
        return OrganizationResponse.model_validate(organization)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve organization")


@organizations_router.patch(
    "/me",
    response_model=OrganizationResponse,
    summary="Update current organization",
    description="Update the current user's organization (admin only)"
)
async def update_current_organization(
    organization_data: OrganizationUpdate,
    current_user: User = Depends(get_mock_admin_user),  # Admin only
    db: AsyncSession = Depends(get_db)
) -> OrganizationResponse:
    """Update the current user's organization.
    
    Only organization administrators can update organization details.
    
    **Updatable Fields:**
    - Basic info: name, name_arabic, description
    - Contact: email, phone_number, website
    - Address: address fields, city, state, postal code
    - Branding: logo_url, banner_url
    - Settings: public use cases, approval requirements
    
    **Admin-Only Fields** (not available in regular update):
    - Status, subscription tier, usage limits
    - Trial settings, registration details
    """
    try:
        # Get current organization
        organization = await organization_crud.get(db, id=current_user.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404, 
                detail="Organization not found"
            )
        
        # Update organization
        updated_org = await organization_crud.update(
            db, 
            db_obj=organization, 
            obj_in=organization_data.model_dump(exclude_unset=True)
        )
        
        logger.info(f"Organization {organization.id} updated by admin {current_user.id}")
        return OrganizationResponse.model_validate(updated_org)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update organization")


@organizations_router.post(
    "/me/logo",
    response_model=OrganizationResponse,
    summary="Upload organization logo",
    description="Upload a new logo for the organization (admin only)"
)
async def upload_organization_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_mock_admin_user),  # Admin only
    db: AsyncSession = Depends(get_db)
) -> OrganizationResponse:
    """Upload organization logo.
    
    **File Requirements:**
    - Format: JPG, PNG, GIF
    - Max size: 5MB
    - Recommended: Square aspect ratio (1:1)
    - Recommended size: 512x512px or larger
    
    The logo will be automatically resized and optimized for various uses.
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Only image files are allowed for logo upload"
            )
        
        # Get current organization
        organization = await organization_crud.get(db, id=current_user.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404, 
                detail="Organization not found"
            )
        
        # Upload file
        file_record = await file_storage_service.upload_file(
            file=file,
            user_id=current_user.id,
            file_type="organization_logo",
            description=f"Logo for {organization.name}"
        )
        
        # Update organization with new logo URL
        updated_org = await organization_crud.update(
            db,
            db_obj=organization,
            obj_in={"logo_url": file_record.file_url}
        )
        
        logger.info(f"Logo uploaded for organization {organization.id} by admin {current_user.id}")
        return OrganizationResponse.model_validate(updated_org)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading organization logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload logo")


@organizations_router.delete(
    "/me/logo",
    response_model=OrganizationResponse,
    summary="Remove organization logo", 
    description="Remove the current organization logo (admin only)"
)
async def remove_organization_logo(
    current_user: User = Depends(get_mock_admin_user),  # Admin only
    db: AsyncSession = Depends(get_db)
) -> OrganizationResponse:
    """Remove the organization's current logo.
    
    This will set the logo_url to null, reverting to a default logo
    or organization initials in the frontend.
    """
    try:
        # Get current organization
        organization = await organization_crud.get(db, id=current_user.organization_id)
        if not organization:
            raise HTTPException(
                status_code=404, 
                detail="Organization not found"
            )
        
        # Remove logo URL
        updated_org = await organization_crud.update(
            db,
            db_obj=organization,
            obj_in={"logo_url": None}
        )
        
        logger.info(f"Logo removed for organization {organization.id} by admin {current_user.id}")
        return OrganizationResponse.model_validate(updated_org)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing organization logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove logo")


@organizations_router.get(
    "/{org_id}",
    response_model=OrganizationBrief,
    summary="Get organization public info",
    description="Get public information about any organization"
)
async def get_organization_public(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> OrganizationBrief:
    """Get public organization information.
    
    This endpoint provides limited, public information about any organization:
    - Name and Arabic name
    - Logo URL
    - Industry type
    
    This is useful for displaying organization information in use cases,
    forum posts, or other public contexts without exposing sensitive data.
    """
    try:
        # Get organization
        organization = await organization_crud.get(db, id=org_id)
        if not organization or organization.is_deleted:
            raise HTTPException(
                status_code=404, 
                detail="Organization not found"
            )
        
        # Return only public information
        return OrganizationBrief(
            id=organization.id,
            name=organization.name,
            name_arabic=organization.name_arabic,
            logo_url=organization.logo_url,
            industry_type=organization.industry_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization {org_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve organization")


@organizations_router.get(
    "/stats",
    response_model=OrganizationStats,
    summary="Get organization statistics",
    description="Get comprehensive statistics for the current organization (admin only)"
)
async def get_organization_statistics(
    current_user: User = Depends(get_mock_admin_user),  # Admin only
    db: AsyncSession = Depends(get_db)
) -> OrganizationStats:
    """Get comprehensive organization statistics.
    
    Only organization administrators can access this endpoint.
    
    Returns detailed statistics including:
    - User counts by status and role
    - Activity metrics (forums, use cases, messages)
    - Storage usage and limits
    - Subscription information
    
    This data is useful for:
    - Admin dashboards
    - Usage monitoring
    - Capacity planning
    - Billing and subscription management
    """
    try:
        from datetime import datetime
        from sqlalchemy import func, and_
        from app.models.enums import UserStatus, UserRole
        from app.models.file_metadata import FileMetadata
        
        org_id = current_user.organization_id
        
        # Get organization for subscription details
        organization = await organization_crud.get(db, id=org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # === USER STATISTICS ===
        
        # Total users count
        total_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(User.organization_id == org_id, User.is_deleted == False))
        )
        total_users = total_users_result.scalar() or 0
        
        # Active users count
        active_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.organization_id == org_id,
                User.is_deleted == False,
                User.status == UserStatus.ACTIVE
            ))
        )
        active_users = active_users_result.scalar() or 0
        
        # Admin users count
        admin_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.organization_id == org_id,
                User.is_deleted == False,
                User.role == UserRole.ADMIN
            ))
        )
        admin_users = admin_users_result.scalar() or 0
        
        # Member users count
        member_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.organization_id == org_id,
                User.is_deleted == False,
                User.role == UserRole.MEMBER
            ))
        )
        member_users = member_users_result.scalar() or 0
        
        # Pending users count
        pending_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.organization_id == org_id,
                User.is_deleted == False,
                User.status == UserStatus.PENDING
            ))
        )
        pending_users = pending_users_result.scalar() or 0
        
        # Inactive users count
        inactive_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.organization_id == org_id,
                User.is_deleted == False,
                User.status == UserStatus.INACTIVE
            ))
        )
        inactive_users = inactive_users_result.scalar() or 0
        
        # === STORAGE STATISTICS ===
        
        # Total files and storage usage
        storage_result = await db.execute(
            select(
                func.count(FileMetadata.id),
                func.coalesce(func.sum(FileMetadata.size_bytes), 0)
            )
            .where(and_(
                FileMetadata.organization_id == org_id,
                FileMetadata.is_deleted == False
            ))
        )
        storage_data = storage_result.first()
        total_files = storage_data[0] or 0
        storage_used_bytes = storage_data[1] or 0
        
        # Convert storage to different units
        storage_used_mb = storage_used_bytes / (1024 * 1024) if storage_used_bytes > 0 else 0.0
        storage_used_gb = storage_used_mb / 1024 if storage_used_mb > 0 else 0.0
        storage_limit_gb = organization.max_storage_gb
        storage_percentage_used = (storage_used_gb / storage_limit_gb * 100) if storage_limit_gb > 0 else 0.0
        
        # === ACTIVITY STATISTICS (Placeholder values for now) ===
        # These will be implemented when forum and use case models are available
        forum_topics = 0
        forum_posts = 0
        use_cases_submitted = 0
        use_cases_published = 0
        messages_sent = 0
        
        # Create statistics response
        stats = OrganizationStats(
            # User Statistics
            total_users=total_users,
            active_users=active_users,
            admin_users=admin_users,
            member_users=member_users,
            pending_users=pending_users,
            inactive_users=inactive_users,
            
            # Activity Statistics (placeholders)
            forum_topics=forum_topics,
            forum_posts=forum_posts,
            use_cases_submitted=use_cases_submitted,
            use_cases_published=use_cases_published,
            messages_sent=messages_sent,
            
            # Storage Statistics
            total_files=total_files,
            storage_used_bytes=storage_used_bytes,
            storage_used_mb=round(storage_used_mb, 2),
            storage_used_gb=round(storage_used_gb, 2),
            storage_limit_gb=storage_limit_gb,
            storage_percentage_used=round(storage_percentage_used, 1),
            
            # Subscription Information
            subscription_tier=organization.subscription_tier,
            max_users=organization.max_users,
            max_use_cases=organization.max_use_cases,
            trial_ends_at=organization.trial_ends_at,
            
            # Timestamps
            calculated_at=datetime.utcnow()
        )
        
        logger.info(f"Organization statistics calculated for {org_id} by admin {current_user.id}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating organization statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate organization statistics")