# PeerLink Session Security Controls

## Control Objective

PeerLink enforces a 30-minute inactivity timeout and an eight-hour absolute session lifetime for every authenticated session, including normal users and administrators. SuperTokens remains the token and cookie authority; PeerLink adds shared-database policy enforcement and browser inactivity handling.

## Final Baseline

| Setting | Value | Enforcement point |
|---|---:|---|
| Idle timeout | 30 minutes | Backend SuperTokens session hooks plus frontend inactivity timer |
| Absolute lifetime | 8 hours | Backend SuperTokens session hooks |
| Access-token validity | 1,800 seconds | SuperTokens Core |
| Refresh-token validity | 480 minutes | SuperTokens Core, with application absolute-limit enforcement |
| Cookie `Secure` | Enabled in production | SuperTokens Python recipe |
| Cookie `HttpOnly` | SuperTokens-managed session cookie default | SuperTokens Core/SDK |
| Cookie `SameSite` | `Lax` | SuperTokens Python recipe |

The application limits are authoritative even if a token has not yet reached its cryptographic expiry.

## Architecture

### Session creation

`app/core/session_security.py` overrides the SuperTokens session recipe's `create_new_session` function. Every newly created session receives a `peerlink_session_security` record in SuperTokens session data containing the policy version, latest activity timestamp, and configured limits.

### Authenticated requests

The recipe's `get_session` function checks:

1. Time since the session was originally created.
2. Time since the last authenticated activity stored in shared session data.

A session at or beyond either limit is revoked and rejected with a generic `Session expired. Please sign in again.` response. Each authenticated API request persists its activity time in shared session data so enforcement does not expire a genuinely active session early.

### Token refresh

The same checks run after refresh-token processing. An expired session is immediately revoked and the refresh fails. This prevents refresh rotation from extending the eight-hour absolute lifetime.

### Browser inactivity

`src/hooks/useSessionTimeout.ts` tracks pointer, keyboard, scrolling, touch, and visibility activity. It shares the latest activity timestamp across tabs through `localStorage`, sends an authenticated activity heartbeat at most once per minute for interactions that do not naturally call an API, and invokes the normal logout flow after 30 minutes of inactivity. Backend enforcement remains authoritative if browser code is disabled, suspended, or manipulated.

### Distributed deployment

Activity state is stored in SuperTokens' PostgreSQL-backed session data rather than backend process memory. Requests routed to another backend instance therefore see the same activity record and expiration policy.

## Role Coverage

PeerLink uses one global SuperTokens session recipe for administrators and normal users. All protected API routes call the same `verify_session()` flow, so both roles pass through these controls. Role-specific acceptance tests are still required after deployment to prove behavior in the target environment.

## Logout and Rotation

- Manual logout first clears the trusted-device cookie through `/api/v1/auth/custom-signout`, then calls SuperTokens `Session.signOut()` to revoke the active session.
- SuperTokens performs normal access/refresh-token rotation.
- Idle and absolute checks are applied to both normal verification and refresh flows.
- Existing sessions without the versioned activity marker fail closed: creation time becomes their last known activity. Deployment may therefore require existing users to sign in again.

## Configuration

Backend:

```env
SESSION_IDLE_TIMEOUT_MINUTES=30
SESSION_ABSOLUTE_LIFETIME_HOURS=8
```

Frontend:

```env
VITE_SESSION_IDLE_TIMEOUT_MINUTES=30
```

SuperTokens Core:

```env
ACCESS_TOKEN_VALIDITY=1800
REFRESH_TOKEN_VALIDITY=480
```

Changing the frontend timer never weakens backend enforcement. Any exception to the baseline must be documented and approved before deployment.

## Deployment Procedure

1. Back up the production configuration and record the release identifier.
2. Confirm all values above in the deployment environment.
3. Recreate/redeploy SuperTokens Core so its validity settings load.
4. Rebuild and deploy the backend and frontend.
5. Confirm health checks pass.
6. Expect pre-deployment sessions to be invalidated on their next authenticated request if already outside the new limits.
7. Execute the normal-user and administrator test matrix in `docs/Reports/PeerLink-KACST-Session-Control-Test-Record.md`.
8. Capture sanitized configuration and browser-cookie screenshots without token values.
9. Record actual timestamps, results, release ID, and tester.

## Security Notes

- Never capture cookie values, access tokens, refresh tokens, or database session data in external evidence.
- Browser DevTools evidence should show cookie attribute names only, with values redacted.
- An eight-hour absolute test may use controlled time manipulation or a temporary shortened lifetime only in an isolated test environment. The final production configuration must still be independently verified as eight hours.
- Production acceptance is not complete until elapsed-time behavior is tested after deployment.
