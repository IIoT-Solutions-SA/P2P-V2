#!/usr/bin/env python3
"""
Link existing SuperTokens users with database users.
This script updates our database users to use real SuperTokens user IDs instead of fake ones.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update, text
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def get_supertokens_users():
    """Get all users from SuperTokens database."""
    # Need to connect to the supertokens database specifically
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    
    # Create connection to supertokens database
    supertokens_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/supertokens"
    engine = create_async_engine(supertokens_url)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        result = await session.execute(
            text("SELECT user_id, email FROM emailpassword_users ORDER BY time_joined")
        )
        return result.fetchall()

async def get_database_users_with_fake_ids():
    """Get all users from our database that have fake SuperTokens IDs."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.supertokens_user_id.like('st-%'))
        )
        return result.scalars().all()

async def link_users():
    """Link SuperTokens users with database users by email."""
    print("🔗 Linking SuperTokens users with database users...")
    
    # Get SuperTokens users
    supertokens_users = await get_supertokens_users()
    print(f"  📋 Found {len(supertokens_users)} users in SuperTokens")
    
    # Create email -> SuperTokens ID mapping
    email_to_supertokens_id = {user.email: user.user_id for user in supertokens_users}
    
    # Get database users with fake IDs
    database_users = await get_database_users_with_fake_ids()
    print(f"  📋 Found {len(database_users)} users with fake SuperTokens IDs in database")
    
    if not database_users:
        print("  ℹ️  No users need linking")
        return True
    
    print()
    
    successful_links = 0
    failed_links = 0
    
    async with AsyncSessionLocal() as session:
        for db_user in database_users:
            email = db_user.email
            fake_id = db_user.supertokens_user_id
            
            if email in email_to_supertokens_id:
                real_supertokens_id = email_to_supertokens_id[email]
                
                # Update database user with real SuperTokens ID
                await session.execute(
                    update(User)
                    .where(User.id == db_user.id)
                    .values(supertokens_user_id=real_supertokens_id)
                )
                
                print(f"  ✅ Linked: {email}")
                print(f"    Old ID: {fake_id}")
                print(f"    New ID: {real_supertokens_id}")
                successful_links += 1
            else:
                print(f"  ❌ No SuperTokens user found for: {email}")
                failed_links += 1
        
        # Commit all updates
        await session.commit()
    
    print()
    print(f"📊 Linking Summary:")
    print(f"  ✅ Successfully linked: {successful_links}")
    print(f"  ❌ Failed to link: {failed_links}")
    
    return failed_links == 0

async def verify_linking():
    """Verify that all users now have real SuperTokens IDs."""
    print("\n🔍 Verifying user linking...")
    
    async with AsyncSessionLocal() as session:
        # Count users with fake SuperTokens IDs
        fake_id_result = await session.execute(
            select(User).where(User.supertokens_user_id.like('st-%'))
        )
        fake_id_users = fake_id_result.scalars().all()
        
        # Count users with real SuperTokens IDs (UUID format)
        real_id_result = await session.execute(
            select(User).where(~User.supertokens_user_id.like('st-%'))
        )
        real_id_users = real_id_result.scalars().all()
        
        print(f"  📋 Users with fake SuperTokens IDs: {len(fake_id_users)}")
        print(f"  📋 Users with real SuperTokens IDs: {len(real_id_users)}")
        
        if fake_id_users:
            print(f"  ⚠️  These users still have fake IDs:")
            for user in fake_id_users[:5]:  # Show first 5
                print(f"    - {user.email} ({user.supertokens_user_id})")
            if len(fake_id_users) > 5:
                print(f"    ... and {len(fake_id_users) - 5} more")
        
        return len(fake_id_users) == 0

async def main():
    """Main function."""
    print("🚀 SuperTokens User Linking Script")
    print("=" * 50)
    print("This script links existing SuperTokens users with database users by email")
    print()
    
    try:
        # Link users
        success = await link_users()
        
        if not success:
            print("❌ Some user linking failed!")
            return False
        
        # Verify the results
        verification_success = await verify_linking()
        
        if verification_success:
            print("\n🎉 All users are now linked with real SuperTokens accounts!")
            print("💡 Users can now login with their existing passwords")
        else:
            print("\n⚠️  Some users still don't have proper SuperTokens linking")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Script failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🔗 Starting SuperTokens user linking...")
    
    success = asyncio.run(main())
    
    if success:
        print("\n✅ SuperTokens user linking completed successfully!")
    else:
        print("\n❌ SuperTokens user linking failed!")
        sys.exit(1)