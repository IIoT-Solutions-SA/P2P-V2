# KACST Controls OCI Production Release

**Date:** 2026-08-11 AST
**Environment:** PeerLink OCI production / `https://p2p.iiotsolutions.sa`
**Production branch:** `hamza-backend`
**Deployed application commit:** `c52558534938f4b7c66358685f437c86d6080fee`
**Final verification/workflow commit:** `6f532c3`
**Deployment run:** GitHub Actions `31530596370` — success
**Final verification run:** GitHub Actions `31531595809` — success

## Scope

Released the three KACST follow-up workstreams to OCI production:

1. 30-minute idle and eight-hour absolute session controls;
2. five-attempt failed-login protection with a 15-minute lockout; and
3. Q3 2026 vulnerability-assessment repository remediations, evidence, and quarterly process.

The release also removed the recorded frontend lint debt, hardened the deployment workflow, applied the failed-login database migration, rebuilt production images, upgraded the SuperTokens image, and retained rollback backups.

## Branch and Release Model

Three feature branches exist as linear review checkpoints rather than three divergent implementations:

| Branch | Purpose | Checkpoint |
|---|---|---|
| `feature/kacst-session-controls` | Item 1 | `d8b2b3b` |
| `feature/kacst-failed-login-protection` | Item 2, based on Item 1 | `b17c2f7` |
| `feature/kacst-quarterly-vulnerability-assessment` | Item 3 and release hardening, based on Items 1 and 2 | `6f532c3` |
| `hamza-backend` | OCI production deployment branch | `6f532c3` |

Because the branches are linear, production contains all three items without a conflict-prone merge of independent histories.

## Frontend Lint Resolution

The earlier `33 errors and 7 warnings` text was an honest baseline recorded before release, not a claim that the new controls introduced those failures. The baseline was removed before production deployment.

Corrections included:

- stable Hook dependencies for image validation;
- safe object-URL cleanup through current refs;
- removal of unused map zoom and location state;
- corrected effect lifecycle dependencies;
- removal of unused variables and stale lint suppression;
- explicit handling of intentionally runtime-shaped Leaflet/API payloads;
- explicit allowance for shared component modules that export helpers; and
- preservation of intentional NUL-byte input detection.

Final checks:

- `npm run lint`: **PASS, zero errors and zero warnings**;
- `npm run build`: **PASS**;
- the remaining large-bundle message is a Vite optimization advisory, not a lint or compilation failure.

## Pre-Deployment Validation

| Check | Result |
|---|---|
| Auth/session/failed-login unit and regression tests | 32 passed |
| Existing security-validation suite | 126 passed |
| Frontend full lint | 0 errors, 0 warnings |
| Frontend production build | Passed |
| Production/development/acceptance Compose parse | Passed |
| Workflow YAML parse | Passed |
| Git whitespace validation | Passed |

## Deployment Safety and Backups

The deployment workflow was changed so backend source changes are built into the immutable production image instead of merely restarting an old image. Compose changes now rebuild backend and frontend images before reconciliation.

Before deployment, the workflow created and size-validated:

- PostgreSQL `p2p_sandbox` dump;
- PostgreSQL `supertokens` dump; and
- MongoDB `p2p_sandbox` archive.

Initial release backup:

`/home/ubuntu/P2P-V2/deploy-backups/20260811-225915-AST-pre-kacst-controls/`

Final verification backup:

`/home/ubuntu/P2P-V2/deploy-backups/20260811-231100-AST-pre-kacst-controls/`

Existing production credentials were moved from tracked Compose source into the untracked host `docker/.env` without printing values. Credential rotation remains a separate coordinated maintenance action because database-user passwords must be changed atomically with service connection strings.

## OCI Production Changes

- Applied Alembic revision `f4a9c2d78110` for shared failed-login state.
- Deployed backend session-policy enforcement and activity endpoint.
- Deployed frontend cross-tab inactivity tracking and heartbeat.
- Set production session idle timeout to 30 minutes.
- Set production absolute lifetime to eight hours.
- Set failed-login threshold to five attempts.
- Set failed-login lockout duration to 15 minutes.
- Confirmed all accelerated test overrides are absent in production.
- Set SuperTokens access-token validity to 1,800 seconds.
- Set SuperTokens refresh-token validity to 480 minutes.
- Upgraded SuperTokens production image to `11.3.7`.
- Rebuilt hardened backend and frontend production images.
- Kept PostgreSQL and MongoDB persistent volumes in place.

## Production Verification

Final workflow run `31531595809` passed all gates:

| Verification | Result |
|---|---|
| Backend container | Healthy |
| Frontend container | Running and reachable |
| PostgreSQL | Healthy |
| MongoDB | Healthy |
| SuperTokens 11.3.7 | Running |
| Backend health endpoint | Passed |
| Frontend local endpoint | Passed |
| Alembic head | `f4a9c2d78110` applied |
| Production settings | `idle=30m`, `absolute=8h`, `failures=5`, `lockout=15m` |
| Accelerated production overrides | All absent |
| Unit/regression tests inside deployed image | 32 passed |
| Live unknown-account attempts 1–4 | HTTP 401 with generic response |
| Live unknown-account attempt 5 | HTTP 429 with generic response |
| Live active-lock attempt 6 | HTTP 429 with generic response |
| Shared database state | Five failures and active lock confirmed |
| Acceptance database residue | Test row removed automatically |

The live failed-login acceptance used a unique nonexistent identifier. It sent no email, touched no real user, exposed no account-existence detail, and removed its own HMAC-keyed database row.

## BrowserOps Evidence

Task: `20260811-230228-peerlink-kacst-production-release`

Evidence path:

`/home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260811-230228-peerlink-kacst-production-release`

Final rendered evidence:

- `screenshots/003-final-production-health-after-security-verification.png`
- `texts/003-final-production-health-after-security-verification.txt`

This is a real rendered production capture, not a generated screenshot.

## Timing Evidence Interpretation

The deployed image passed deterministic exact-boundary tests for:

- valid immediately before 30 minutes and expired at 30 minutes;
- valid immediately before eight hours and expired at eight hours;
- recent activity not extending the eight-hour maximum;
- role-independent enforcement for users and administrators; and
- a 15-minute production lock duration with test-only overrides disabled.

The isolated browser/API acceptance also proved the complete behavior using shortened timers. A literal eight-hour wall-clock browser observation was not fabricated. If Aadil requires role-specific, real-duration screenshots, they should be scheduled with approved disposable production user/admin accounts and recorded as supplemental evidence.

## Remaining Operational Items

- Hamza technical-owner review and Aadil internal sign-off.
- Production credential rotation in a coordinated maintenance window.
- Effective SSH MAC correction and mapped OCI host-package remediation.
- Resolution of the constrained dependency advisory when the upstream compatibility path is available.
- Optional literal 30-minute/eight-hour role-specific elapsed-time screenshots if requested by the reviewer.
- Email approval and sending; no email was sent by this release task.
