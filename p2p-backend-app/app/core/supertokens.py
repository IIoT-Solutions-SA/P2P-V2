from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session, emailverification
from supertokens_python.recipe.emailpassword import InputFormField
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryConfig
from app.core.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def custom_email_delivery_override(original_implementation):
    """Custom email delivery for verification emails"""
    original_send_email = original_implementation.send_email

    async def send_email(template_vars, user_context: Dict[str, Any]):
        """Send verification email using our custom service"""
        try:
            from app.services.email_verification_service import send_email_verification

            # Send using our custom email service
            await send_email_verification(
                email=template_vars.user.email,
                email_verify_url=template_vars.email_verify_link
            )
            logger.info(f"Verification email sent to {template_vars.user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            # Fallback to original implementation if custom fails
            await original_send_email(template_vars, user_context)

    original_implementation.send_email = send_email
    return original_implementation


def init_supertokens():
    """Initialize SuperTokens with email/password authentication and email verification."""

    init(
        app_info=InputAppInfo(
            app_name="P2P Sandbox for SMEs",
            api_domain=settings.API_DOMAIN,
            website_domain=settings.WEBSITE_DOMAIN,
            api_base_path="/api/v1/auth",
            website_base_path="/auth"
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.SUPERTOKENS_CONNECTION_URI,
        ),
        framework='fastapi',
        recipe_list=[
            emailpassword.init(
                sign_up_feature=emailpassword.InputSignUpFeature(
                    form_fields=[
                        InputFormField(id="email"),
                        InputFormField(id="password"),
                        InputFormField(id="firstName", optional=False),
                        InputFormField(id="lastName", optional=False),
                        InputFormField(id="companyName", optional=False),
                        InputFormField(id="industrySector", optional=False),
                        InputFormField(id="companySize", optional=False),
                        InputFormField(id="city", optional=False),
                    ]
                )
            ),
            emailverification.init(
                mode="REQUIRED",
                email_delivery=EmailDeliveryConfig(
                    override=custom_email_delivery_override
                )
            ),
            session.init(
                cookie_domain=settings.COOKIE_DOMAIN,
                cookie_same_site="lax",
                cookie_secure=settings.ENVIRONMENT == "production",
                override=session.InputOverrideConfig(
                    functions=lambda original_implementation: original_implementation
                )
            )
        ],
        mode='asgi',
        telemetry=False
    )
