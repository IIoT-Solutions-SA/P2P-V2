"""PeerLink session lifetime enforcement layered on top of SuperTokens.

SuperTokens remains responsible for token issuance, rotation, cookie handling, and
revocation. This module adds application-enforced idle and absolute limits backed
by SuperTokens' shared session database, so multiple backend instances cannot
bypass the policy.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from supertokens_python.recipe.session.exceptions import UnauthorisedError

from app.core.config import settings

logger = logging.getLogger(__name__)

_SECURITY_DATA_KEY = "peerlink_session_security"


def _now_seconds() -> float:
    return time.time()


def _session_created_seconds(created_at_ms: int) -> float:
    return created_at_ms / 1000.0


def configured_idle_timeout_seconds() -> int:
    """Return the production baseline or an explicit isolated-test override."""
    if (
        settings.ENVIRONMENT == "test"
        and settings.SESSION_IDLE_TIMEOUT_SECONDS_TEST is not None
    ):
        return settings.SESSION_IDLE_TIMEOUT_SECONDS_TEST
    return settings.SESSION_IDLE_TIMEOUT_MINUTES * 60


def configured_absolute_lifetime_seconds() -> int:
    """Return the production baseline or an explicit isolated-test override."""
    if (
        settings.ENVIRONMENT == "test"
        and settings.SESSION_ABSOLUTE_LIFETIME_SECONDS_TEST is not None
    ):
        return settings.SESSION_ABSOLUTE_LIFETIME_SECONDS_TEST
    return settings.SESSION_ABSOLUTE_LIFETIME_HOURS * 3600


def session_expiry_reason(
    *,
    now: float,
    created_at: float,
    last_activity_at: float,
    idle_timeout_seconds: int,
    absolute_lifetime_seconds: int,
) -> Optional[str]:
    """Return the policy limit exceeded by a session, if any."""
    if now - created_at >= absolute_lifetime_seconds:
        return "absolute"
    if now - last_activity_at >= idle_timeout_seconds:
        return "idle"
    return None


async def enforce_session_limits(
    session_container: Any,
    user_context: Optional[Dict[str, Any]] = None,
    *,
    now: Optional[float] = None,
) -> None:
    """Revoke expired sessions and periodically persist authenticated activity."""
    context = user_context or {}
    checked_at = _now_seconds() if now is None else now
    created_at = _session_created_seconds(
        await session_container.get_time_created(context)
    )
    session_data = dict(
        await session_container.get_session_data_from_database(context) or {}
    )
    security_data = dict(session_data.get(_SECURITY_DATA_KEY) or {})

    # Existing sessions created before this control was deployed have no activity
    # marker. Treat creation as their last known activity and fail closed.
    last_activity_at = float(security_data.get("last_activity_at", created_at))
    reason = session_expiry_reason(
        now=checked_at,
        created_at=created_at,
        last_activity_at=last_activity_at,
        idle_timeout_seconds=configured_idle_timeout_seconds(),
        absolute_lifetime_seconds=configured_absolute_lifetime_seconds(),
    )

    if reason is not None:
        await session_container.revoke_session(context)
        logger.info(
            "Revoked session %s after %s lifetime limit",
            session_container.get_handle(),
            reason,
        )
        raise UnauthorisedError("Session expired. Please sign in again.", True)

    security_data.update(
        {
            "policy_version": 1,
            "last_activity_at": checked_at,
            "idle_timeout_minutes": settings.SESSION_IDLE_TIMEOUT_MINUTES,
            "absolute_lifetime_hours": settings.SESSION_ABSOLUTE_LIFETIME_HOURS,
        }
    )
    session_data[_SECURITY_DATA_KEY] = security_data
    await session_container.update_session_data_in_database(session_data, context)


def session_functions_override(original_implementation: Any) -> Any:
    """Install creation, verification, and refresh enforcement hooks."""
    original_create_new_session = original_implementation.create_new_session
    original_get_session = original_implementation.get_session
    original_refresh_session = original_implementation.refresh_session

    async def create_new_session(
        user_id,
        recipe_user_id,
        access_token_payload,
        session_data_in_database,
        disable_anti_csrf,
        tenant_id,
        user_context,
    ):
        now = _now_seconds()
        database_data = dict(session_data_in_database or {})
        database_data[_SECURITY_DATA_KEY] = {
            "policy_version": 1,
            "last_activity_at": now,
            "idle_timeout_minutes": settings.SESSION_IDLE_TIMEOUT_MINUTES,
            "absolute_lifetime_hours": settings.SESSION_ABSOLUTE_LIFETIME_HOURS,
        }
        return await original_create_new_session(
            user_id,
            recipe_user_id,
            access_token_payload,
            database_data,
            disable_anti_csrf,
            tenant_id,
            user_context,
        )

    async def get_session(
        access_token,
        anti_csrf_token=None,
        anti_csrf_check=None,
        session_required=None,
        check_database=None,
        override_global_claim_validators=None,
        user_context=None,
    ):
        result = await original_get_session(
            access_token,
            anti_csrf_token,
            anti_csrf_check,
            session_required,
            check_database,
            override_global_claim_validators,
            user_context,
        )
        if result is not None:
            await enforce_session_limits(result, user_context)
        return result

    async def refresh_session(
        refresh_token,
        anti_csrf_token,
        disable_anti_csrf,
        user_context,
    ):
        result = await original_refresh_session(
            refresh_token,
            anti_csrf_token,
            disable_anti_csrf,
            user_context,
        )
        await enforce_session_limits(result, user_context)
        return result

    original_implementation.create_new_session = create_new_session
    original_implementation.get_session = get_session
    original_implementation.refresh_session = refresh_session
    return original_implementation
