# KACST Failed-Login Protection

**Date:** 2026-08-11 AST
**Project:** PeerLink / P2P-V2
**Branch:** `feature/kacst-failed-login-protection`
**Classification:** Internal engineering documentation

## Control Baseline

| Control | Production value | Purpose |
|---|---:|---|
| Consecutive password failures | 5 | Activate protection at the upper end of KACST's recommended 3–5 range |
| Lockout duration | 15 minutes | Block additional password verification and materially slow guessing |
| Recovery | Automatic timer | Avoid unsafe manual database edits; correct credentials work after expiry |
| Success behavior | Delete failure record | A valid password starts a fresh consecutive-failure sequence |
| State store | PostgreSQL | Make the counter consistent across backend instances |
| User feedback | Generic | Avoid disclosing whether an account exists or is currently locked |

The production settings are `LOGIN_MAX_FAILED_ATTEMPTS=5` and
`LOGIN_LOCKOUT_MINUTES=15`. `LOGIN_LOCKOUT_SECONDS_TEST` is accepted only when
`ENVIRONMENT=test`; production ignores it.

## Request Flow

1. Normalize the supplied email address.
2. Derive a 64-character HMAC-SHA-256 identity key using the application secret.
3. Read the shared PostgreSQL protection state before password verification.
4. If an active lock exists, do not call SuperTokens password verification. Return the
   generic message with HTTP 429 and `Retry-After`.
5. If SuperTokens reports wrong credentials, atomically increment the shared counter.
6. On the fifth consecutive failure, set `locked_until` and return the same generic
   message with HTTP 429 and `Retry-After`.
7. If password verification succeeds after the timer, delete the counter before
   continuing email-verification, trusted-device, or MFA handling.

## Shared-State and Concurrency Design

The `login_attempts` table contains:

- `identity_key`: HMAC-derived primary key; plaintext email is not stored.
- `failed_attempts`: current consecutive failure count.
- `locked_until`: absolute UTC lock expiry.
- `last_failed_at` and `updated_at`: operational timestamps.

The service first performs PostgreSQL `INSERT ... ON CONFLICT DO NOTHING`, then selects
the account row `FOR UPDATE`. Concurrent requests and separate backend instances
therefore serialize updates for one identity instead of maintaining process-local
counters that can be bypassed through another instance.

## Enumeration Resistance

Wrong credentials for existing and unknown accounts follow the same sequence:

- Attempts 1–4: HTTP 401.
- Attempt 5 and requests during lockout: HTTP 429 with `Retry-After`.
- Body in every case: `Invalid email or password. Please try again later.`

Unknown identifiers receive and persist the same protection state as existing accounts.
The response does not contain remaining-attempt counts, account existence, role,
verification state, or lockout wording. A valid password may continue to MFA or email
verification because possession of that password is no longer an account-enumeration
probe.

## Coverage

Administrators and normal users use the same `/api/v1/auth/custom-signin` password
stage, so the control is role-independent. The separate login-MFA OTP stage already
limits each challenge to five invalid OTP attempts; password lockout does not weaken or
replace that second-factor control.

## Recovery and Operations

- Normal recovery: wait until `locked_until`, then authenticate with the correct password.
- A successful password check removes the stored counter.
- A wrong password after timer expiry begins a fresh sequence at one.
- Operators should not edit or delete rows manually as routine recovery.
- Repeated lockouts may indicate password spraying or targeted account denial and should
  be reviewed in centralized application logs.
- The application logs only the first 12 characters of the derived identity key for this
  control, not the plaintext email.

## Deployment

1. Back up the target PostgreSQL database under the normal release procedure.
2. Set the production variables to 5 attempts and 15 minutes.
3. Run `alembic upgrade head`; revision `f4a9c2d78110` creates `login_attempts`. The
   migration also safely recognizes a matching table created earlier by the application's
   legacy `Base.metadata.create_all()` startup path and records the revision without a
   duplicate-table failure.
4. Deploy all backend instances from the same commit with the same `SECRET_KEY`.
5. Confirm health, migration revision, and configuration without exposing secrets.
6. Run controlled normal-user and administrator tests in the approved window.
7. Preserve sanitized evidence and the release identifier.

## Rollback

Roll back application code through the normal release mechanism. Retaining the
`login_attempts` table is harmless while older code is active. Drop it only through the
reviewed Alembic downgrade if rollback policy requires schema reversal.

## Limitations

- Local acceptance proves implementation behavior, not production deployment.
- Account lockout can be abused for temporary denial of access; the 15-minute bounded
  timer, generic feedback, shared state, and logging balance this risk against the KACST
  requirement. Gateway/IP-level rate limiting can be added as defense in depth but must
  not replace the account-level fifth-failure control.
