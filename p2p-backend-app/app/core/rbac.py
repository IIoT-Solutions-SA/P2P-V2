"""Role-Based Access Control (RBAC) dependencies for FastAPI."""

from typing import Dict, Any, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.core.logging import get_logger
from app.db.session import get_db
from app.services.auth import auth_service
from app.models.user import User
from app.models.enums import UserRole, UserStatus

logger = get_logger(__name__)


# Permission constants for clarity and maintainability
class Permissions:
    """Permission constants for role-based access control."""
    
    # User management permissions
    MANAGE_USERS = "manage_users"
    INVITE_USERS = "invite_users"
    VIEW_USERS = "view_users"
    
    # Organization management permissions
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_ORGANIZATION_STATS = "view_organization_stats"
    
    # Content management permissions
    CREATE_CONTENT = "create_content"
    MODERATE_CONTENT = "moderate_content"
    DELETE_ANY_CONTENT = "delete_any_content"
    
    # Forum permissions
    CREATE_FORUM_POSTS = "create_forum_posts"
    MODERATE_FORUM = "moderate_forum"
    PIN_FORUM_POSTS = "pin_forum_posts"
    
    # Use case permissions
    CREATE_USE_CASES = "create_use_cases"
    MODERATE_USE_CASES = "moderate_use_cases"
    EXPORT_USE_CASES = "export_use_cases"
    
    # System permissions
    VIEW_SYSTEM_STATS = "view_system_stats"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"


# Role-based permission matrix
ROLE_PERMISSIONS: Dict[UserRole, List[str]] = {
    UserRole.ADMIN: [
        # Admin has all permissions
        Permissions.MANAGE_USERS,
        Permissions.INVITE_USERS,
        Permissions.VIEW_USERS,
        Permissions.MANAGE_ORGANIZATION,
        Permissions.VIEW_ORGANIZATION_STATS,
        Permissions.CREATE_CONTENT,
        Permissions.MODERATE_CONTENT,
        Permissions.DELETE_ANY_CONTENT,
        Permissions.CREATE_FORUM_POSTS,
        Permissions.MODERATE_FORUM,
        Permissions.PIN_FORUM_POSTS,
        Permissions.CREATE_USE_CASES,
        Permissions.MODERATE_USE_CASES,
        Permissions.EXPORT_USE_CASES,
        Permissions.VIEW_SYSTEM_STATS,
        Permissions.MANAGE_SYSTEM_SETTINGS,
    ],
    UserRole.MEMBER: [
        # Members have limited permissions
        Permissions.VIEW_USERS,
        Permissions.VIEW_ORGANIZATION_STATS,
        Permissions.CREATE_CONTENT,
        Permissions.CREATE_FORUM_POSTS,
        Permissions.CREATE_USE_CASES,
    ],
}


class RBACError(HTTPException):
    """Custom exception for RBAC-related errors."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_with_permissions(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user with their permissions from database.
    
    This is the base dependency that validates session and retrieves
    user data with permissions from the database.
    
    Returns:
        Dict containing user, organization, and permissions data
        
    Raises:
        HTTPException: If user not found or inactive
    """
    try:
        # Get SuperTokens user ID from session
        supertokens_user_id = session.get_user_id()
        logger.debug(f"RBAC: Getting user data for SuperTokens ID: {supertokens_user_id}")
        
        # Get user with organization data from our database
        user_data = await auth_service.get_user_with_organization(
            db, supertokens_user_id=supertokens_user_id
        )
        
        if not user_data:
            logger.warning(f"RBAC: No user data found for SuperTokens ID: {supertokens_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = user_data["user"]
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"RBAC: Inactive user attempted access: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Get role-based permissions
        role_permissions = ROLE_PERMISSIONS.get(user.role, [])
        
        # Enhance permissions with role-based permissions
        enhanced_permissions = {
            **user_data["permissions"],  # Model-based permissions
            "role_permissions": role_permissions,
            "all_permissions": role_permissions,  # For easy checking
        }
        
        result = {
            **user_data,
            "permissions": enhanced_permissions
        }
        
        logger.debug(f"RBAC: User {user.email} has role {user.role} with {len(role_permissions)} permissions")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"RBAC: Error getting user permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate user permissions"
        )


def require_permissions(*required_permissions: str):
    """
    Create a dependency that requires specific permissions.
    
    Args:
        *required_permissions: List of required permission strings
        
    Returns:
        FastAPI dependency function that validates permissions
        
    Example:
        @app.get("/admin/users")
        async def get_users(
            user_data: dict = Depends(require_permissions(Permissions.VIEW_USERS))
        ):
            return {"users": [...]}
    """
    async def permission_checker(
        user_data: Dict[str, Any] = Depends(get_current_user_with_permissions)
    ) -> Dict[str, Any]:
        user = user_data["user"]
        user_permissions = user_data["permissions"]["all_permissions"]
        
        # Check if user has all required permissions
        missing_permissions = []
        for permission in required_permissions:
            if permission not in user_permissions:
                missing_permissions.append(permission)
        
        if missing_permissions:
            logger.warning(
                f"RBAC: User {user.email} lacks permissions: {missing_permissions}"
            )
            raise RBACError(
                f"Missing required permissions: {', '.join(missing_permissions)}"
            )
        
        logger.debug(f"RBAC: User {user.email} granted access with permissions: {required_permissions}")
        return user_data
    
    return permission_checker


def require_role(*required_roles: UserRole):
    """
    Create a dependency that requires specific user roles.
    
    Args:
        *required_roles: List of required UserRole enums
        
    Returns:
        FastAPI dependency function that validates roles
        
    Example:
        @app.get("/admin/dashboard")
        async def admin_dashboard(
            user_data: dict = Depends(require_role(UserRole.ADMIN))
        ):
            return {"message": "Admin dashboard"}
    """
    async def role_checker(
        user_data: Dict[str, Any] = Depends(get_current_user_with_permissions)
    ) -> Dict[str, Any]:
        user = user_data["user"]
        user_role = user.role
        
        if user_role not in required_roles:
            logger.warning(
                f"RBAC: User {user.email} with role {user_role} attempted to access "
                f"endpoint requiring roles: {required_roles}"
            )
            raise RBACError(
                f"Access denied. Required role(s): {', '.join([role.value for role in required_roles])}"
            )
        
        logger.debug(f"RBAC: User {user.email} granted role-based access: {user_role}")
        return user_data
    
    return role_checker


# Convenience dependencies for common role checks
require_admin = require_role(UserRole.ADMIN)
require_member_or_admin = require_role(UserRole.MEMBER, UserRole.ADMIN)

# Convenience dependencies for common permission checks
require_user_management = require_permissions(Permissions.MANAGE_USERS)
require_organization_management = require_permissions(Permissions.MANAGE_ORGANIZATION)
require_content_creation = require_permissions(Permissions.CREATE_CONTENT)
require_content_moderation = require_permissions(Permissions.MODERATE_CONTENT)


async def get_current_user(
    user_data: Dict[str, Any] = Depends(get_current_user_with_permissions)
) -> User:
    """
    Get the current user object (convenience dependency).
    
    Returns:
        User object from database
    """
    return user_data["user"]


async def get_current_admin_user(
    user_data: Dict[str, Any] = Depends(require_admin)
) -> User:
    """
    Get current user, ensuring they are an admin.
    
    Returns:
        User object (guaranteed to be admin)
    """
    return user_data["user"]


def check_resource_ownership(user: User, resource_user_id: str) -> bool:
    """
    Check if user owns a resource or has admin privileges.
    
    Args:
        user: Current user
        resource_user_id: ID of user who owns the resource
        
    Returns:
        True if user can access the resource
    """
    # Admin can access any resource
    if user.role == UserRole.ADMIN:
        return True
    
    # User can access their own resources
    return str(user.id) == resource_user_id


def require_ownership_or_admin(resource_user_id: str):
    """
    Create a dependency that requires resource ownership or admin role.
    
    Args:
        resource_user_id: ID of user who owns the resource
        
    Returns:
        FastAPI dependency function
    """
    async def ownership_checker(
        user_data: Dict[str, Any] = Depends(get_current_user_with_permissions)
    ) -> Dict[str, Any]:
        user = user_data["user"]
        
        if not check_resource_ownership(user, resource_user_id):
            logger.warning(
                f"RBAC: User {user.email} attempted to access resource owned by {resource_user_id}"
            )
            raise RBACError("You can only access your own resources")
        
        return user_data
    
    return ownership_checker