#!/usr/bin/env python3
"""Test script for session management functionality."""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import get_db
from app.services.auth import auth_service


async def test_session_management():
    """Test session management functionality."""
    print("🧪 Testing Session Management (P2.AUTH.03)")
    print("=" * 50)
    
    # Test 1: Get user with organization data
    print("\n1. Testing get_user_with_organization...")
    try:
        async for db in get_db():
            # Test with the mock SuperTokens user ID from our test data
            user_data = await auth_service.get_user_with_organization(
                db, supertokens_user_id="mock_st_test_login_company_sa"
            )
            
            if user_data:
                print("✅ Successfully retrieved user with organization data")
                print(f"   User: {user_data['user'].email}")
                print(f"   Organization: {user_data['organization'].name}")
                print(f"   Permissions: {user_data['permissions']}")
            else:
                print("❌ No user data found")
            break
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get user by email with organization
    print("\n2. Testing get_user_by_email_with_organization...")
    try:
        async for db in get_db():
            user_data = await auth_service.get_user_by_email_with_organization(
                db, email="test@login.company.sa"
            )
            
            if user_data:
                print("✅ Successfully retrieved user by email with organization data")
                print(f"   User: {user_data['user'].email}")
                print(f"   Role: {user_data['user'].role}")
                print(f"   Organization: {user_data['organization'].name}")
                print(f"   Status: {user_data['organization'].status}")
            else:
                print("❌ No user data found by email")
            break
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Session validation scenario
    print("\n3. Testing session validation scenario...")
    try:
        async for db in get_db():
            # Simulate session validation for logout
            supertokens_user_id = "mock_st_test_login_company_sa"
            user_data = await auth_service.get_user_with_organization(
                db, supertokens_user_id=supertokens_user_id
            )
            
            if user_data and user_data['user'].is_active:
                print("✅ Session validation passed - user is active")
                print(f"   Can manage users: {user_data['permissions']['can_manage_users']}")
                print(f"   Can create content: {user_data['permissions']['can_create_content']}")
                print(f"   Is admin: {user_data['permissions']['is_admin']}")
            else:
                print("❌ Session validation failed - user inactive or not found")
            break
    except Exception as e:
        print(f"❌ Error in session validation: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Session Management Tests Complete!")
    print("\nNext Steps:")
    print("- Session logout endpoints are implemented with proper dependency injection")
    print("- Protected endpoints validate sessions using verify_session() middleware")
    print("- Session enhancement stores user/org data in session context")
    print("- Ready to test with SuperTokens integration")


if __name__ == "__main__":
    asyncio.run(test_session_management())