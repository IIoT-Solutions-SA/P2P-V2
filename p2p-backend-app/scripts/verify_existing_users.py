#!/usr/bin/env python3
"""
Script to mark all existing users as email verified.
This is needed for users created before email verification was implemented.
"""
import asyncio
import sys
import os
import asyncpg

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import setup_logging

async def verify_existing_users():
    """Mark all existing users as email verified in SuperTokens."""
    logger = setup_logging()

    try:
        # Connect to SuperTokens database
        conn = await asyncpg.connect(
            user='p2p_user',
            password='iiot123',
            database='supertokens',
            host='postgres',
            port=5432
        )

        logger.info("🔐 Marking all existing users as email verified...")

        # Insert verification records for all users who don't have one
        result = await conn.execute("""
            INSERT INTO emailverification_verified_emails (app_id, user_id, email)
            SELECT 'public', user_id, email
            FROM emailpassword_users
            WHERE user_id NOT IN (SELECT user_id FROM emailverification_verified_emails)
            ON CONFLICT DO NOTHING
        """)

        # Count total verified users
        verified_count = await conn.fetchval(
            "SELECT COUNT(*) FROM emailverification_verified_emails"
        )

        await conn.close()

        logger.info(f"✅ Total verified users: {verified_count}")
        return verified_count

    except Exception as e:
        logger.error(f"❌ Failed to verify existing users: {e}")
        raise

if __name__ == "__main__":
    print("🔐 Starting email verification for existing users...")
    count = asyncio.run(verify_existing_users())
    print(f"✅ Verified {count} users successfully!")
