"""Unit tests for KACST session idle and absolute lifetime controls.

Run: cd p2p-backend-app && python -m unittest tests.test_session_security
"""

import unittest
from unittest.mock import AsyncMock, patch

from supertokens_python.recipe.session.exceptions import UnauthorisedError

from app.core.session_security import enforce_session_limits, session_expiry_reason


class FakeSession:
    def __init__(self, created_at_seconds: float, session_data=None):
        self.created_at_ms = int(created_at_seconds * 1000)
        self.session_data = session_data or {}
        self.revoked = False
        self.updated_data = None

    async def get_time_created(self, _context):
        return self.created_at_ms

    async def get_session_data_from_database(self, _context):
        return self.session_data

    async def update_session_data_in_database(self, data, _context):
        self.updated_data = data
        self.session_data = data

    async def revoke_session(self, _context):
        self.revoked = True

    def get_handle(self):
        return "test-session-handle"


class TestExpiryCalculation(unittest.TestCase):
    def test_active_session_is_valid(self):
        self.assertIsNone(
            session_expiry_reason(
                now=1_000,
                created_at=500,
                last_activity_at=900,
                idle_timeout_seconds=1_800,
                absolute_lifetime_seconds=28_800,
            )
        )

    def test_idle_limit_expires_at_thirty_minutes(self):
        self.assertEqual(
            session_expiry_reason(
                now=2_800,
                created_at=0,
                last_activity_at=1_000,
                idle_timeout_seconds=1_800,
                absolute_lifetime_seconds=28_800,
            ),
            "idle",
        )

    def test_absolute_limit_expires_at_eight_hours_even_if_active(self):
        self.assertEqual(
            session_expiry_reason(
                now=28_800,
                created_at=0,
                last_activity_at=28_799,
                idle_timeout_seconds=1_800,
                absolute_lifetime_seconds=28_800,
            ),
            "absolute",
        )


class TestSessionEnforcement(unittest.IsolatedAsyncioTestCase):
    @patch("app.core.session_security.settings.SESSION_ABSOLUTE_LIFETIME_HOURS", 8)
    @patch("app.core.session_security.settings.SESSION_IDLE_TIMEOUT_MINUTES", 30)
    async def test_activity_is_persisted_in_shared_session_data(self):
        session = FakeSession(
            created_at_seconds=100,
            session_data={
                "unrelated": "preserved",
                "peerlink_session_security": {
                    "last_activity_at": 1_000,
                },
            },
        )

        await enforce_session_limits(session, now=1_061)

        self.assertFalse(session.revoked)
        self.assertEqual(session.updated_data["unrelated"], "preserved")
        self.assertEqual(
            session.updated_data["peerlink_session_security"]["last_activity_at"],
            1_061,
        )

    @patch("app.core.session_security.settings.SESSION_ABSOLUTE_LIFETIME_HOURS", 8)
    @patch("app.core.session_security.settings.SESSION_IDLE_TIMEOUT_MINUTES", 30)
    async def test_idle_session_is_revoked(self):
        session = FakeSession(
            created_at_seconds=100,
            session_data={
                "peerlink_session_security": {
                    "last_activity_at": 1_000,
                }
            },
        )

        with self.assertRaises(UnauthorisedError):
            await enforce_session_limits(session, now=2_800)

        self.assertTrue(session.revoked)

    @patch("app.core.session_security.settings.SESSION_ABSOLUTE_LIFETIME_HOURS", 8)
    @patch("app.core.session_security.settings.SESSION_IDLE_TIMEOUT_MINUTES", 30)
    async def test_absolute_expiry_cannot_be_extended_by_activity(self):
        session = FakeSession(
            created_at_seconds=100,
            session_data={
                "peerlink_session_security": {
                    "last_activity_at": 28_899,
                }
            },
        )

        with self.assertRaises(UnauthorisedError):
            await enforce_session_limits(session, now=28_900)

        self.assertTrue(session.revoked)

    @patch("app.core.session_security.settings.SESSION_ABSOLUTE_LIFETIME_HOURS", 8)
    @patch("app.core.session_security.settings.SESSION_IDLE_TIMEOUT_MINUTES", 30)
    async def test_legacy_session_fails_closed(self):
        session = FakeSession(created_at_seconds=100, session_data={})

        with self.assertRaises(UnauthorisedError):
            await enforce_session_limits(session, now=1_900)

        self.assertTrue(session.revoked)


if __name__ == "__main__":
    unittest.main()
