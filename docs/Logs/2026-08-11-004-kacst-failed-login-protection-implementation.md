# KACST Failed-Login Protection Implementation Log

**Date:** 2026-08-11 AST
**Project:** PeerLink / P2P-V2
**Workstream:** Item 2 — failed-login protection
**Branch:** `feature/kacst-failed-login-protection`
**Base:** Item 1 commit `d8b2b3b`

## Objective

Implement and locally validate the KACST follow-up requirement to activate protection on
the fifth consecutive failed password attempt, provide safe timed recovery, avoid account
enumeration, and apply the same behavior to normal users and administrators.

## Implemented Changes

- Added shared PostgreSQL `login_attempts` state and Alembic revision
  `f4a9c2d78110`.
- Added an HMAC-derived account key so the control table does not store plaintext email.
- Added a five-failure threshold and 15-minute production lockout.
- Added pre-authentication enforcement so a locked request never reaches SuperTokens
  password verification.
- Added atomic account-level updates using PostgreSQL conflict handling and row locking.
- Added successful-password reset of consecutive failures.
- Added identical generic body text for wrong credentials and lockout state.
- Added equivalent counters for unknown identifiers to prevent response-sequence
  enumeration.
- Added `Retry-After` on active protection responses without disclosing remaining
  attempts or account state in the body.
- Added production, development, template, and isolated-test configuration.
- Added test-only accelerated lockout guarded by `ENVIRONMENT=test`.
- Retained the existing five-attempt protection for each login-MFA OTP challenge.

## Files

### Backend

- `p2p-backend-app/app/services/login_protection_service.py`
- `p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py`
- `p2p-backend-app/app/models/pg_models.py`
- `p2p-backend-app/app/core/config.py`
- `p2p-backend-app/alembic/versions/f4a9c2d78110_add_failed_login_protection.py`
- `p2p-backend-app/tests/test_login_protection.py`

### Configuration and acceptance

- `p2p-backend-app/.env.template`
- `docker/docker-compose.yml`
- `docker/development_docker-compose.yml`
- `docker/session-control-acceptance-compose.yml`
- `scripts/run_failed_login_acceptance.py`

### Documentation

- `docs/architecture/failed-login-protection.md`
- `docs/Reports/PeerLink-KACST-Failed-Login-Protection-Test-Record.md`
- This log.

## Local Validation

| Validation | Result |
|---|---|
| Backend unit/regression tests | 32 PASS |
| Existing input/security validation checks | 126 PASS |
| Frontend production build and targeted lint | PASS |
| Alembic upgrade/downgrade/re-upgrade | PASS |
| Alembic upgrade when legacy startup already created the table | PASS |
| Main local backend migration, health, and generic-failure smoke check | PASS |
| Administrator fifth-failure activation | PASS |
| Normal-user fifth-failure activation | PASS |
| Existing-versus-unknown response sequence | PASS |
| Concurrent failure serialization | PASS |
| Correct password blocked during lock | PASS |
| Accelerated timer recovery | PASS |
| Successful-password counter reset | PASS |
| No plaintext email in control table | PASS |
| Real rendered frontend generic feedback | PASS — BrowserOps task `20260811-143546-peerlink-failed-login-local-acceptance` |
| All three Compose files | VALID |
| Python compilation and diff check | PASS |

The isolated acceptance environment used a 12-second lockout so recovery could be tested
repeatably. The production setting remains 15 minutes, and production-mode tests prove
the accelerated override is ignored.

## Security Decisions

- Shared database state was selected instead of in-memory counters because multiple
  backend instances must not bypass protection.
- HMAC account keys reduce sensitive identity storage while preserving deterministic
  lookup.
- Unknown accounts are counted and locked using the same mechanism; otherwise status and
  timing sequences could reveal account existence.
- The user-facing text never says that an account exists, is locked, or has a specific
  number of attempts remaining.
- Password verification remains blocked throughout the timer even when the supplied
  password is correct. This avoids using correct-password behavior as a lock-state probe.
- Recovery is automatic and bounded. Routine manual database unlock is not part of the
  control.

## Status

**Locally complete; not pushed, deployed, or submitted.**

Production readiness still requires deployment approval, migration execution, a release
identifier, controlled tests with the real 15-minute duration for both roles, sanitized
production evidence, and Aadil's internal review. Nothing should be sent directly to Dr.
Ibrahim or KACST from this engineering branch.
