"""Unit tests for KACST failed-login protection.

Run: cd p2p-backend-app && python -m unittest tests.test_login_protection
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from app.models.pg_models import LoginAttempt
from app.services.login_protection_service import (
    GENERIC_AUTH_MESSAGE,
    get_protection_state,
    identity_key,
    lockout_duration,
    record_failed_attempt,
    reset_failed_attempts,
)


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one(self):
        return self.value


class TestIdentityProtection(unittest.TestCase):
    def test_identity_key_is_normalized_and_not_plaintext(self):
        first = identity_key(" User@Example.COM ")
        second = identity_key("user@example.com")
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        self.assertNotIn("user@example.com", first)

    @patch("app.services.login_protection_service.settings.LOGIN_LOCKOUT_SECONDS_TEST", 9)
    @patch("app.services.login_protection_service.settings.LOGIN_LOCKOUT_MINUTES", 15)
    @patch("app.services.login_protection_service.settings.ENVIRONMENT", "production")
    def test_production_ignores_accelerated_lockout_override(self):
        self.assertEqual(lockout_duration(), timedelta(minutes=15))

    @patch("app.services.login_protection_service.settings.LOGIN_LOCKOUT_SECONDS_TEST", 9)
    @patch("app.services.login_protection_service.settings.ENVIRONMENT", "test")
    def test_isolated_test_can_accelerate_lockout(self):
        self.assertEqual(lockout_duration(), timedelta(seconds=9))


class TestProtectionState(unittest.IsolatedAsyncioTestCase):
    async def test_active_lock_is_blocked_without_disclosing_attempt_count(self):
        now = datetime(2026, 8, 11, tzinfo=timezone.utc)
        db = AsyncMock()
        db.get.return_value = LoginAttempt(
            identity_key=identity_key("member@example.sa"),
            failed_attempts=5,
            locked_until=now + timedelta(seconds=30),
        )

        state = await get_protection_state(db, "member@example.sa", now=now)

        self.assertTrue(state.blocked)
        self.assertEqual(state.retry_after_seconds, 30)

    async def test_expired_lock_allows_a_new_attempt(self):
        now = datetime(2026, 8, 11, tzinfo=timezone.utc)
        db = AsyncMock()
        db.get.return_value = LoginAttempt(
            identity_key=identity_key("member@example.sa"),
            failed_attempts=5,
            locked_until=now,
        )

        state = await get_protection_state(db, "member@example.sa", now=now)

        self.assertFalse(state.blocked)

    @patch("app.services.login_protection_service.settings.LOGIN_LOCKOUT_MINUTES", 15)
    @patch("app.services.login_protection_service.settings.LOGIN_MAX_FAILED_ATTEMPTS", 5)
    @patch("app.services.login_protection_service.settings.ENVIRONMENT", "production")
    async def test_fifth_consecutive_failure_starts_fifteen_minute_lock(self):
        now = datetime(2026, 8, 11, tzinfo=timezone.utc)
        record = LoginAttempt(
            identity_key=identity_key("admin@example.sa"),
            failed_attempts=4,
        )
        db = AsyncMock()
        db.execute.side_effect = [AsyncMock(), ScalarResult(record)]

        state = await record_failed_attempt(db, "admin@example.sa", now=now)

        self.assertTrue(state.blocked)
        self.assertEqual(state.retry_after_seconds, 900)
        self.assertEqual(record.failed_attempts, 5)
        self.assertEqual(record.locked_until, now + timedelta(minutes=15))
        db.commit.assert_awaited_once()

    async def test_successful_password_authentication_clears_counter(self):
        record = LoginAttempt(
            identity_key=identity_key("member@example.sa"),
            failed_attempts=3,
        )
        db = AsyncMock()
        db.get.return_value = record

        await reset_failed_attempts(db, "member@example.sa")

        db.delete.assert_awaited_once_with(record)
        db.commit.assert_awaited_once()

    def test_generic_message_contains_no_account_or_lockout_detail(self):
        lowered = GENERIC_AUTH_MESSAGE.lower()
        self.assertNotIn("account exists", lowered)
        self.assertNotIn("locked", lowered)
        self.assertNotIn("attempt", lowered)


if __name__ == "__main__":
    unittest.main()
