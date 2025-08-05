#!/usr/bin/env python3
"""Create test data for development and testing."""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.enums import UserRole, UserStatus, OrganizationStatus, IndustryType


async def create_test_data():
    """Create test data for development and testing."""
    print("🔧 Creating Test Data")
    print("=" * 30)
    
    try:
        async for db in get_db():
            # Create test organization
            print("\n1. Creating test organization...")
            test_org = Organization(
                name="Test Company SA",
                email="info@company.sa",
                phone_number="+966123456789",
                website="https://company.sa",
                description="Test organization for development",
                industry_type=IndustryType.TECHNOLOGY,
                status=OrganizationStatus.TRIAL,
                address_line_1="123 Business District",
                city="Riyadh",
                country="SA",
                registration_number="1234567890",
                company_size="11-50"
            )
            db.add(test_org)
            await db.commit()
            await db.refresh(test_org)
            print(f"✅ Created organization: {test_org.name} (ID: {test_org.id})")
            
            # Create test users
            print("\n2. Creating test users...")
            
            # Test login user (member)
            test_user = User(
                email="test.login@company.sa",
                first_name="Test",
                last_name="User",
                phone_number="+966501234567",
                role=UserRole.MEMBER,
                status=UserStatus.ACTIVE,
                organization_id=test_org.id,
                supertokens_user_id="mock_st_test_login_company_sa",
                bio="Test user for development",
                job_title="Software Developer",
                department="Engineering",
                email_verified=False,  # Start as unverified for testing
                email_notifications_enabled=True,
                forum_notifications_enabled=True,
                message_notifications_enabled=True
            )
            db.add(test_user)
            
            # Admin test user
            admin_user = User(
                email="admin.test@company.sa",
                first_name="Admin",
                last_name="User",
                phone_number="+966501234568",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                organization_id=test_org.id,
                supertokens_user_id="mock_st_admin_test_company_sa",
                bio="Admin test user for development",
                job_title="System Administrator",
                department="IT",
                email_verified=True,  # Admin starts verified
                email_verified_at=datetime.utcnow(),
                email_notifications_enabled=True,
                forum_notifications_enabled=True,
                message_notifications_enabled=True
            )
            db.add(admin_user)
            
            await db.commit()
            await db.refresh(test_user)
            await db.refresh(admin_user)
            
            print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
            print(f"   Role: {test_user.role}, Status: {test_user.status}")
            print(f"   Email verified: {test_user.email_verified}")
            
            print(f"✅ Created admin user: {admin_user.email} (ID: {admin_user.id})")
            print(f"   Role: {admin_user.role}, Status: {admin_user.status}")
            print(f"   Email verified: {admin_user.email_verified}")
            
            print("\n" + "=" * 30)
            print("✅ Test Data Created Successfully!")
            print("\nTest Users Available:")
            print(f"- Member: {test_user.email} (SuperTokens ID: {test_user.supertokens_user_id})")
            print(f"- Admin: {admin_user.email} (SuperTokens ID: {admin_user.supertokens_user_id})")
            print(f"\nOrganization: {test_org.name} (ID: {test_org.id})")
            
            break
            
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_test_data())