"""
OTP Service — generates, stores (hashed), and verifies 6-digit codes for:
  - signup_verify: email verification after admin signup
  - login_mfa: MFA challenge for first login on a new device

Security properties:
  - Codes are SHA-256 hashed before storage (never stored plaintext)
  - Codes expire after OTP_EXPIRY_MINUTES (configurable, default 7)
  - Max OTP_MAX_ATTEMPTS (default 5) before the code is locked
  - Resend is rate-limited to 1 per OTP_RESEND_COOLDOWN_SECONDS (default 60)
  - Old unused codes for the same (email, purpose) are deleted on new issuance
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from app.models.pg_models import OtpCode, TrustedDevice
from app.core.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _generate_code() -> str:
    """Return a cryptographically random 6-digit string (zero-padded)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_code(code: str) -> str:
    """SHA-256 hex digest of the plaintext code."""
    return hashlib.sha256(code.encode()).hexdigest()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────
# Core service functions
# ─────────────────────────────────────────────

async def create_otp(
    db: AsyncSession,
    email: str,
    purpose: str,
) -> Tuple[str, str]:
    """
    Generate a new 6-digit OTP for (email, purpose), persist it hashed,
    and return (plaintext_code, challenge_id_str).

    Raises ValueError if a recent OTP was issued within the resend cooldown window.
    Deletes any existing unused codes for the same (email, purpose) before inserting.
    """
    now = _now_utc()
    cooldown_cutoff = now - timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS)

    # Check resend rate limit: was an OTP issued within the cooldown window?
    result = await db.execute(
        select(OtpCode).where(
            and_(
                OtpCode.email == email,
                OtpCode.purpose == purpose,
                OtpCode.used == False,  # noqa: E712
                OtpCode.created_at > cooldown_cutoff,
            )
        )
    )
    recent = result.scalars().first()
    if recent:
        seconds_remaining = int(
            (recent.created_at.replace(tzinfo=timezone.utc) + timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS) - now).total_seconds()
        )
        raise ValueError(f"RATE_LIMITED:{seconds_remaining}")

    # Delete old unused codes for this (email, purpose)
    await db.execute(
        delete(OtpCode).where(
            and_(
                OtpCode.email == email,
                OtpCode.purpose == purpose,
                OtpCode.used == False,  # noqa: E712
            )
        )
    )

    # Generate and store new code
    plain_code = _generate_code()
    code_hash = _hash_code(plain_code)
    expires_at = now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

    import uuid as _uuid
    new_otp = OtpCode(
        email=email,
        purpose=purpose,
        code_hash=code_hash,
        challenge_id=_uuid.uuid4(),
        attempts=0,
        expires_at=expires_at,
        used=False,
    )
    db.add(new_otp)
    await db.commit()
    await db.refresh(new_otp)

    logger.info(f"OTP created for {email} purpose={purpose} expires={expires_at}")
    return plain_code, str(new_otp.challenge_id)


async def verify_otp(
    db: AsyncSession,
    email: str,
    code: str,
    purpose: str,
    challenge_id: Optional[str] = None,
) -> dict:
    """
    Verify a submitted OTP code.

    Returns dict with keys:
      - ok (bool)
      - error (str | None): 'OTP_EXPIRED' | 'MAX_ATTEMPTS_REACHED' | 'INVALID_CODE' | 'OTP_NOT_FOUND'
      - attempts_remaining (int | None)
    """
    now = _now_utc()

    # Build query — challenge_id is required for login_mfa, optional for signup_verify
    conditions = [
        OtpCode.email == email,
        OtpCode.purpose == purpose,
        OtpCode.used == False,  # noqa: E712
    ]
    if challenge_id:
        import uuid as _uuid
        try:
            conditions.append(OtpCode.challenge_id == _uuid.UUID(challenge_id))
        except ValueError:
            return {"ok": False, "error": "OTP_NOT_FOUND", "attempts_remaining": None}

    result = await db.execute(select(OtpCode).where(and_(*conditions)))
    otp_row = result.scalars().first()

    if not otp_row:
        logger.warning(f"OTP not found for {email} purpose={purpose}")
        return {"ok": False, "error": "OTP_NOT_FOUND", "attempts_remaining": None}

    # Check expiry
    if otp_row.expires_at.replace(tzinfo=timezone.utc) < now:
        logger.warning(f"Expired OTP attempt for {email}")
        return {"ok": False, "error": "OTP_EXPIRED", "attempts_remaining": None}

    # Check max attempts
    if otp_row.attempts >= settings.OTP_MAX_ATTEMPTS:
        logger.warning(f"Max OTP attempts reached for {email}")
        return {"ok": False, "error": "MAX_ATTEMPTS_REACHED", "attempts_remaining": 0}

    # Verify code
    submitted_hash = _hash_code(code.strip())
    if submitted_hash != otp_row.code_hash:
        otp_row.attempts += 1
        await db.commit()
        remaining = settings.OTP_MAX_ATTEMPTS - otp_row.attempts
        logger.warning(f"Invalid OTP for {email} — {remaining} attempts remaining")
        return {"ok": False, "error": "INVALID_CODE", "attempts_remaining": remaining}

    # Mark used
    otp_row.used = True
    await db.commit()
    logger.info(f"OTP verified successfully for {email} purpose={purpose}")
    return {"ok": True, "error": None, "attempts_remaining": None}


# ─────────────────────────────────────────────
# Trusted Device helpers
# ─────────────────────────────────────────────

async def create_trusted_device(db: AsyncSession, email: str) -> str:
    """
    Create a trusted-device record and return the raw token to be set as cookie.
    """
    token = secrets.token_hex(64)  # 128 hex chars
    expires_at = _now_utc() + timedelta(days=settings.TRUSTED_DEVICE_DAYS)
    device = TrustedDevice(
        user_email=email,
        device_token=token,
        expires_at=expires_at,
    )
    db.add(device)
    await db.commit()
    logger.info(f"Trusted device created for {email} expires={expires_at}")
    return token


async def validate_trusted_device(db: AsyncSession, email: str, token: str) -> bool:
    """
    Return True if the token belongs to email and has not expired.
    """
    if not token:
        return False
    now = _now_utc()
    result = await db.execute(
        select(TrustedDevice).where(
            and_(
                TrustedDevice.user_email == email,
                TrustedDevice.device_token == token,
                TrustedDevice.expires_at > now,
            )
        )
    )
    row = result.scalars().first()
    return row is not None
