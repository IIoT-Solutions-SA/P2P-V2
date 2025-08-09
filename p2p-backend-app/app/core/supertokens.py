"""SuperTokens configuration and initialization."""

from typing import Any, Dict, Optional
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session, dashboard
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface,
    APIOptions,
    SignUpPostOkResult,
    SignUpOkResult,
    EmailAlreadyExistsError,
    SignInPostOkResult,
    SignInOkResult,
    EmailExistsGetOkResult,
    GeneralErrorResponse,
)
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.recipe.emailpassword.types import FormField
from typing import List, Union
from supertokens_python.framework.fastapi import get_middleware

from app.core.config import settings
from app.core.logging import get_logger
from app.services.auth import auth_service
from app.db.session import get_db
from app.models.enums import IndustryType

logger = get_logger(__name__)


def init_supertokens() -> None:
    """Initialize SuperTokens with custom configuration."""
    
    logger.info("Initializing SuperTokens...")
    
    # Build SuperTokens configuration
    supertokens_config = SupertokensConfig(
        connection_uri=settings.SUPERTOKENS_CONNECTION_URI,
        api_key=settings.SUPERTOKENS_API_KEY,
    )
    
    # Build app info - let SuperTokens use default paths
    app_info = InputAppInfo(
        app_name=settings.PROJECT_NAME,
        api_domain=settings.API_DOMAIN,
        website_domain=settings.WEBSITE_DOMAIN,
    )
    
    # Configure recipes
    recipes = [
        # Email Password Recipe with custom signup override
        emailpassword.init(
            sign_up_feature=emailpassword.InputSignUpFeature(
                form_fields=[
                    emailpassword.InputFormField(id="email"),
                    emailpassword.InputFormField(id="password"),
                    # Organization data fields
                    emailpassword.InputFormField(id="firstName", optional=True),
                    emailpassword.InputFormField(id="lastName", optional=True),
                    emailpassword.InputFormField(id="organizationName", optional=True),
                    emailpassword.InputFormField(id="organizationSize", optional=True),
                    emailpassword.InputFormField(id="industry", optional=True),
                    emailpassword.InputFormField(id="country", optional=True),
                    emailpassword.InputFormField(id="city", optional=True),
                ]
            ),
            # Enable custom overrides for full signup flow
            override=emailpassword.InputOverrideConfig(
                apis=lambda original_implementation: EmailPasswordAPIOverride(original_implementation),
            )
        ),
        # Session Recipe with custom configuration
        session.init(
            cookie_domain=None,  # Let browser determine domain
            cookie_same_site="lax",
            session_expired_status_code=401,
            invalid_claim_status_code=403,
        ),
        # Dashboard Recipe for monitoring and management
        dashboard.init(
            # No additional config needed - API key handled by core
        ),
    ]
    
    # Initialize SuperTokens
    init(
        app_info=app_info,
        supertokens_config=supertokens_config,
        recipe_list=recipes,
        framework="fastapi",
        mode="asgi",
    )
    
    logger.info("SuperTokens initialized successfully")


class EmailPasswordAPIOverride(APIInterface):
    """Custom API overrides for EmailPassword recipe."""
    
    def __init__(self, original_implementation: APIInterface):
        super().__init__()
        self.original_implementation = original_implementation
    
    async def email_exists_get(
        self,
        email: str,
        tenant_id: str,
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ) -> EmailExistsGetOkResult:
        """Override email exists check."""
        logger.info(f"Email exists check for: {email}")
        
        # Call the default implementation
        result = await api_options.recipe_implementation.get_user_by_email(
            email, tenant_id, user_context
        )
        
        return EmailExistsGetOkResult(exists=result is not None)
    
    async def sign_up_post(
        self,
        form_fields: List[FormField],
        tenant_id: str,
        session: Union[SessionContainer, None],
        should_try_linking_with_session_user: Union[bool, None],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ) -> Any:
        """Override signup with custom organization creation logic."""
        logger.info("Processing signup request with organization creation")
        
        # Parse form fields
        field_data = {}
        for field in form_fields:
            field_data[field.id] = field.value
        email = field_data.get("email")
        password = field_data.get("password")
        first_name = field_data.get("firstName", "")
        last_name = field_data.get("lastName", "")
        
        # Validate required fields
        if not email or not password:
            return GeneralErrorResponse("Missing required field")
        
        # If no name provided, extract from email
        if not first_name:
            first_name = email.split("@")[0].title()
        if not last_name:
            last_name = "User"
        
        logger.info(f"Processing signup for: {email} ({first_name} {last_name})")
        
        try:
            # First, let SuperTokens create the user
            result = await self.original_implementation.sign_up_post(
                form_fields, tenant_id, session, should_try_linking_with_session_user, api_options, user_context
            )
            
            # If SuperTokens signup was successful, create our database records
            if hasattr(result, 'user'):  # Check if it's a successful result
                organization_name = field_data.get("organizationName", "")
                organization_size = field_data.get("organizationSize", "small")
                industry = field_data.get("industry", "Other")
                country = field_data.get("country", "Saudi Arabia")
                city = field_data.get("city", "")
                
                # Now we have the actual SuperTokens user ID
                supertokens_user_id = result.user.id
                
                await self._create_organization_for_user(
                    supertokens_user_id=supertokens_user_id,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    organization_name=organization_name,
                    organization_size=organization_size,
                    industry=industry,
                    country=country,
                    city=city,
                )
                
                logger.info(f"Successfully created user and organization for {email}")
            
            return result
            
        except ValueError as e:
            logger.error(f"Validation error during signup: {e}")
            return GeneralErrorResponse(str(e))
        except Exception as e:
            logger.error(f"Unexpected error during signup: {e}")
            return GeneralErrorResponse("Signup failed. Please try again.")
    
    async def sign_in_post(
        self,
        form_fields: List[FormField],
        tenant_id: str,
        session: Union[SessionContainer, None],
        should_try_linking_with_session_user: Union[bool, None],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ) -> Any:
        """Override signin with custom user + organization data retrieval."""
        logger.info("Processing signin request with organization data")
        
        # Parse form fields
        field_data = {}
        for field in form_fields:
            field_data[field.id] = field.value
        email = field_data.get("email")
        password = field_data.get("password")
        
        # Validate required fields
        if not email or not password:
            return GeneralErrorResponse("Missing email or password")
        
        logger.info(f"Processing signin for: {email}")
        
        try:
            # 1. Call SuperTokens default signin first
            result = await self.original_implementation.sign_in_post(
                form_fields, tenant_id, session, should_try_linking_with_session_user, api_options, user_context
            )
            
            # 2. If signin was successful, extract user ID and enhance session
            if hasattr(result, 'user'):
                supertokens_user_id = result.user.id
                logger.info(f"SuperTokens signin successful: {supertokens_user_id}")
                
                # 3. Enhance session with user + organization data
                await self._enhance_session_with_user_data(
                    supertokens_user_id=supertokens_user_id,
                    user_context=user_context
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error during signin: {e}")
            return GeneralErrorResponse("Signin failed. Please try again.")
    
    async def _enhance_session_with_user_data(
        self,
        supertokens_user_id: str,
        user_context: Dict[str, Any]
    ) -> None:
        """Enhance session with user and organization data."""
        logger.info(f"Enhancing session for SuperTokens user: {supertokens_user_id}")
        
        try:
            # Get database session
            async for db in get_db():
                # Get user with organization data
                user_data = await auth_service.get_user_with_organization(
                    db, supertokens_user_id=supertokens_user_id
                )
                
                if user_data:
                    # Store user and organization data in session context
                    user_context["user_id"] = str(user_data["user"].id)
                    user_context["organization_id"] = str(user_data["user"].organization_id)
                    user_context["user_role"] = user_data["user"].role
                    user_context["organization_name"] = user_data["organization"].name
                    user_context["permissions"] = user_data["permissions"]
                    
                    logger.info(
                        f"Session enhanced for user {user_data['user'].email} "
                        f"in organization {user_data['organization'].name}"
                    )
                else:
                    logger.warning(f"No user data found for SuperTokens ID: {supertokens_user_id}")
                
                break  # Exit the async generator loop
                
        except Exception as e:
            logger.error(f"Failed to enhance session for user {supertokens_user_id}: {e}")
            # Don't re-raise here as signin was successful, just log the issue
    
    async def _create_organization_for_user(
        self, 
        supertokens_user_id: str,
        email: str, 
        first_name: str,
        last_name: str,
        organization_name: str = "",
        organization_size: str = "small",
        industry: str = "Other",
        country: str = "Saudi Arabia",
        city: str = ""
    ) -> None:
        """Create organization and user record for new signup."""
        logger.info(f"Creating organization for SuperTokens user: {supertokens_user_id}")
        
        try:
            # Get database session
            async for db in get_db():
                # Use provided organization name or generate from email domain
                final_organization_name = organization_name or auth_service.extract_organization_name_from_email(email)
                
                # Map industry string to enum
                industry_type = IndustryType.OTHER
                try:
                    industry_type = IndustryType(industry.lower().replace(" ", "_"))
                except ValueError:
                    industry_type = IndustryType.OTHER
                
                # Create organization and admin user
                user, organization = await auth_service.create_organization_and_admin_user(
                    db,
                    supertokens_user_id=supertokens_user_id,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    organization_name=final_organization_name,
                    industry_type=industry_type,
                    organization_size=organization_size,
                    country=country,
                    city=city,
                )
                
                logger.info(
                    f"Successfully created organization '{organization.name}' "
                    f"with admin user '{user.email}' (ID: {user.id})"
                )
                break  # Exit the async generator loop
                
        except Exception as e:
            logger.error(f"Failed to create organization for user {supertokens_user_id}: {e}")
            # Re-raise to trigger SuperTokens error handling
            raise


def get_supertokens_middleware():
    """Get the SuperTokens middleware for FastAPI."""
    return get_middleware()


async def get_session_info(session: SessionContainer) -> Dict[str, Any]:
    """Extract user and organization info from session."""
    user_id = session.get_user_id()
    session_data = session.get_session_data_from_database()
    
    # TODO: Fetch user and organization data from our database
    # This will be implemented when we integrate the User model
    
    return {
        "user_id": user_id,
        "session_handle": session.get_handle(),
        "session_data": session_data,
    }