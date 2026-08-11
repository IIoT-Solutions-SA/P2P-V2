"""Distributed failed-login protection for the password authentication flow."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.pg_models import LoginAttempt


GENERIC_AUTH_MESSAGE = "Invalid email or password. Please try again later."


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def lockout_duration() -> timedelta:
    if settings.ENVIRONMENT == "test" and settings.LOGIN_LOCKOUT_SECONDS_TEST is not None:
        return timedelta(seconds=settings.LOGIN_LOCKOUT_SECONDS_TEST)
    return timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)


def identity_key(email: str) -> str:
    """Return a stable, non-plaintext account key shared by all backend instances."""
    normalized = email.strip().lower().encode("utf-8")
    secret = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(secret, normalized, hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class ProtectionState:
    blocked: bool
    retry_after_seconds: int = 0


async def get_protection_state(
    db: AsyncSession,
    email: str,
    *,
    now: datetime | None = None,
) -> ProtectionState:
    current_time = now or _now_utc()
    record = await db.get(LoginAttempt, identity_key(email))
    if not record or not record.locked_until or record.locked_until <= current_time:
        return ProtectionState(blocked=False)

    retry_after = max(1, int((record.locked_until - current_time).total_seconds()))
    return ProtectionState(blocked=True, retry_after_seconds=retry_after)


async def record_failed_attempt(
    db: AsyncSession,
    email: str,
    *,
    now: datetime | None = None,
) -> ProtectionState:
    """Atomically increment failures and lock at the configured threshold."""
    current_time = now or _now_utc()
    key = identity_key(email)

    # Ensure the row exists, then serialize updates for this account across all
    # application instances. PostgreSQL's conflict handling closes the initial
    # concurrent-insert race without storing the plaintext email address.
    await db.execute(
        insert(LoginAttempt)
        .values(identity_key=key, failed_attempts=0)
        .on_conflict_do_nothing(index_elements=[LoginAttempt.identity_key])
    )
    result = await db.execute(
        select(LoginAttempt).where(LoginAttempt.identity_key == key).with_for_update()
    )
    record = result.scalar_one()

    # A completed lockout window starts a fresh consecutive-attempt sequence.
    if record.locked_until and record.locked_until <= current_time:
        record.failed_attempts = 0
        record.locked_until = None

    if record.locked_until and record.locked_until > current_time:
        retry_after = max(1, int((record.locked_until - current_time).total_seconds()))
        await db.commit()
        return ProtectionState(blocked=True, retry_after_seconds=retry_after)

    record.failed_attempts += 1
    record.last_failed_at = current_time

    if record.failed_attempts >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
        duration = lockout_duration()
        record.locked_until = current_time + duration
        retry_after = max(1, int(duration.total_seconds()))
        await db.commit()
        return ProtectionState(blocked=True, retry_after_seconds=retry_after)

    await db.commit()
    return ProtectionState(blocked=False)


async def reset_failed_attempts(db: AsyncSession, email: str) -> None:
    """Clear the consecutive-failure sequence after valid password authentication."""
    record = await db.get(LoginAttempt, identity_key(email))
    if record:
        await db.delete(record)
        await db.commit()
