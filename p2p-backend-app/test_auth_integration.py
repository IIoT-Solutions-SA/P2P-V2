"""Pytest-based integration tests for authentication system."""

import pytest
from typing import Dict, Any

from app.services.auth import auth_service
from app.services.password_reset import password_reset_service
from app.services.email_verification import email_verification_service
from app.crud.user import user as user_crud
from app.models.enums import UserRole, UserStatus
from app.core.rbac import get_user_permissions


class TestAuthenticationIntegration:
    """Integration tests for the complete authentication system."""
    
    @pytest.mark.asyncio
    async def test_complete_user_signup_flow(self, db_session, test_user_data):
        """Test complete user signup flow."""
        # Create organization and admin user
        user, organization = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id=test_user_data["supertokens_user_id"],
            email=test_user_data["email"],
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            organization_name=test_user_data["organization_name"],
        )
        
        # Assert user was created correctly
        assert user is not None
        assert user.email == test_user_data["email"]
        assert user.role == UserRole.ADMIN
        assert user.status == UserStatus.ACTIVE
        assert not user.email_verified  # Should start unverified
        
        # Assert organization was created correctly
        assert organization is not None
        assert organization.name == test_user_data["organization_name"]
        assert user.organization_id == organization.id
    
    @pytest.mark.asyncio
    async def test_user_permissions_system(self, db_session, test_user_data):
        """Test user permissions and RBAC system."""
        # Create admin user
        admin_user, _ = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id=f"{test_user_data['supertokens_user_id']}_admin",
            email=f"admin.{test_user_data['email']}",
            first_name="Admin",
            last_name="User",
            organization_name=f"Admin {test_user_data['organization_name']}",
        )
        
        # Create member user
        member_user = await user_crud.create_user(
            db=db_session,
            email=f"member.{test_user_data['email']}",
            first_name="Member",
            last_name="User",
            role=UserRole.MEMBER,
            status=UserStatus.ACTIVE,
            organization_id=admin_user.organization_id,
            supertokens_user_id=f"{test_user_data['supertokens_user_id']}_member"
        )
        
        # Test admin permissions
        admin_permissions = get_user_permissions(admin_user.role)
        assert "MANAGE_USERS" in admin_permissions
        assert "DELETE_ANY_CONTENT" in admin_permissions
        assert len(admin_permissions) > 10  # Admin should have many permissions
        
        # Test member permissions
        member_permissions = get_user_permissions(member_user.role)
        assert "MANAGE_USERS" not in member_permissions
        assert "DELETE_ANY_CONTENT" not in member_permissions
        assert "VIEW_USERS" in member_permissions  # Basic permission
        assert len(member_permissions) < len(admin_permissions)
    
    @pytest.mark.asyncio
    async def test_password_reset_flow(self, db_session, test_user_data):
        """Test password reset functionality."""
        # Create user for testing
        user, _ = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id=f"{test_user_data['supertokens_user_id']}_pwd",
            email=f"password.{test_user_data['email']}",
            first_name="Password",
            last_name="Test",
            organization_name=f"Password {test_user_data['organization_name']}",
        )
        
        # Test password reset request
        reset_result = await password_reset_service.request_password_reset(
            db=db_session,
            email=user.email
        )
        
        assert reset_result["success"] is True
        
        # Test password validation
        weak_password = "weak"
        strong_password = "Strong123!"
        
        weak_result = password_reset_service._validate_password(weak_password)
        strong_result = password_reset_service._validate_password(strong_password)
        
        assert weak_result["valid"] is False
        assert strong_result["valid"] is True
    
    @pytest.mark.asyncio
    async def test_email_verification_flow(self, db_session, test_user_data):
        """Test email verification functionality."""
        # Create user for testing
        user, _ = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id=f"{test_user_data['supertokens_user_id']}_email",
            email=f"email.{test_user_data['email']}",
            first_name="Email",
            last_name="Test",
            organization_name=f"Email {test_user_data['organization_name']}",
        )
        
        # Test email verification request
        verify_result = await email_verification_service.send_verification_email(
            db=db_session,
            user_id=user.supertokens_user_id,
            email=user.email
        )
        
        # Should succeed in creating verification request
        assert verify_result["success"] is True
        
        # User should still be unverified
        assert not user.email_verified
    
    @pytest.mark.asyncio
    async def test_organization_user_management(self, db_session, test_user_data):
        """Test organization-level user management."""
        # Create organization with admin
        admin_user, organization = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id=f"{test_user_data['supertokens_user_id']}_org_admin",
            email=f"org.admin.{test_user_data['email']}",
            first_name="Org",
            last_name="Admin",
            organization_name=f"Org {test_user_data['organization_name']}",
        )
        
        # Add multiple users to the organization
        for i in range(3):
            await user_crud.create_user(
                db=db_session,
                email=f"user{i}.{test_user_data['email']}",
                first_name=f"User{i}",
                last_name="Test",
                role=UserRole.MEMBER,
                status=UserStatus.ACTIVE,
                organization_id=organization.id,
                supertokens_user_id=f"{test_user_data['supertokens_user_id']}_user{i}"
            )
        
        # Test organization user listing
        org_users = await user_crud.get_users_by_organization(
            db_session, organization_id=organization.id
        )
        
        assert len(org_users) == 4  # 1 admin + 3 members
        
        # Test that all users belong to the same organization
        for user in org_users:
            assert user.organization_id == organization.id
    
    @pytest.mark.asyncio
    async def test_user_status_and_activity(self, db_session, test_user_data):
        """Test user status and activity management."""
        # Create user
        user, _ = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id=f"{test_user_data['supertokens_user_id']}_status",
            email=f"status.{test_user_data['email']}",
            first_name="Status",
            last_name="Test",
            organization_name=f"Status {test_user_data['organization_name']}",
        )
        
        # Test active user
        assert user.is_active is True
        assert user.status == UserStatus.ACTIVE
        
        # Test user properties
        assert user.full_name == "Status Test"
        assert user.is_admin is True  # Created as admin
        assert user.can_manage_users() is True
        assert user.can_create_content() is True
    
    @pytest.mark.asyncio
    async def test_error_handling_and_edge_cases(self, db_session, test_user_data):
        """Test error handling and edge cases."""
        # Test duplicate email handling
        with pytest.raises(Exception):  # Should raise integrity error
            # Create first user
            await auth_service.create_organization_and_admin_user(
                db=db_session,
                supertokens_user_id=f"{test_user_data['supertokens_user_id']}_dup1",
                email="duplicate@test.com",
                first_name="First",
                last_name="User",
                organization_name="First Organization",
            )
            
            # Try to create second user with same email
            await auth_service.create_organization_and_admin_user(
                db=db_session,
                supertokens_user_id=f"{test_user_data['supertokens_user_id']}_dup2",
                email="duplicate@test.com",  # Same email
                first_name="Second",
                last_name="User",
                organization_name="Second Organization",
            )
        
        # Test non-existent user lookup
        non_existent = await user_crud.get_by_email(db_session, email="nonexistent@test.com")
        assert non_existent is None
        
        # Test password reset for non-existent user (should not reveal)
        reset_result = await password_reset_service.request_password_reset(
            db=db_session,
            email="nonexistent@test.com"
        )
        
        # Should return success but not actually send email (email enumeration protection)
        assert reset_result["success"] is True
        assert reset_result.get("email_sent", True) is False


@pytest.mark.asyncio
async def test_comprehensive_auth_system_integration(db_session, auth_test_config):
    """Comprehensive integration test covering the entire authentication system."""
    test_results = []
    
    # Test 1: Complete user journey
    try:
        user, organization = await auth_service.create_organization_and_admin_user(
            db=db_session,
            supertokens_user_id="comprehensive_test_user",
            email=f"comprehensive{auth_test_config['test_email_domain']}",
            first_name="Comprehensive",
            last_name="Test",
            organization_name=f"{auth_test_config['organization_prefix']} Comprehensive",
        )
        
        test_results.append(("User Creation", True, "User and organization created"))
        
        # Test permissions
        permissions = get_user_permissions(user.role)
        test_results.append(("Permissions", len(permissions) > 0, f"User has {len(permissions)} permissions"))
        
        # Test password reset
        reset_result = await password_reset_service.request_password_reset(
            db=db_session,
            email=user.email
        )
        test_results.append(("Password Reset", reset_result["success"], "Password reset request"))
        
        # Test email verification
        verify_result = await email_verification_service.send_verification_email(
            db=db_session,
            user_id=user.supertokens_user_id,
            email=user.email
        )
        test_results.append(("Email Verification", verify_result["success"], "Email verification request"))
        
    except Exception as e:
        test_results.append(("Comprehensive Test", False, f"Failed: {str(e)}"))
    
    # Assert all tests passed
    for test_name, success, message in test_results:
        assert success, f"{test_name} failed: {message}"
    
    # Final assertion: All components working together
    assert len(test_results) == 4  # All 4 tests completed
    assert all(result[1] for result in test_results)  # All tests passed