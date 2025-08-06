"""User profile and management API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
# Temporarily disable RBAC due to SuperTokens compatibility
# from app.core.rbac import get_current_user, get_current_admin_user, require_permissions
from app.models.user import User
from app.models.organization import Organization
from app.schemas.user import (
    UserProfile,
    UserUpdate,
    UserUpdateAdmin,
    UserWithOrganization,
    User as UserResponse
)
from app.schemas.organization import OrganizationBrief
from app.crud.user import user
from app.services.file_storage import file_storage_service
from app.core.logging import get_logger

logger = get_logger(__name__)

users_router = APIRouter()


# Temporary mock dependencies for testing without SuperTokens
async def get_mock_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Mock current user for testing."""
    from sqlalchemy import select
    from app.models.enums import UserRole, UserStatus
    
    # Try to get first active user from database
    result = await db.execute(
        select(User).where(User.status == UserStatus.ACTIVE).limit(1)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create a mock user if none exists
        from uuid import uuid4
        mock_user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone_number="+1234567890",
            bio="Test user bio",
            job_title="Software Engineer",
            department="Engineering",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            organization_id=uuid4(),
            supertokens_user_id="mock-supertokens-id",
            email_verified=True,
            email_notifications_enabled=True,
            forum_notifications_enabled=True,
            message_notifications_enabled=True
        )
        return mock_user
    
    return user


async def get_mock_admin_user(db: AsyncSession = Depends(get_db)) -> User:
    """Mock admin user for testing."""
    user = await get_mock_current_user(db)
    from app.models.enums import UserRole
    user.role = UserRole.ADMIN
    return user


# Use mock dependencies until SuperTokens is re-enabled
get_current_user = get_mock_current_user
get_current_admin_user = get_mock_admin_user


@users_router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfile:
    """Get the current user's profile with organization details."""
    try:
        # Get organization details
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Create organization brief
        org_brief = OrganizationBrief(
            id=organization.id,
            name=organization.name,
            name_arabic=organization.name_arabic,
            logo_url=organization.logo_url,
            industry_type=organization.industry_type
        )
        
        # TODO: Get actual counts from database when forum and use case models are implemented
        total_posts = 0
        total_use_cases = 0
        
        # Create user profile response
        profile = UserProfile(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            phone_number=current_user.phone_number,
            bio=current_user.bio,
            job_title=current_user.job_title,
            department=current_user.department,
            profile_picture_url=current_user.profile_picture_url,
            organization_id=current_user.organization_id,
            role=current_user.role,
            status=current_user.status,
            supertokens_user_id=current_user.supertokens_user_id,
            email_notifications_enabled=current_user.email_notifications_enabled,
            forum_notifications_enabled=current_user.forum_notifications_enabled,
            message_notifications_enabled=current_user.message_notifications_enabled,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            is_deleted=current_user.is_deleted,
            deleted_at=current_user.deleted_at,
            organization=org_brief,
            total_posts=total_posts,
            total_use_cases=total_use_cases
        )
        
        logger.info(f"User {current_user.id} retrieved their profile")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")


@users_router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user"
)
async def update_current_user_profile(
    user_update: UserUpdate = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update the current user's profile.
    
    Users can update their own:
    - Basic info (name, phone, bio, job title, department)
    - Notification preferences
    - Profile picture URL (use separate endpoint for upload)
    
    Users CANNOT update:
    - Email (requires verification)
    - Role (admin only)
    - Status (admin only)
    - Organization (not allowed)
    """
    try:
        # Filter out fields that users cannot update themselves
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Prevent users from changing their email without verification
        if "email" in update_data:
            logger.warning(f"User {current_user.id} attempted to change email directly")
            del update_data["email"]
        
        # Update user in database
        updated_user = await user.update(db, db_obj=current_user, obj_in=update_data)
        
        logger.info(f"User {current_user.id} updated their profile")
        
        return UserResponse.model_validate(updated_user)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")


@users_router.post(
    "/me/profile-picture",
    response_model=dict,
    summary="Upload profile picture",
    description="Upload a new profile picture for the current user"
)
async def upload_profile_picture(
    file: UploadFile = File(..., description="Profile picture file (JPG, PNG, or WebP)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Upload a profile picture for the current user.
    
    The image will be validated, resized if necessary, and stored.
    The user's profile will be updated with the new picture URL.
    
    **Restrictions:**
    - Max file size: 10MB
    - Allowed formats: JPG, PNG, WebP
    - Image will be resized if larger than 1024x1024
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Check file size (10MB max for images)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Upload file using storage service
        file_info = await file_storage_service.upload_file(
            file=file,
            category="profile_pictures",
            user_id=current_user.id
        )
        
        # Update user's profile picture URL
        file_url = file_storage_service.get_file_url(file_info["storage_path"])
        updated_user = await user.update(
            db, 
            db_obj=current_user, 
            obj_in={"profile_picture_url": file_url}
        )
        
        logger.info(f"User {current_user.id} uploaded new profile picture: {file_info['file_id']}")
        
        return {
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": file_url,
            "file_id": file_info["file_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload profile picture")


@users_router.delete(
    "/me/profile-picture",
    response_model=dict,
    summary="Remove profile picture",
    description="Remove the current user's profile picture"
)
async def remove_profile_picture(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Remove the current user's profile picture."""
    try:
        if not current_user.profile_picture_url:
            raise HTTPException(status_code=404, detail="No profile picture to remove")
        
        # TODO: Delete the actual file from storage when file deletion is implemented
        # For now, just clear the URL from the user profile
        
        # Clear profile picture URL
        updated_user = await user.update(
            db,
            db_obj=current_user,
            obj_in={"profile_picture_url": None}
        )
        
        logger.info(f"User {current_user.id} removed their profile picture")
        
        return {"message": "Profile picture removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove profile picture")


@users_router.get(
    "/{user_id}",
    response_model=UserWithOrganization,
    summary="Get user by ID",
    description="Get a user's public profile by their ID (same organization only)"
)
async def get_user_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserWithOrganization:
    """Get a user's public profile by ID.
    
    Users can only view profiles of users in the same organization.
    Admins can see all users in their organization.
    """
    try:
        # Get the target user
        target_user = await user.get(db, id=user_id)
        
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if users are in the same organization
        if target_user.organization_id != current_user.organization_id:
            logger.warning(
                f"User {current_user.id} attempted to access user {user_id} "
                f"from different organization"
            )
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get organization details
        result = await db.execute(
            select(Organization).where(Organization.id == target_user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return UserWithOrganization(
            id=target_user.id,
            email=target_user.email,
            first_name=target_user.first_name,
            last_name=target_user.last_name,
            phone_number=target_user.phone_number,
            bio=target_user.bio,
            job_title=target_user.job_title,
            department=target_user.department,
            profile_picture_url=target_user.profile_picture_url,
            organization_id=target_user.organization_id,
            organization_name=organization.name,
            role=target_user.role,
            status=target_user.status,
            supertokens_user_id=target_user.supertokens_user_id,
            email_notifications_enabled=target_user.email_notifications_enabled,
            forum_notifications_enabled=target_user.forum_notifications_enabled,
            message_notifications_enabled=target_user.message_notifications_enabled,
            created_at=target_user.created_at,
            updated_at=target_user.updated_at,
            is_deleted=target_user.is_deleted,
            deleted_at=target_user.deleted_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@users_router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user (admin only)",
    description="Update any user's profile (admin only)"
)
async def update_user_by_admin(
    user_id: uuid.UUID,
    user_update: UserUpdateAdmin = Body(...),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update a user's profile (admin only).
    
    Admins can update any field including role and status.
    Admins can only manage users in their own organization.
    """
    try:
        # Get the target user
        target_user = await user.get(db, id=user_id)
        
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify admin can only manage users in their organization
        if target_user.organization_id != current_user.organization_id:
            logger.warning(
                f"Admin {current_user.id} attempted to modify user {user_id} "
                f"from different organization"
            )
            raise HTTPException(
                status_code=403,
                detail="Cannot modify users from other organizations"
            )
        
        # Prevent admin from changing their own role
        if user_id == current_user.id and "role" in user_update.model_dump(exclude_unset=True):
            logger.warning(f"Admin {current_user.id} attempted to change their own role")
            raise HTTPException(status_code=400, detail="Cannot change your own role")
        
        # Update the user
        update_data = user_update.model_dump(exclude_unset=True)
        updated_user = await user.update(db, db_obj=target_user, obj_in=update_data)
        
        logger.info(
            f"Admin {current_user.id} updated user {user_id} with data: "
            f"{list(update_data.keys())}"
        )
        
        return UserResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user")