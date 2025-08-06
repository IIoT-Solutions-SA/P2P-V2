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
    OrganizationBrief
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