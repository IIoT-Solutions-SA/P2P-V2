# KACST Session Controls Implementation

**Date:** 2026-08-10 AST
**Project:** PeerLink / P2P-V2
**Branch:** `feature/kacst-session-controls`
**Base commit:** `631b6af`
**Workstream:** 1 of 3 — session controls

## Objective

Implement the first KACST follow-up workstream completely at source level: 30-minute inactivity expiry, eight-hour absolute lifetime, consistent enforcement for all authenticated roles, secure production cookie settings, logout/revocation behavior, automated checks, deployment guidance, and an evidence record.

## Existing-State Findings

- PeerLink used SuperTokens globally for authenticated users and administrators.
- Production cookies were already configured as `Secure` with `SameSite=Lax`; SuperTokens manages session cookies as `HttpOnly`.
- The production SuperTokens refresh-token validity was seven days.
- There was no application-level idle timeout or eight-hour absolute lifetime.
- Manual logout already cleared the trusted-device cookie and then invoked SuperTokens sign-out/revocation.
- Frontend authentication used the same `AuthContext` and SuperTokens session recipe for all roles.

## Changes Implemented

### Backend policy enforcement

Added `p2p-backend-app/app/core/session_security.py`:

- Adds versioned security metadata when every SuperTokens session is created.
- Checks inactivity and original session age on every protected-session verification.
- Repeats enforcement during token refresh so rotation cannot extend absolute lifetime.
- Revokes and rejects sessions at 30 minutes idle or eight hours total.
- Stores authenticated API activity in SuperTokens shared session data for multi-instance consistency.
- Fails closed for legacy sessions that do not contain the new marker.
- Preserves unrelated SuperTokens session data.

Connected the override globally in `app/core/supertokens.py`, covering normal users and administrators without duplicate role-specific implementations.

### Configuration

Added backend settings:

- `SESSION_IDLE_TIMEOUT_MINUTES=30`
- `SESSION_ABSOLUTE_LIFETIME_HOURS=8`

Updated production and development Compose definitions:

- `ACCESS_TOKEN_VALIDITY=1800`
- `REFRESH_TOKEN_VALIDITY=480`
- The three application settings above.

Updated `.env.template` with the baseline.

### Frontend inactivity handling

Added `p2p-frontend-app/src/hooks/useSessionTimeout.ts` and connected it to `AuthContext`:

- Tracks pointer, keyboard, scrolling, touch, and page-visibility activity.
- Shares activity across browser tabs using local storage.
- Sends an authenticated `/api/v1/auth/session-activity` heartbeat at most once per minute so scrolling and other local-only activity reaches backend enforcement.
- Runs the normal logout flow after 30 minutes of browser inactivity.
- Keeps backend enforcement authoritative.

Added `VITE_SESSION_IDLE_TIMEOUT_MINUTES=30` to development and production frontend environments.

### Tests and documentation

Added eleven backend unit tests covering:

- Valid active sessions.
- Exact 30-minute idle expiry.
- Exact eight-hour absolute expiry.
- Absolute expiry despite recent activity.
- Revocation on expiry.
- Shared activity persistence.
- Fail-closed handling of legacy sessions.
- Acceptance-only accelerated idle and absolute settings.
- Proof that production ignores accelerated test overrides.

Added:

- `docs/architecture/session-security-controls.md`
- `docs/Reports/PeerLink-KACST-Session-Control-Test-Record.md`

The report template separates completed automated verification from post-deployment acceptance evidence and prevents unfinished production checks from being represented as complete.

## Validation Results

| Validation | Result |
|---|---|
| Backend session security unit tests | 11 passed |
| Backend Python compilation | Passed |
| Frontend TypeScript + Vite production build | Passed |
| Production Docker Compose validation | Passed |
| Development Docker Compose validation | Passed |
| Running development backend startup after hot reload | Passed |
| Running development health route | Reachable; existing route redirects `/health` to `/health/` |
| Isolated acceptance stack | Five services healthy/running under project `p2p-session-acceptance` |
| Combined session + auth regression tests | 24 passed |
| Administrator accelerated idle expiration | Passed at 45 seconds |
| Normal-user accelerated absolute expiration | Passed at 150 seconds despite 25-second activity heartbeats |
| Refresh-token rotation | Passed; rotated values intentionally not printed |
| Logout revocation/token replay | Passed; replay returned 401 |
| Browser-rendered isolated frontend | Passed; BrowserOps task `20260811-141442-peerlink-session-acceptance-final` |

The frontend build retains its pre-existing advisory that the main JavaScript chunk exceeds 500 kB; this is unrelated to session security. The repository-wide ESLint baseline was subsequently cleaned up before production release, and the full `npm run lint` command now passes with zero errors and zero warnings.

## Files Changed

- `docker/docker-compose.yml`
- `docker/development_docker-compose.yml`
- `docker/session-control-acceptance-compose.yml`
- `p2p-backend-app/.env.template`
- `p2p-backend-app/app/core/config.py`
- `p2p-backend-app/app/core/supertokens.py`
- `p2p-backend-app/app/api/v1/endpoints/auth.py`
- `p2p-backend-app/app/core/session_security.py`
- `p2p-backend-app/app/services/email_verification_service.py`
- `p2p-backend-app/tests/test_session_security.py`
- `p2p-frontend-app/.env.development`
- `p2p-frontend-app/.env.production`
- `p2p-frontend-app/src/contexts/AuthContext.tsx`
- `p2p-frontend-app/src/hooks/useSessionTimeout.ts`
- `p2p-frontend-app/src/lib/api/auth.ts`
- `scripts/run_session_control_acceptance.py`
- `docs/architecture/session-security-controls.md`
- `docs/Reports/PeerLink-KACST-Session-Control-Test-Record.md`
- This implementation log.

## Deployment and Evidence Status

Source implementation, automated verification, and isolated local acceptance are complete. The isolated environment uses separate databases, network, containers, volumes, and ports (`18000`/`15173`) and cannot modify the ordinary local stack. Accelerated second-based settings are accepted only when backend `ENVIRONMENT=test` and frontend Vite mode is `test`; production ignores them by code and test.

The following cannot truthfully be marked complete before the branch is reviewed and deployed to the target environment:

1. Production release identifier and implementation timestamp.
2. Sanitized screenshot/configuration capture from the deployed environment.
3. Production cookie-attribute capture with values redacted.
4. Real-duration idle tests for one normal user and one administrator (local accelerated behavior passed).
5. Real-duration absolute-lifetime tests for one normal user and one administrator (local accelerated behavior passed).
6. Post-deployment logout, rotation, two-tab visual evidence, and multi-instance checks.
7. Aadil's internal review/sign-off.

No email or package was sent to Dr. Ibrahim or KACST.

## Operational Note

The code was loaded automatically only by the existing local development backend's hot-reload volume while validation ran. Production was not deployed or restarted. The SuperTokens Core validity settings require its container/service to be recreated during an approved deployment; changing Compose source alone does not alter the already-running Core process.
