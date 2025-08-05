"""Pytest configuration and fixtures for authentication testing."""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


@pytest.fixture(scope="session")  
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    async for session in get_db():
        yield session
        break


@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "email": "pytest.user@testcompany.sa",
        "first_name": "Pytest",
        "last_name": "User",
        "organization_name": "Pytest Test Company",
        "supertokens_user_id": "pytest_test_user"
    }


@pytest.fixture
def test_organization_data():
    """Provide test organization data."""
    return {
        "name": "Pytest Test Organization",
        "email": "info@pytest-test.sa",
        "industry_type": "technology"
    }


@pytest.fixture
def auth_test_config():
    """Provide authentication test configuration."""
    return {
        "test_email_domain": "@pytest-test.sa",
        "organization_prefix": "Pytest Test",
        "user_prefix": "pytest_user",
        "timeout_seconds": 30
    }