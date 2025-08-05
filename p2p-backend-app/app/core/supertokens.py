"""
SuperTokens initialization and configuration for P2P Sandbox authentication.
"""

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.emailpassword import InputFormField
from app.core.config import settings


def init_supertokens():
    """Initialize SuperTokens with email/password authentication."""
    
    init(
        app_info=InputAppInfo(
            app_name="P2P Sandbox for SMEs",  
            api_domain=settings.API_DOMAIN,
            website_domain=settings.WEBSITE_DOMAIN,
            api_base_path="/api/v1/auth",  # Back to /api/v1/auth to match our working CORS
            website_base_path="/auth"
        ),
        supertokens_config=SupertokensConfig(
            # SuperTokens service running in Docker container
            connection_uri=settings.SUPERTOKENS_CONNECTION_URI,
        ),
        framework='fastapi',
        recipe_list=[
            # Email/Password authentication with additional fields
            emailpassword.init(
                sign_up_feature=emailpassword.InputSignUpFeature(
                    form_fields=[
                        InputFormField(id="email"),
                        InputFormField(id="password"),
                        InputFormField(
                            id="firstName",
                            optional=False,
                        ),
                        InputFormField(
                            id="lastName", 
                            optional=False,
                        ),
                    ]
                )
            ),
            # Session management with cookie configuration
            session.init(
                cookie_domain=settings.COOKIE_DOMAIN,
                cookie_same_site="lax",
                cookie_secure=settings.ENVIRONMENT == "production"
            )
        ],
        mode='asgi',
        telemetry=False
    )