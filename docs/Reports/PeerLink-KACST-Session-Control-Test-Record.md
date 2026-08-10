# PeerLink KACST Session Control Test Record

**Classification:** Internal working evidence; sanitize before external submission
**Control:** Session idle timeout and absolute lifetime
**Required release ID:** _Pending deployment_
**Implementation date:** _Pending deployment_
**Environment:** _Pending_
**Tester / reviewer:** _Pending_

## Sanitized Configuration Evidence

| Evidence ID | Required capture | Status |
|---|---|---|
| SC-CONFIG-01 | Backend values: idle 30 minutes and absolute 8 hours | Source configuration implemented; deployed capture pending |
| SC-CONFIG-02 | SuperTokens values: access 1,800 seconds, refresh 480 minutes | Source configuration implemented; deployed capture pending |
| SC-CONFIG-03 | Frontend value: idle 30 minutes | Source configuration implemented; deployed capture pending |
| SC-COOKIE-01 | Production cookie attributes show `Secure`, `HttpOnly`, and `SameSite=Lax`; values redacted | Pending deployment |

## Acceptance Test Matrix

Record timestamps in AST (UTC+3). Never paste a usable cookie or token.

| Test ID | Role | Procedure | Expected result | Actual result | Pass/Fail | Evidence reference |
|---|---|---|---|---|---|---|
| SC-IDLE-USER | Normal user | Sign in, record time, leave browser and account inactive for 30 minutes, then request a protected page/API | Session is rejected and a new sign-in is required | Pending | Pending | Pending |
| SC-IDLE-ADMIN | Administrator | Repeat normal-user idle test using an administrator | Same 30-minute expiry | Pending | Pending | Pending |
| SC-ACTIVITY-USER | Normal user | Remain active with genuine interactions before 30 minutes | Session remains usable before absolute limit | Pending | Pending | Pending |
| SC-ABS-USER | Normal user | Maintain controlled activity until eight hours from session creation, then request protected resource | Session expires at eight hours despite activity | Pending | Pending | Pending |
| SC-ABS-ADMIN | Administrator | Repeat absolute-lifetime test using an administrator | Same eight-hour expiry | Pending | Pending | Pending |
| SC-LOGOUT-USER | Normal user | Sign in, log out, then replay a protected request from the same browser | Active session is revoked; protected request fails | Pending | Pending | Pending |
| SC-LOGOUT-ADMIN | Administrator | Repeat logout test using an administrator | Active session is revoked | Pending | Pending | Pending |
| SC-ROTATE-01 | Either | Observe sanitized cookie metadata before and after a normal refresh | SuperTokens refresh succeeds only while policy remains valid; token value rotates | Pending | Pending | Pending |
| SC-CROSS-TAB-01 | Either | Open two tabs, remain inactive, observe expiry | Tabs share inactivity state and account is signed out | Pending | Pending | Pending |
| SC-DISTRIBUTED-01 | Either | If multiple backend instances exist, authenticate through one and validate expiry through another | Shared session state prevents bypass | Pending/N/A | Pending | Pending |
| SC-LEGACY-01 | Either | Use a pre-deployment session outside the new idle limit after deployment | Existing session fails closed and requires sign-in | Pending | Pending | Pending |

## Automated Verification Completed

| Check | Result |
|---|---|
| Idle boundary calculation at 30 minutes | Pass |
| Absolute boundary calculation at 8 hours | Pass |
| Absolute limit cannot be extended by recent activity | Pass |
| Expired session is revoked | Pass |
| Activity is persisted while unrelated session data is preserved | Pass |
| Legacy session without marker fails closed | Pass |
| Frontend TypeScript and production build | Pass |
| Backend Python compile | Pass |
| Production and development Compose validation | Pass |

Automated checks support the implementation but do not replace post-deployment elapsed-time tests.

## Evidence Handling

- Save internal raw evidence under the quarterly package's `05_Raw_Internal_Results/` directory.
- Place only sanitized captures under `04_Security_Control_Evidence/`.
- Redact cookie values, session handles, user identifiers, tokens, secrets, internal hostnames, and unnecessary IP addresses.
- Include release ID and exact implementation date before submission.

## Exceptions / Limitations

_No approved exceptions. Production deployment and role-based behavioral acceptance remain pending._

## Sign-Off

| Role | Name | Date | Decision |
|---|---|---|---|
| Technical owner | Hamza Feroze | Pending | Pending |
| Internal reviewer | Aadil Feroze | Pending | Pending |
