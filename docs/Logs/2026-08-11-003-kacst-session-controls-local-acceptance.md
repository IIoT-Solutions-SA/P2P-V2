# KACST Session Controls — Isolated Local Acceptance

**Date:** 2026-08-11 AST
**Branch:** `feature/kacst-session-controls`
**Scope:** Item 1 isolated local acceptance only; no production deployment

## Environment

A dedicated Compose project, `p2p-session-acceptance`, was created using `docker/session-control-acceptance-compose.yml`. It uses isolated PostgreSQL, MongoDB, SuperTokens, backend, frontend, volumes, and network resources.

| Component | Local endpoint / setting |
|---|---|
| Frontend | `http://127.0.0.1:15173` |
| Backend | `http://127.0.0.1:18000` |
| Idle acceptance boundary | 45 seconds, test mode only |
| Absolute acceptance boundary | 150 seconds, test mode only |
| Final source baseline | 30 minutes idle / 8 hours absolute |

Accelerated second-based settings are ignored outside explicit backend `ENVIRONMENT=test` and frontend Vite `test` mode. Unit tests verify production retains 1,800-second idle and 28,800-second absolute boundaries even if test override variables exist.

## Executed Tests

| Test | Result |
|---|---|
| Compose configuration validation | Pass |
| Isolated PostgreSQL health | Pass |
| Isolated MongoDB health | Pass |
| Isolated SuperTokens startup | Pass |
| Isolated backend health | Pass |
| Isolated frontend HTTP/render | Pass |
| Session/auth combined regression suite | 24 passed |
| Frontend TypeScript and production build | Pass |
| New session hook targeted ESLint | Pass |
| Administrator idle expiration | Pass after 45 seconds inactive |
| Normal-user activity continuity | Pass with authenticated heartbeats every 25 seconds |
| Normal-user absolute expiration | Pass at 150 seconds despite continued activity |
| Refresh-token rotation | Pass; rotated session stayed authorized |
| Manual logout/revocation | Pass |
| Replay after logout | Pass; request rejected with 401 |

Final sanitized runner output:

```text
administrator idle expiry at accelerated 45-second boundary: PASS
normal-user absolute expiry at accelerated 150-second boundary despite activity: PASS
refresh rotation while policy valid: PASS
manual logout revocation: PASS
elapsed_seconds=198
No credentials, cookies, session handles, or token values were printed.
```

## Browser Evidence

- BrowserOps task: `20260811-141442-peerlink-session-acceptance-final`
- Evidence directory: `/home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260811-141442-peerlink-session-acceptance-final`
- Captures confirm the isolated frontend rendered from `127.0.0.1:15173` and exposed the expected PeerLink public/sign-up flow.

## Safety and Data Handling

- No production service, database, or deployment was changed.
- Disposable local test accounts used unique domains and isolated databases.
- OTPs were recovered only from isolated test hashes to automate account activation.
- Credentials, cookies, token values, session handles, and OTP values were not written into project evidence.
- Email delivery is disabled for both local `development` and isolated `test` environments unless explicitly enabled.

## Remaining Production Evidence

Local acceptance is complete. Submission still requires the approved production release ID, deployed 30-minute/eight-hour captures, production cookie metadata with values redacted, real-duration user/admin checks, two-tab visual evidence, and Hamza/Aadil sign-off. No email has been sent to Dr. Ibrahim or KACST.
