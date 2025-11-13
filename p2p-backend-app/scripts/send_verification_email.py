"""
Manual script to send verification email to a specific user
Usage: python scripts/send_verification_email.py <email>
Example: python scripts/send_verification_email.py user@example.com
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import db_manager
from app.core.supertokens import init_supertokens
from app.models.pg_models import User as PGUser
from sqlalchemy import select
from supertokens_python.asyncio import get_user
from supertokens_python.recipe.emailverification.asyncio import is_email_verified
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def send_verification_to_user(email: str):
    """
    Send verification email to a specific user by email
    """
    try:
        # Initialize SuperTokens
        logger.info("Initializing SuperTokens...")
        init_supertokens()

        # Initialize databases
        logger.info("Connecting to databases...")
        await db_manager.init_postgres()
        await db_manager.init_mongodb()

        # Get PostgreSQL session
        async with db_manager.pg_session_factory() as session:
            # Look up user by email
            logger.info(f"Looking up user with email: {email}")
            result = await session.execute(
                select(PGUser).where(PGUser.email == email)
            )
            pg_user = result.scalar_one_or_none()

            if not pg_user:
                logger.error(f"❌ User not found with email: {email}")
                return False

            if not pg_user.supertokens_id:
                logger.error(f"❌ User has no SuperTokens ID: {email}")
                return False

            logger.info(f"✓ Found user: {pg_user.email} (SuperTokens ID: {pg_user.supertokens_id})")

            # Get SuperTokens user to access recipe_user_id
            logger.info("Fetching SuperTokens user data...")
            supertokens_user = await get_user(pg_user.supertokens_id)

            if not supertokens_user:
                logger.error(f"❌ Could not find SuperTokens user for ID: {pg_user.supertokens_id}")
                return False

            # Get the recipe_user_id from the first login method
            if not supertokens_user.login_methods or len(supertokens_user.login_methods) == 0:
                logger.error(f"❌ No login methods found for user: {pg_user.supertokens_id}")
                return False

            recipe_user_id = supertokens_user.login_methods[0].recipe_user_id

            # Check if email is already verified
            logger.info("Checking email verification status...")
            email_verified = await is_email_verified(recipe_user_id)

            if email_verified:
                logger.warning(f"⚠️  Email is already verified for: {email}")
                logger.info("ℹ️  User can log in normally. No verification email needed.")
                return True

            # Create verification token
            logger.info(f"📧 Creating verification token for: {email}")
            from supertokens_python.recipe.emailverification.asyncio import create_email_verification_token
            token_result = await create_email_verification_token("public", recipe_user_id, email)

            if not hasattr(token_result, 'token'):
                logger.error(f"❌ Failed to create verification token for: {email}")
                return False

            # Build verification URL
            from app.core.config import settings
            verification_url = f"{settings.WEBSITE_DOMAIN}/auth/verify-email?token={token_result.token}&tenantId=public"

            # Send using our custom email service
            from app.services.email_verification_service import send_email_verification
            logger.info(f"📧 Sending verification email to: {email}")
            await send_email_verification(
                email=email,
                email_verify_url=verification_url
            )

            logger.info(f"✅ Verification email sent successfully to: {email}")
            logger.info(f"ℹ️  Check the output above for the verification link")
            return True

    except Exception as e:
        logger.error(f"❌ Error sending verification email: {str(e)}", exc_info=True)
        return False
    finally:
        # Close database connections
        await db_manager.close_connections()


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("❌ Error: Email address required")
        print("\nUsage:")
        print("  python scripts/send_verification_email.py <email>")
        print("\nExample:")
        print("  python scripts/send_verification_email.py user@example.com")
        sys.exit(1)

    email = sys.argv[1]

    print("\n" + "="*80)
    print(f"📧 Manual Email Verification Sender")
    print("="*80)
    print(f"Target Email: {email}")
    print("="*80 + "\n")

    success = await send_verification_to_user(email)

    print("\n" + "="*80)
    if success:
        print("✅ Process completed successfully!")
    else:
        print("❌ Process failed. Check the logs above for details.")
    print("="*80 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
