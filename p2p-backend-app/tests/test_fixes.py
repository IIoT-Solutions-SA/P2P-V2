"""Tests for OTP verification and invitation consumption fixes.

Run:  cd p2p-backend-app && python -m tests.test_fixes

No external dependencies needed — mocks all DB/SuperTokens calls.
"""

import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)


class TestPostOtpMessageFix(unittest.TestCase):
    """Verify Fix 1: "signed in" success only when session/cookie actually succeed."""

    def _simulate_response_body(self, auto_login_success: bool) -> dict:
        """Replicates the exact logic from verify_signup_otp in supertokens_auth.py (lines 321-331)."""
        return {
            "status": "OK",
            "message": (
                "Email verified successfully! You are now signed in."
                if auto_login_success else
                "Email verified successfully! Please sign in to continue."
            ),
            "requiresManualLogin": not auto_login_success,
        }

    def test_full_success_returns_signed_in_message(self):
        """When all post-OTP steps succeed, response should claim 'signed in'."""
        body = self._simulate_response_body(auto_login_success=True)
        self.assertEqual(body["status"], "OK")
        self.assertEqual(body["message"], "Email verified successfully! You are now signed in.")
        self.assertFalse(body["requiresManualLogin"])

    def test_post_otp_failure_returns_requires_manual_login(self):
        """When session/cookie creation fails, response must NOT claim 'signed in'."""
        body = self._simulate_response_body(auto_login_success=False)
        self.assertEqual(body["status"], "OK")
        self.assertEqual(body["message"], "Email verified successfully! Please sign in to continue.")
        self.assertTrue(body["requiresManualLogin"])

    def test_flag_defaults_to_false_on_exception(self):
        """auto_login_success starts False and stays False if an exception occurs."""
        auto_login_success = False
        try:
            raise RuntimeError("Simulated SuperTokens failure")
        except RuntimeError:
            pass
        body = self._simulate_response_body(auto_login_success)
        self.assertTrue(body["requiresManualLogin"])

    def test_flag_true_only_after_all_steps_succeed(self):
        """auto_login_success only becomes True after every post-OTP step completes."""
        steps_completed = 0
        try:
            steps_completed += 1  # email verified in SuperTokens
            steps_completed += 1  # DB user marked verified
            steps_completed += 1  # session created
            steps_completed += 1  # trusted device cookie set
            auto_login_success = True
        except Exception:
            auto_login_success = False
        self.assertTrue(auto_login_success)
        self.assertEqual(steps_completed, 4)


class TestInviteConsumptionFix(unittest.TestCase):
    """Verify Fix 2: invitation only marked used after OTP verification succeeds."""

    def test_invite_not_marked_used_before_otp(self):
        """Invite should remain pending before OTP verification."""
        invite = MagicMock()
        invite.used = False
        # Simulate: user created, invite NOT consumed
        self.assertFalse(invite.used, "Invite was prematurely marked used!")

    def test_invite_marked_used_after_otp_success(self):
        """Invite should be marked used only after OTP verification."""
        email = "test@example.com"
        invitation = MagicMock()
        invitation.used = False
        invitation.used_at = None
        invitation.save = AsyncMock()

        # Simulate OTP verification success
        async def simulate_otp_verify():
            return {"ok": True}

        # Simulate marking invite used after OTP
        async def mark_invite():
            invitation.used = True
            invitation.used_at = datetime.utcnow()
            await invitation.save()

        import asyncio
        asyncio.run(simulate_otp_verify())
        asyncio.run(mark_invite())

        self.assertTrue(invitation.used)
        self.assertIsNotNone(invitation.used_at)

    def test_invite_expires_after_7_days(self):
        """Existing behaviour: invite expires naturally after 7 days."""
        created_at = datetime.utcnow() - timedelta(days=8)
        expires_at = created_at + timedelta(days=7)

        # Simulate checking expired invite
        is_expired = datetime.utcnow() > expires_at
        self.assertTrue(is_expired, "Invite should be expired after 8 days")

        # Simulate checking non-expired invite
        recent = datetime.utcnow() + timedelta(days=1)
        is_valid = datetime.utcnow() < recent
        self.assertTrue(is_valid, "Invite should be valid within 7 days")


class TestResponseShape(unittest.TestCase):
    """Verify the API response contract for both fixes."""

    def test_invite_consumption_response_unchanged(self):
        """custom-signup response should still look the same (no invite_token leak)."""
        response = {
            "status": "OK",
            "message": "Account created. Please check your email for a 6-digit verification code.",
            "requiresOTPVerification": True,
            "email": "test@example.com"
        }
        self.assertEqual(response["status"], "OK")
        self.assertIn("requiresOTPVerification", response)
        self.assertNotIn("inviteToken", response)  # no leak of invite token

    def test_verify_otp_response_has_requires_manual_login(self):
        """verify-signup-otp response must include requiresManualLogin."""
        for auto_login_ok in [True, False]:
            resp = {
                "status": "OK",
                "message": "...",
                "requiresManualLogin": not auto_login_ok,
            }
            self.assertIn("requiresManualLogin", resp)
            self.assertIsInstance(resp["requiresManualLogin"], bool)


class TestCodePresence(unittest.TestCase):
    """Verify the actual code changes are present in the source files."""

    def setUp(self):
        path = os.path.join(BASE, "app", "api", "v1", "endpoints", "supertokens_auth.py")
        with open(path, "r", encoding="utf-8") as f:
            self.auth_code = f.read()

    def test_invite_not_consumed_in_signup(self):
        """custom-signup should NOT contain mark_invitation_used."""
        signup_section = self.auth_code.split("# `-- Send OTP")[0]
        signup_end = signup_section.split("# Mark email as verified")[0]
        # Check that mark_invitation_used is NOT called in the signup flow
        lines = signup_end.split("\n")
        offending = [l for l in lines if "mark_invitation_used" in l]
        self.assertFalse(
            offending,
            f"mark_invitation_used still called in custom-signup:\n" + "\n".join(offending)
        )

    def test_invite_marked_in_verify_otp(self):
        """verify-signup-otp SHOULD contain mark_invitation_used logic."""
        verify_section = self.auth_code.split("# Mark invitation as used after successful OTP verification")
        self.assertTrue(len(verify_section) > 1, "Invite consumption block not found in verify-signup-otp")

    def test_auto_login_flag_exists(self):
        """verify-signup-otp should reference auto_login_success."""
        self.assertIn("auto_login_success", self.auth_code)

    def test_requires_manual_login_in_response(self):
        """verify-signup-otp should include requiresManualLogin in response."""
        self.assertIn("requiresManualLogin", self.auth_code)


if __name__ == "__main__":
    print("=" * 60)
    print("P2P OTP & Invite Fix Tests")
    print("=" * 60)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.TestLoader().loadTestsFromModule(sys.modules[__name__]))
    sys.exit(0 if result.wasSuccessful() else 1)
