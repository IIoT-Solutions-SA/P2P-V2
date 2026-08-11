# PeerLink KACST Cybersecurity Follow-Up Email Draft

**Status:** Draft only — not sent
**Intended recipient:** Aadil Feroze
**Purpose:** Internal review before any communication to Dr. Ibrahim or KACST

## Subject

PeerLink KACST cybersecurity follow-up — session controls, failed-login protection, Q3 vulnerability assessment, and production evidence

## Email Body

Dear Aadil,

I have completed and deployed the three PeerLink cybersecurity follow-up workstreams requested for the KACST environment. The implementation, local acceptance, OCI production release, and supporting evidence are now available for your internal review.

The three completed workstreams are:

1. session inactivity and absolute-lifetime controls;
2. failed-login protection; and
3. the Q3 2026 quarterly vulnerability assessment and remediation cycle.

### 1. Session controls

PeerLink now enforces a 30-minute inactivity timeout and an eight-hour absolute session lifetime.

The backend is authoritative for both boundaries. Authenticated requests, activity heartbeats, and token refreshes are evaluated against shared server-side session state. Activity can extend the session only within the eight-hour absolute limit; it cannot reset or bypass that limit. Expired and legacy sessions fail closed and are revoked.

The frontend provides the corresponding user experience by recording genuine browser activity, sharing the latest activity timestamp across tabs, sending throttled authenticated heartbeats, and signing the browser out when the idle boundary is reached. This does not replace backend enforcement.

Production SuperTokens values are aligned with the policy:

- access-token validity: 1,800 seconds;
- refresh-token validity: 480 minutes;
- cookies in production: Secure, HttpOnly, SameSite=Lax; and
- session state: shared through the SuperTokens/PostgreSQL deployment rather than per-process memory.

Validation included deterministic boundary tests at exactly 30 minutes and eight hours, proof that recent activity cannot extend the absolute limit, revocation checks, token rotation, logout/replay rejection, cross-tab implementation checks, and isolated accelerated administrator/member acceptance. The same tests were executed inside the deployed production backend image.

A literal eight-hour browser wait was not represented as completed evidence. If role-specific elapsed-time screenshots are required, we can schedule controlled disposable production user and administrator accounts for that supplemental capture.

### 2. Failed-login protection

PeerLink now activates protection on the fifth consecutive failed password attempt and applies a 15-minute production lockout.

The implementation uses atomic PostgreSQL updates and row locking so concurrent requests and multiple backend workers cannot bypass the threshold. Successful authentication resets the failure sequence. Existing and unknown account identifiers receive the same generic response so the endpoint does not reveal whether an account exists.

The database stores an HMAC-derived identity key rather than a plaintext email address in the failed-login tracking table.

Local acceptance covered administrators, normal users, unknown identifiers, concurrent attempts, lockout recovery, successful-login reset, migration compatibility, and test-override isolation.

The production release applied Alembic revision `f4a9c2d78110`. A controlled live OCI acceptance used a unique nonexistent identifier and confirmed:

- attempts 1–4: HTTP 401 with generic feedback;
- attempt 5: HTTP 429 with the same generic feedback;
- attempt 6 during the active lock: HTTP 429 with the same generic feedback; and
- shared database state: five failures with an active lock.

The acceptance sent no email, touched no real user, and automatically removed its HMAC-keyed test row afterward.

### 3. Q3 2026 vulnerability assessment

A fresh quarterly assessment was completed across the PeerLink application, dependencies, images, public web boundary, OCI network posture, OCI Vulnerability Scanning Service results, authentication controls, and deployment configuration.

The package includes a formal assessment report, findings register, evidence index, sanitized evidence, quarterly schedule, architecture/process documentation, implementation log, and a repeatable assessment runner.

Repository remediation included:

- dependency and image updates;
- hardened backend and frontend production images;
- removal of the production source mount and development reload behavior;
- non-root backend runtime;
- production worker configuration;
- disabled production API documentation exposure;
- frontend defense headers;
- mandatory untracked production secret variables;
- improved Docker build context; and
- repeatable dependency, secret, image, Compose, and public-boundary checks.

The frontend production dependency audit and final frontend image scan reported zero findings. The backend dependency audit was reduced from 34 advisories to one constrained advisory whose currently published fixed version conflicts with the supported dependency chain. Remaining vendor/unfixed operating-system image records, the SSH MAC correction, host-package actions, and credential rotation are recorded transparently in the findings register rather than being described as completed.

### Frontend lint clarification

Some earlier working logs stated that the full frontend lint baseline contained 33 errors and seven warnings. That statement described pre-existing repository debt at that point in the work; it did not mean the security implementation introduced 40 new problems.

Before production release, I resolved that baseline. The cleanup addressed stale Hook dependencies, object-URL cleanup, unused state/variables, stale suppressions, and ESLint alignment for intentional Leaflet runtime payloads, shared helper exports, and NUL-byte validation.

The final full command now passes with zero errors and zero warnings. The frontend production build also passes. The only remaining frontend build message is a large-bundle optimization advisory, not a lint or build failure.

### Validation summary

The final evidence includes:

- 32 authentication/session/failed-login unit and regression tests passed;
- 126 existing security-validation checks passed;
- full frontend lint passed with zero errors and zero warnings;
- frontend production build passed;
- local accelerated session acceptance passed;
- local failed-login acceptance passed;
- production, development, and acceptance Compose files validated;
- production database migration applied;
- OCI backend health passed;
- OCI frontend health passed;
- all five production services running/healthy as applicable;
- exact production values confirmed as 30 minutes, eight hours, five failures, and 15 minutes;
- accelerated test overrides confirmed absent from production; and
- controlled live failed-login production acceptance passed.

### Production release and rollback evidence

The application release was deployed through the `hamza-backend` production branch.

- deployed application commit: `c52558534938f4b7c66358685f437c86d6080fee`;
- final verification/workflow commit: `6f532c3`;
- deployment workflow run: `31530596370` — successful;
- final production verification run: `31531595809` — successful.

Before deployment, the workflow created validated PostgreSQL application, PostgreSQL SuperTokens, and MongoDB backups. The final backup set is stored on the OCI VM under:

`/home/ubuntu/P2P-V2/deploy-backups/20260811-231100-AST-pre-kacst-controls/`

Existing credentials were moved out of tracked Compose source into the untracked production environment file without printing their values. Actual credential rotation remains a separate coordinated maintenance action because database-user passwords and every dependent connection string must change atomically.

### Documents for review

I recommend reading the following files in this order:

1. `docs/Logs/2026-08-11-006-kacst-controls-oci-production-release.md`
2. `docs/Reports/PeerLink-KACST-Quarterly-Vulnerability-Assessment-2026-Q3.md`
3. `docs/Reports/PeerLink-KACST-Quarterly-VA-Findings-Register-2026-Q3.md`
4. `docs/Reports/PeerLink-KACST-Session-Control-Test-Record.md`
5. `docs/Reports/PeerLink-KACST-Failed-Login-Protection-Test-Record.md`
6. `docs/Reports/PeerLink-KACST-Quarterly-VA-Evidence-Index-2026-Q3.md`
7. `docs/architecture/session-security-controls.md`
8. `docs/architecture/failed-login-protection.md`
9. `docs/architecture/quarterly-vulnerability-management.md`
10. `docs/security/quarterly-vulnerability-assessment-schedule.md`
11. `docs/Logs/2026-08-10-001-kacst-cybersecurity-follow-up-action-plan.md`
12. `docs/Logs/2026-08-10-002-kacst-session-controls-implementation.md`
13. `docs/Logs/2026-08-11-003-kacst-session-controls-local-acceptance.md`
14. `docs/Logs/2026-08-11-004-kacst-failed-login-protection-implementation.md`
15. `docs/Logs/2026-08-11-005-kacst-quarterly-vulnerability-assessment.md`

Please review the evidence, wording, remaining-risk treatment, and whether you require supplemental real-duration user/admin screenshots before approving the package for onward communication.

No message should be sent directly to Dr. Ibrahim or KACST until you have reviewed and approved the internal package.

Regards,

Hamza Feroze

## Proposed Attachments

Attach or link the five primary review documents first:

- production release log;
- quarterly vulnerability-assessment report;
- findings register;
- session-control test record; and
- failed-login protection test record.

Provide the remaining architecture, evidence-index, schedule, and implementation logs as a supporting folder or repository links to avoid an unnecessarily large email attachment set.

## Send Control

This document is only a draft. Confirm the final recipient address, wording, and attachments with Hamza before sending. Do not send to Aadil, Dr. Ibrahim, or KACST without explicit approval.
