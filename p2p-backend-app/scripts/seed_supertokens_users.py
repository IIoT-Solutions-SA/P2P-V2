#!/usr/bin/env python3
"""
Create SuperTokens users for seeded database users.
This script creates actual SuperTokens users for all our seeded users so they can login.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from supertokens_python.recipe.emailpassword.asyncio import sign_up
from supertokens_python.recipe.emailpassword.interfaces import EmailAlreadyExistsError
from app.db.session import AsyncSessionLocal
from app.models.user import User

# Import and initialize SuperTokens
from app.core.supertokens import init_supertokens

# Default password for all seeded users (this is for development/testing only)
DEFAULT_PASSWORD = "TestPassword123!"

async def get_seeded_users():
    """Get all users that need SuperTokens accounts."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.supertokens_user_id.like('st-%'))  # Fake SuperTokens IDs start with 'st-'
        )
        users = result.scalars().all()
        return users

async def create_supertokens_user(user: User) -> tuple[bool, str]:
    """Create a SuperTokens user for a database user."""
    try:
        # Attempt to create SuperTokens user
        response = await sign_up("public", user.email, DEFAULT_PASSWORD)
        
        if isinstance(response, EmailAlreadyExistsError):
            print(f"  ⚠️  User already exists in SuperTokens: {user.email}")
            return False, "Email already exists"
        
        # Success - update our database with the real SuperTokens user ID
        # The response structure is SignUpOkResult which has a 'user' attribute
        if hasattr(response, 'user') and hasattr(response.user, 'user_id'):
            real_supertokens_id = response.user.user_id
        elif hasattr(response, 'user') and hasattr(response.user, 'id'):
            real_supertokens_id = response.user.id
        else:
            # Debug the actual response structure
            print(f"  🔍 Debug: response type = {type(response)}")
            print(f"  🔍 Debug: response attributes = {dir(response)}")
            if hasattr(response, 'user'):
                print(f"  🔍 Debug: user type = {type(response.user)}")
                print(f"  🔍 Debug: user attributes = {dir(response.user)}")
            return False, "Could not extract user ID from response"
        
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(supertokens_user_id=real_supertokens_id)
            )
            await session.commit()
        
        print(f"  ✅ Created SuperTokens user: {user.email} -> {real_supertokens_id}")
        return True, real_supertokens_id
        
    except Exception as e:
        print(f"  ❌ Failed to create SuperTokens user {user.email}: {e}")
        return False, str(e)

async def create_all_supertokens_users():
    """Create SuperTokens users for all seeded users."""
    print("🔐 Creating SuperTokens users for seeded database users...")
    
    # Get users that need SuperTokens accounts
    users = await get_seeded_users()
    
    if not users:
        print("  ℹ️  No users found that need SuperTokens accounts")
        return True
    
    print(f"  📋 Found {len(users)} users that need SuperTokens accounts")
    print(f"  🔑 Default password for all users: {DEFAULT_PASSWORD}")
    print()
    
    successful_creations = 0
    failed_creations = 0
    
    for user in users:
        print(f"Creating SuperTokens account for: {user.full_name} ({user.email})")
        success, result = await create_supertokens_user(user)
        
        if success:
            successful_creations += 1
        else:
            failed_creations += 1
    
    print()
    print(f"📊 SuperTokens User Creation Summary:")
    print(f"  ✅ Successful: {successful_creations}")
    print(f"  ❌ Failed: {failed_creations}")
    
    if failed_creations > 0:
        print(f"  ⚠️  Some users may already exist or there were errors")
    
    return failed_creations == 0

async def verify_supertokens_users():
    """Verify that all users now have real SuperTokens accounts."""
    print("\n🔍 Verifying SuperTokens user creation...")
    
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
    print("🚀 SuperTokens User Creation Script")
    print("=" * 50)
    print(f"This script creates actual SuperTokens users for all seeded database users")
    print(f"so they can login with password: {DEFAULT_PASSWORD}")
    print()
    
    try:
        # Initialize SuperTokens
        print("🔧 Initializing SuperTokens...")
        init_supertokens()
        print("  ✅ SuperTokens initialized")
        print()
        # Create SuperTokens users
        success = await create_all_supertokens_users()
        
        if not success:
            print("❌ Some SuperTokens user creations failed!")
            return False
        
        # Verify the results
        verification_success = await verify_supertokens_users()
        
        if verification_success:
            print("\n🎉 All users now have SuperTokens accounts and can login!")
            print(f"💡 Login credentials:")
            print(f"   Email: Use any seeded user email (e.g., sarah.ahmed@advanced-electronics.sa)")
            print(f"   Password: {DEFAULT_PASSWORD}")
        else:
            print("\n⚠️  Some users still don't have proper SuperTokens accounts")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Script failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Starting SuperTokens user creation...")
    
    success = asyncio.run(main())
    
    if success:
        print("\n✅ SuperTokens user creation completed successfully!")
    else:
        print("\n❌ SuperTokens user creation failed!")
        sys.exit(1)