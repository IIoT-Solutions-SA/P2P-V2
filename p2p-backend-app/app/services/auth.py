"""Authentication service for handling signup/signin flows."""

from typing import Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import uuid as uuid_lib
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.utils.logging import log_database_operation, log_business_event
from app.models.user import User
from app.models.organization import Organization
from app.models.enums import UserRole, UserStatus, OrganizationStatus, IndustryType
from app.crud.user import user as user_crud
from app.crud.organization import organization as organization_crud
from app.schemas.user import UserCreate, UserCreateInternal
from app.schemas.organization import OrganizationCreate

logger = get_logger(__name__)


class AuthService:
    """Service for handling authentication-related business logic."""

    @staticmethod
    async def create_organization_and_admin_user(
        db: AsyncSession,
        *,
        supertokens_user_id: str,
        email: str,
        first_name: str,
        last_name: str,
        organization_name: str,
        industry_type: IndustryType = IndustryType.OTHER,
        organization_size: str = "small",
        country: str = "Saudi Arabia",
        city: str = "",
    ) -> Tuple[User, Organization]:
        """
        Create an organization and its admin user atomically.
        
        This is the core business logic for P2P Sandbox: every signup creates
        an organization with the user as admin.
        
        Args:
            db: Database session
            supertokens_user_id: SuperTokens user ID
            email: User email
            first_name: User first name  
            last_name: User last name
            organization_name: Organization name
            industry_type: Industry type for the organization
            
        Returns:
            Tuple of (User, Organization) objects
            
        Raises:
            IntegrityError: If organization name or email already exists
            Exception: For other database errors
        """
        
        logger.info(f"Creating organization and admin user for: {email}")
        
        try:
            # Start transaction by using the provided session
            # 1. Create organization first
            org_data = OrganizationCreate(
                name=organization_name,
                email=email,
                industry_type=industry_type,
                status=OrganizationStatus.TRIAL,
                subscription_tier="basic",
                max_users=10,
                max_use_cases=50,
                max_storage_gb=10,
                company_size=organization_size,
                country="SA" if country == "Saudi Arabia" else country[:2].upper(),
                city=city,
                # Set trial to expire in 30 days
                trial_ends_at=datetime.utcnow() + timedelta(days=30)
            )
            
            organization = await organization_crud.create(db, obj_in=org_data)
            log_database_operation(
                operation="CREATE",
                table="organizations", 
                record_id=str(organization.id),
                details={"name": organization_name, "industry": industry_type}
            )
            
            # 2. Create admin user linked to organization
            user_data = UserCreateInternal(
                email=email,
                first_name=first_name,
                last_name=last_name,
                supertokens_user_id=supertokens_user_id,
                organization_id=organization.id,
                role=UserRole.ADMIN,  # First user is always admin
                status=UserStatus.ACTIVE,  # Skip email verification for now
                email_notifications_enabled=True,
                forum_notifications_enabled=True,
                message_notifications_enabled=True
            )
            
            user = await user_crud.create(db, obj_in=user_data)
            log_database_operation(
                operation="CREATE",
                table="users",
                record_id=str(user.id),
                details={
                    "email": email,
                    "role": UserRole.ADMIN,
                    "organization_id": str(organization.id)
                }
            )
            
            # 3. Log business event
            log_business_event(
                event_type="USER_SIGNUP_WITH_ORG_CREATION",
                entity_type="user",
                entity_id=str(user.id),
                organization_id=str(organization.id),
                supertokens_user_id=supertokens_user_id,
                organization_name=organization_name,
                industry_type=industry_type,
                user_role=UserRole.ADMIN
            )
            
            logger.info(
                f"Successfully created organization '{organization_name}' "
                f"and admin user '{email}' (User ID: {user.id}, Org ID: {organization.id})"
            )
            
            return user, organization
            
        except IntegrityError as e:
            logger.error(f"Integrity error during signup: {e}")
            # Handle specific constraint violations
            if "organizations_name_key" in str(e):
                raise ValueError(f"Organization name '{organization_name}' already exists")
            elif "users_email_key" in str(e):
                raise ValueError(f"Email '{email}' already exists")
            elif "users_supertokens_user_id_key" in str(e):
                raise ValueError(f"SuperTokens user ID already exists")
            else:
                raise ValueError("Data integrity error during signup")
                
        except Exception as e:
            logger.error(f"Unexpected error during signup: {e}")
            raise Exception(f"Failed to create organization and user: {str(e)}")

    @staticmethod 
    async def get_user_by_supertokens_id(
        db: AsyncSession,
        *,
        supertokens_user_id: str
    ) -> Optional[User]:
        """Get user by SuperTokens user ID."""
        return await user_crud.get_by_supertokens_id(
            db, supertokens_user_id=supertokens_user_id
        )

    @staticmethod
    async def get_user_with_organization(
        db: AsyncSession,
        *,
        supertokens_user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user with their organization data.
        
        Returns:
            Dict containing user and organization data, or None if not found
        """
        user = await user_crud.get_by_supertokens_id(
            db, supertokens_user_id=supertokens_user_id
        )
        
        if not user:
            return None
        
        # Get organization data
        organization = await organization_crud.get(db, id=user.organization_id)
        
        return {
            "user": user,
            "organization": organization,
            "permissions": {
                "can_manage_users": user.can_manage_users(),
                "can_create_content": user.can_create_content(),
                "is_admin": user.is_admin,
                "is_active": user.is_active
            }
        }

    @staticmethod
    async def get_user_by_email_with_organization(
        db: AsyncSession,
        *,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user by email with their organization data.
        
        Returns:
            Dict containing user and organization data, or None if not found
        """
        user = await user_crud.get_by_email(db, email=email)
        
        if not user:
            return None
        
        # Get organization data
        organization = await organization_crud.get(db, id=user.organization_id)
        
        return {
            "user": user,
            "organization": organization,
            "permissions": {
                "can_manage_users": user.can_manage_users(),
                "can_create_content": user.can_create_content(),
                "is_admin": user.is_admin,
                "is_active": user.is_active
            }
        }

    @staticmethod
    def extract_organization_name_from_email(email: str) -> str:
        """
        Extract organization name from email domain.
        
        This creates a reasonable default organization name from the email.
        Users can change this later in their organization settings.
        """
        domain = email.split("@")[1]
        # Remove common TLD extensions and clean up
        org_name = domain.replace(".com", "").replace(".org", "").replace(".net", "")
        org_name = org_name.replace(".", " ").title()
        
        # Add "Organization" suffix to make it clear
        return f"{org_name} Organization"

    @staticmethod
    def parse_signup_form_fields(form_fields: list) -> Dict[str, str]:
        """
        Parse SuperTokens form fields into a dictionary.
        
        Args:
            form_fields: List of form field objects with 'id' and 'value'
            
        Returns:
            Dictionary mapping field IDs to values
        """
        return {field.id: field.value for field in form_fields}


# Create singleton instance
auth_service = AuthService()