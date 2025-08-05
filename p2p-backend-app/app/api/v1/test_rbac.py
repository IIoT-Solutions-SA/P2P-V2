"""Test endpoints for Role-Based Access Control (RBAC) functionality."""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.logging import get_logger
from app.db.session import get_db
from app.core.rbac import (
    get_current_user,
    get_current_admin_user,
    require_admin,
    require_member_or_admin,
    require_permissions,
    require_role,
    require_user_management,
    require_organization_management,
    require_content_creation,
    require_content_moderation,
    Permissions,
    ROLE_PERMISSIONS,
)
from app.models.enums import UserRole
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


class RBACTestResponse(BaseModel):
    """Response schema for RBAC test endpoints."""
    success: bool
    message: str
    user_email: str
    user_role: str
    required_permissions: List[str] = []
    user_permissions: List[str] = []


@router.get("/whoami", response_model=RBACTestResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information (any authenticated user).
    
    This endpoint is accessible to any authenticated user.
    """
    logger.info(f"RBAC Test: whoami accessed by {current_user.email}")
    
    user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
    
    return RBACTestResponse(
        success=True,
        message=f"Hello {current_user.first_name}! You are authenticated.",
        user_email=current_user.email,
        user_role=current_user.role.value,
        user_permissions=user_permissions
    )


@router.get("/admin-only", response_model=RBACTestResponse)
async def admin_only_endpoint(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Admin-only endpoint using role-based access control.
    
    Only users with ADMIN role can access this endpoint.
    """
    logger.info(f"RBAC Test: admin-only accessed by {current_user.email}")
    
    return RBACTestResponse(
        success=True,
        message="Admin access granted! You have full administrative privileges.",
        user_email=current_user.email,
        user_role=current_user.role.value,
        required_permissions=["ADMIN_ROLE"],
        user_permissions=ROLE_PERMISSIONS.get(current_user.role, [])
    )


@router.get("/member-or-admin", response_model=RBACTestResponse)
async def member_or_admin_endpoint(
    user_data: Dict[str, Any] = Depends(require_member_or_admin)
):
    """
    Endpoint accessible to both members and admins.
    
    Tests multi-role access control.
    """
    user = user_data["user"]
    logger.info(f"RBAC Test: member-or-admin accessed by {user.email}")
    
    return RBACTestResponse(
        success=True,
        message=f"Welcome! This endpoint is accessible to members and admins.",
        user_email=user.email,
        user_role=user.role.value,
        required_permissions=["MEMBER_OR_ADMIN_ROLE"],
        user_permissions=ROLE_PERMISSIONS.get(user.role, [])
    )


@router.get("/user-management", response_model=RBACTestResponse)
async def user_management_endpoint(
    user_data: Dict[str, Any] = Depends(require_user_management)
):
    """
    Endpoint requiring user management permissions.
    
    Tests permission-based access control.
    """
    user = user_data["user"]
    logger.info(f"RBAC Test: user-management accessed by {user.email}")
    
    return RBACTestResponse(
        success=True,
        message="User management access granted! You can manage users.",
        user_email=user.email,
        user_role=user.role.value,
        required_permissions=[Permissions.MANAGE_USERS],
        user_permissions=ROLE_PERMISSIONS.get(user.role, [])
    )


@router.get("/organization-management", response_model=RBACTestResponse)
async def organization_management_endpoint(
    user_data: Dict[str, Any] = Depends(require_organization_management)
):
    """
    Endpoint requiring organization management permissions.
    
    Tests permission-based access control for organization management.
    """
    user = user_data["user"]
    logger.info(f"RBAC Test: organization-management accessed by {user.email}")
    
    return RBACTestResponse(
        success=True,
        message="Organization management access granted! You can manage the organization.",
        user_email=user.email,
        user_role=user.role.value,
        required_permissions=[Permissions.MANAGE_ORGANIZATION],
        user_permissions=ROLE_PERMISSIONS.get(user.role, [])
    )


@router.get("/content-creation", response_model=RBACTestResponse) 
async def content_creation_endpoint(
    user_data: Dict[str, Any] = Depends(require_content_creation)
):
    """
    Endpoint requiring content creation permissions.
    
    This should be accessible to both admins and members.
    """
    user = user_data["user"]
    logger.info(f"RBAC Test: content-creation accessed by {user.email}")
    
    return RBACTestResponse(
        success=True,
        message="Content creation access granted! You can create content.",
        user_email=user.email,
        user_role=user.role.value,
        required_permissions=[Permissions.CREATE_CONTENT],
        user_permissions=ROLE_PERMISSIONS.get(user.role, [])
    )


@router.get("/content-moderation", response_model=RBACTestResponse)
async def content_moderation_endpoint(
    user_data: Dict[str, Any] = Depends(require_content_moderation)
):
    """
    Endpoint requiring content moderation permissions.
    
    This should only be accessible to admins.
    """
    user = user_data["user"]
    logger.info(f"RBAC Test: content-moderation accessed by {user.email}")
    
    return RBACTestResponse(
        success=True,
        message="Content moderation access granted! You can moderate content.",
        user_email=user.email,
        user_role=user.role.value,
        required_permissions=[Permissions.MODERATE_CONTENT],
        user_permissions=ROLE_PERMISSIONS.get(user.role, [])
    )


@router.get("/multiple-permissions", response_model=RBACTestResponse)
async def multiple_permissions_endpoint(
    user_data: Dict[str, Any] = Depends(
        require_permissions(
            Permissions.MANAGE_USERS, 
            Permissions.MANAGE_ORGANIZATION
        )
    )
):
    """
    Endpoint requiring multiple permissions.
    
    Tests multi-permission access control.
    """
    user = user_data["user"]
    logger.info(f"RBAC Test: multiple-permissions accessed by {user.email}")
    
    required_perms = [Permissions.MANAGE_USERS, Permissions.MANAGE_ORGANIZATION]
    
    return RBACTestResponse(
        success=True,
        message="Multiple permissions access granted! You have admin-level access.",
        user_email=user.email,
        user_role=user.role.value,
        required_permissions=required_perms,
        user_permissions=ROLE_PERMISSIONS.get(user.role, [])
    )


@router.get("/permission-matrix")
async def get_permission_matrix():
    """
    Get the complete role-permission matrix.
    
    This endpoint shows all roles and their associated permissions.
    """
    logger.info("RBAC Test: permission-matrix accessed")
    
    return {
        "success": True,
        "message": "Role-permission matrix retrieved successfully",
        "role_permissions": {
            role.value: permissions 
            for role, permissions in ROLE_PERMISSIONS.items()
        },
        "available_permissions": {
            "user_management": [
                Permissions.MANAGE_USERS,
                Permissions.INVITE_USERS,
                Permissions.VIEW_USERS,
            ],
            "organization_management": [
                Permissions.MANAGE_ORGANIZATION,
                Permissions.VIEW_ORGANIZATION_STATS,
            ],
            "content_management": [
                Permissions.CREATE_CONTENT,
                Permissions.MODERATE_CONTENT,
                Permissions.DELETE_ANY_CONTENT,
            ],
            "forum_management": [
                Permissions.CREATE_FORUM_POSTS,
                Permissions.MODERATE_FORUM,
                Permissions.PIN_FORUM_POSTS,
            ],
            "use_case_management": [
                Permissions.CREATE_USE_CASES,
                Permissions.MODERATE_USE_CASES,
                Permissions.EXPORT_USE_CASES,
            ],
            "system_management": [
                Permissions.VIEW_SYSTEM_STATS,
                Permissions.MANAGE_SYSTEM_SETTINGS,
            ],
        }
    }


@router.get("/test-forbidden")
async def test_forbidden_endpoint(
    user_data: Dict[str, Any] = Depends(
        require_permissions("NON_EXISTENT_PERMISSION")
    )
):
    """
    Endpoint that should always return 403.
    
    Tests that permission checking works for non-existent permissions.
    """
    # This should never be reached due to permission check
    return {"message": "This should not be accessible"}


class ResourceOwnershipTestResponse(BaseModel):
    """Response for resource ownership tests."""
    success: bool
    message: str
    resource_owner: str
    current_user: str
    can_access: bool


@router.get("/resource-ownership/{resource_user_id}", response_model=ResourceOwnershipTestResponse)
async def test_resource_ownership(
    resource_user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Test resource ownership checking.
    
    Users can only access their own resources unless they are admin.
    """
    from app.core.rbac import check_resource_ownership
    
    can_access = check_resource_ownership(current_user, resource_user_id)
    
    logger.info(
        f"RBAC Test: resource-ownership - User {current_user.email} "
        f"attempting to access resource owned by {resource_user_id}: {can_access}"
    )
    
    if not can_access:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own resources"
        )
    
    return ResourceOwnershipTestResponse(
        success=True,
        message="Resource access granted",
        resource_owner=resource_user_id,
        current_user=str(current_user.id),
        can_access=can_access
    )