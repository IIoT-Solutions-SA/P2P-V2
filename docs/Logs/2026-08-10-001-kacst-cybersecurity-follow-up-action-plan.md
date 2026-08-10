# PeerLink KACST Cybersecurity Follow-Up Action Plan

**Date:** 2026-08-10 AST  
**Project:** PeerLink / P2P-V2  
**Branch:** `hamza-backend`  
**Technical owner:** Hamza Feroze  
**Internal reviewer and submission owner:** Aadil Feroze / IIoT Solutions

## Purpose

Record the engineering work required by the latest KACST Cybersecurity Department review of PeerLink. This is an implementation and evidence plan, not a copy of the email correspondence.

The current follow-up has three primary workstreams:

1. Session timeout controls.
2. Failed-login protection.
3. A fresh formal vulnerability assessment that is repeated at least quarterly.

All technical material must be returned to Aadil for internal review. Nothing should be sent directly to Dr. Ibrahim or KACST from the engineering workstream.

## Context and Important Distinction

The earlier PeerLink penetration-test remediation and successful retest are already complete and on record. KACST is requesting a **new formal vulnerability assessment** as a separate recurring control. The earlier penetration-test retest must not be presented as the new quarterly assessment.

KACST did not impose a new fixed deadline in the returned comments, but the response is expected as soon as practical. The existing workbook includes an internal working target of 2026-09-29 for the low-risk PeerLink controls; this is not a newly issued KACST deadline.

## Workstream 1 — Session Controls

### Required outcome

Deploy and verify session expiration controls across all applicable PeerLink user roles.

### Working baseline

| Control | Required baseline | Verification |
|---|---:|---|
| Idle timeout | 30 minutes | An inactive session expires and requires a new sign-in |
| Absolute session lifetime | 8 hours, within KACST's recommended 4–8-hour range | A session cannot continue indefinitely even while active |
| Coverage | Normal users and administrators | Both roles follow the intended expiration policy |

### Implementation checks

- Inspect the existing SuperTokens and backend session configuration before changing it.
- Confirm whether idle and absolute expiration are controlled by access-token lifetime, refresh-token lifetime, application middleware, SuperTokens configuration, or a combination.
- Configure the 30-minute idle timeout.
- Configure the 8-hour absolute session lifetime unless architecture requires another documented value within the 4–8-hour range.
- Verify `Secure`, `HttpOnly`, and appropriate `SameSite` cookie attributes.
- Verify session/token rotation after successful authentication and relevant privilege changes.
- Verify logout invalidates the active session.
- Confirm consistent behavior for normal-user and administrator sessions.
- Avoid relying only on source-code inspection; deployed behavior must be tested.

### Evidence required

- Sanitized configuration extract or screenshot showing final timeout values.
- Test record containing account role, start time, expected behavior, actual behavior, and pass/fail.
- Evidence for both idle expiry and absolute expiry.
- Deployment/release identifier and implementation date.
- Any architectural limitation and the approved alternative control.

## Workstream 2 — Failed-Login Protection

### Required outcome

Deploy and verify protection against repeated consecutive failed authentication attempts.

### Working baseline

| Control | Required baseline | Verification |
|---|---:|---|
| Trigger | 5 consecutive failed attempts, within KACST's recommended 3–5 range | Protection activates on the fifth failure |
| Response | Lockout, throttling, or an equivalent effective control | Continued automated guessing is blocked or materially slowed |
| Recovery | Defined timer, reset mechanism, or administrator process | Recovery works safely and is documented |
| User feedback | Generic authentication message | Response does not reveal whether an account exists |
| Coverage | Normal users and administrators where flows differ | Both paths enforce the intended control |

### Implementation checks

- Inspect current SuperTokens and application-level failed-login behavior.
- Determine whether native SuperTokens controls satisfy the requirement or whether application/gateway controls are needed.
- Configure the five-attempt threshold unless a stricter value is selected and documented.
- Define the lockout/throttling duration and recovery method.
- Ensure a successful login or approved recovery resets counters correctly.
- Ensure distributed deployments cannot bypass the counter through another backend instance.
- Confirm error responses do not enable account enumeration.
- Test normal-user and administrator authentication paths separately when applicable.

### Evidence required

- Sanitized configuration extract or screenshot showing threshold and recovery behavior.
- Controlled test record showing attempts one through five and the resulting protection.
- Recovery/unlock test result.
- Generic-message/account-enumeration check.
- Deployment/release identifier and implementation date.

## Workstream 3 — Quarterly Vulnerability Assessment

### Required outcome

Perform a fresh, formal, evidence-backed vulnerability assessment of the current PeerLink environment and establish a repeatable quarterly process.

### Assessment scope

- Production PeerLink application and internet-facing services.
- OCI compute instances and relevant cloud configuration exposed to PeerLink.
- Operating-system packages and security updates.
- Listening ports and externally reachable services.
- CIS-aligned host checks.
- TLS configuration and HTTP security headers.
- Authentication and session controls.
- Application and framework dependencies.
- Container images where containers are used.
- Approved, non-disruptive web-application vulnerability scanning.
- Existing OCI Vulnerability Scanning Service results, including available host/package, port, CIS, and file scans.
- Explicitly documented exclusions and reasons.

### Execution sequence

1. Confirm the exact asset inventory, environment, URLs, scan window, and responsible owners.
2. Export and review the latest OCI Vulnerability Scanning Service results.
3. Run complementary dependency and container scans where applicable.
4. Run approved TLS, header, authentication, session, and web-application checks.
5. Preserve raw internal outputs without exposing credentials or secrets.
6. Validate scanner results and remove duplicates and false positives.
7. Assign severity, affected asset/component, evidence reference, owner, status, and target date to every validated finding.
8. Escalate Critical or High findings immediately rather than waiting for the final report.
9. Remediate findings according to priority.
10. Retest remediated findings and retain proof.
11. Document realistic action plans for open findings.
12. Produce the reviewed assessment report and evidence package.

### Severity handling

| Severity | Required handling |
|---|---|
| Critical | Escalate immediately; remediate and retest urgently |
| High | Prioritize remediation; provide retest evidence or a formal short-term plan |
| Medium | Assign owner and target date; track to closure |
| Low / Informational | Record, prioritize reasonably, and close or accept with rationale |

Raw scanner counts must not be copied directly into the external report. Results must be validated, deduplicated, triaged, and summarized first.

## Required Report Structure

1. Cover and control information: title, reporting period, assessment dates, environment, version, author/reviewer, and confidentiality marking.
2. Executive summary: scope, overall risk position, findings by severity, and Critical/High status.
3. Scope and exclusions: systems, applications, hosts, URLs, environments, exclusions, and reasons.
4. Methods and tools: OCI services and host, dependency, container, TLS/header, authentication/session, and web checks, including versions where available.
5. Results summary: counts by severity and status.
6. Detailed findings register: one validated finding per row.
7. Remediation and retest: completed actions, open actions, owners, target dates, accepted risks, and retest outcomes.
8. Quarterly schedule: next planned assessment date or month and confirmation that a reviewed package will be produced at least once every three months.
9. Evidence appendix: sanitized proof of configuration, scope, completed run dates, and result references.

## Findings Register Fields

Each validated finding must include:

- Unique finding ID.
- Asset or component.
- Finding title and description.
- Severity.
- Evidence or scanner/test reference.
- Remediation status.
- Owner.
- Target date.
- Retest status and result.
- Exception or acceptance rationale where applicable.

## Handoff Package

Return one organized internal package to Aadil containing:

```text
01_Quarterly_VA_Report.pdf
02_Findings_and_Remediation_Register.xlsx
03_Scanner_Evidence/
04_Security_Control_Evidence/
05_Raw_Internal_Results/
06_Open_Items_and_Blockers.md
```

`05_Raw_Internal_Results/` must be marked **INTERNAL ONLY** and excluded from the external package unless specifically reviewed and sanitized.

## Security and Testing Guardrails

- Use approved, non-disruptive scanning settings.
- Coordinate any production web-application scan window.
- Do not perform destructive exploitation against production.
- Never place passwords, tokens, private keys, cookies, connection strings, or usable secrets in reports or screenshots.
- Remove unnecessary internal IPs, hostnames, account identifiers, and detailed infrastructure data from external-facing evidence.
- Mark sensitive raw exports as **INTERNAL ONLY**.
- Stop normal reporting work and immediately escalate evidence of active compromise or immediate material exposure.
- Report scope exclusions, blockers, or architectural conflicts before marking a workstream complete.

## Definition of Done

- [ ] Scope, asset inventory, environment, and assessment dates are documented.
- [ ] Session idle timeout is deployed at 30 minutes and tested.
- [ ] Absolute session lifetime is deployed within 4–8 hours, using the 8-hour baseline unless otherwise documented, and tested.
- [ ] Normal-user and administrator session behavior is verified.
- [ ] Secure cookie/session rotation/logout behavior is verified.
- [ ] Failed-login protection activates after five consecutive failures or a documented stricter threshold.
- [ ] Lockout/throttling recovery behavior is documented and tested.
- [ ] Authentication feedback is generic and does not disclose account existence.
- [ ] Latest OCI and complementary scan results are exported and reviewed.
- [ ] Findings are validated, deduplicated, severity-rated, and assigned to owners.
- [ ] Critical and High findings are remediated and retested or have an explicit approved short-term plan.
- [ ] Report, register, sanitized evidence, and internal raw results are organized separately.
- [ ] External-facing files contain no secrets or unnecessary sensitive infrastructure details.
- [ ] Next quarterly assessment date or month is recorded.
- [ ] The complete package is returned to Aadil for review.
- [ ] Nothing is sent directly to Dr. Ibrahim or KACST from the engineering workstream.

## Source Records

The engineering plan is based on the KACST-reviewed PeerLink Risk Register/Treatment Plan and the internal engineer action brief dated 2026-08-10. Those source records remain the authority if wording or acceptance criteria need to be rechecked.
