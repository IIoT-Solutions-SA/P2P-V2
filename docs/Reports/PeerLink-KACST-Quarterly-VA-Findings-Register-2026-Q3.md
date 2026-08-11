# PeerLink KACST Quarterly VA Findings Register — 2026 Q3

**Assessment ID:** `PeerLink-2026-Q3-VA`

**Assessment date:** 11 August 2026

**Production target:** `p2p.iiotsolutions.sa` and its OCI host/control plane

**Branch assessed/remediated:** `feature/kacst-quarterly-vulnerability-assessment`

## Status definitions

- **Closed — verified locally:** code/config remediation passed local retest but is not yet production evidence.
- **Open — production action:** a host, credential, or deployment action needs an approved maintenance window.
- **Open — dependency/vendor:** no supported fix is currently installable without an upstream compatibility change.
- **Accepted/monitored:** exposure is intentional and protected by compensating controls.
- **Informational/pass:** control was tested and no vulnerability was found.

## Findings

| ID | Severity | Confidence | Finding | Evidence | Remediation / disposition | Retest | Status |
|---|---|---:|---|---|---|---|---|
| Q3-VA-001 | Critical aggregate scanner rating | Low until mapped | OCI VSS returned 1,000 records: 193 Critical, 649 High and 158 Medium. Only three records identify vulnerable packages; 997 have no package mapping. | OCI host scan completed `2026-08-11T01:13:39Z`. | Do not present all 1,000 as confirmed vulnerabilities. Validate package presence/applicability. The three mapped High records concern host `python3-pip`/`python3-wheel` and ESM fix versions. Patch or remove them in an approved window. | Fresh scan required after host maintenance. | **Open — production action** |
| Q3-VA-002 | High | High | Backend dependency baseline contained 34 advisory records across nine packages. | `pip-audit` before/after records. | Updated FastAPI/Pydantic/SuperTokens/Motor/PyMongo/multipart/mail/AWS dependencies and removed unused `python-jose`. | 34 reduced to one advisory. Imports, 32 unit tests, 126 validation checks and both acceptance suites passed. | **Closed locally; one residual tracked in Q3-VA-003** |
| Q3-VA-003 | High | High | `cryptography 49.0.0` has `PYSEC-2026-3552`; fixed in 50.0.0. Current `fastapi-mail 1.6.5` requires `<50`. | Final `pip-audit` and Trivy backend image scan. | Keep the finding visible; do not force an unsupported resolver override. Track a compatible FastAPI-Mail release or replace the mail abstraction, then upgrade and retest OTP/invitation/password-reset mail. | Final audit still reports exactly one known backend dependency finding. | **Open — dependency/vendor** |
| Q3-VA-004 | High | High | Frontend production dependency audit initially returned four vulnerabilities. | npm audit before/after. | Applied supported lockfile remediation. | `npm audit` for full and production-only trees: 0; Vite production build passed. | **Closed — verified locally** |
| Q3-VA-005 | High | Medium | Production Compose stored default database credentials and a placeholder application secret in tracked configuration. A tracked value must be treated as exposed even if access is network-restricted. | Compose review and tracked-source scan. | Replaced values with mandatory deployment variables, added a non-secret production template, and retained loopback-only database bindings. Production credential generation/rotation is deliberately not performed from this branch. | Compose fails closed when values are absent and validates with supplied dummy values. | **Closed locally; rotation/deployment open** |
| Q3-VA-006 | Medium | High | Production OpenAPI schema is publicly accessible at `/api/v1/openapi.json` (HTTP 200). | Safe public GET on 11 August 2026. | Disable Swagger, ReDoc and OpenAPI when `ENVIRONMENT=production`; retain them in non-production environments. | Local production-mode app assertion required before deployment; current production remains 200. | **Closed — verified locally; pending deployment** |
| Q3-VA-007 | Medium | High | Production backend Compose used a source bind mount and Uvicorn `--reload`, increasing mutable-code and development-runtime exposure. | Compose review. | Removed the bind mount and reload mode; production image now runs immutable copied code with four non-root workers. | Production image build/import and Compose validation passed. | **Closed — verified locally; pending deployment** |
| Q3-VA-008 | Medium | High | OCI CIS check 5.2.14 reports that only strong SSH MAC algorithms are not enforced. | OCI CIS scan: 17 pass, 1 fail. | Inspect effective `sshd -T` MACs and all included config files; remove weak MACs; validate config and open a second session before closing the first. | Repeat OCI CIS scan after approved host change. | **Open — production action** |
| Q3-VA-009 | Medium | High | The inner frontend NGINX response lacked several browser defense headers. The public boundary currently supplies HSTS and CSP but not all defense-in-depth headers. | Public header capture and container config review. | Added `nosniff`, `SAMEORIGIN`, strict-origin referrer policy, and a restrictive permissions policy to container NGINX. HSTS and deployment CSP remain the TLS proxy's responsibility. | NGINX config syntax and frontend image build passed. | **Closed — verified locally; pending deployment** |
| Q3-VA-010 | Medium | High | SuperTokens Python SDK remediation requires CDI 5.4; core 11.0 supports only through CDI 5.3. | Reproduced signup failure after SDK update. | Pin SuperTokens core `11.3.7`, which supports CDI 5.4. Avoided 12.0 because direct 11.0-to-12.0 local upgrade did not migrate one schema column correctly. | Existing 11.0-created acceptance volume upgraded to 11.3.7 and the full failed-login suite passed; fresh-volume acceptance also passed. | **Closed — verified locally; production backup/window required** |
| Q3-VA-011 | Medium scanner / Low confidence | Low | Bandit B608 matched string interpolation in OCI Object Storage URL construction as possible SQL injection. | `app/services/s3_service.py`, URL-generation function. | Reviewed manually: the code constructs an HTTPS object URL and executes no SQL. | No SQL API or database call exists in the matched function. | **Closed — false positive** |
| Q3-VA-012 | Low | High | Bandit reported ten swallowed-exception patterns (B110/B112). | Final Bandit scan. | Retain as code-quality backlog; no direct exploit path was established. Add structured logging when these paths are next modified. | No High-severity Bandit findings. | **Open — engineering backlog** |
| Q3-VA-013 | Critical/High scanner records | Medium | Final backend image has 4 Critical and 20 High records. Four Critical and 19 High OS records have no vendor fixed version; the only fixable High is Q3-VA-003. | Trivy 0.73.0 against final local backend image. | Updated to supported Debian 13/Python base, applied available OS upgrades, removed compiler/curl from production, and uninstalled packaging tools. Re-scan when Debian or dependency fixes publish; evaluate distroless only through a separately tested architecture change. | No fixable Critical; one fixable High remains constrained. | **Open — vendor monitoring** |
| Q3-VA-014 | Informational/pass | High | Frontend runtime image has no detected vulnerabilities. | Trivy 0.73.0 final frontend image scan. | Updated Node build stage, NGINX runtime and Alpine packages. | 0 Critical, High, Medium or Low records. | **Informational/pass** |
| Q3-VA-015 | Medium accepted exposure | High | Public TCP 22 remains reachable. | Independent external connection check. | SSH is key-only, Fail2ban is enabled, and OCI Bastion is staged. Keep public SSH only until a tested Bastion cutover is approved. | TCP 22, 80, 443 reachable; 3567, 5173, 5432, 8000, 8520 and 27017 filtered/unreachable. | **Accepted/monitored; cutover pending** |
| Q3-VA-016 | Informational/pass | High | TLS, redirect, CORS and unsafe method baseline is strong. | Public curl/OpenSSL checks. | No change required in this branch. | HTTP redirects to HTTPS; HTTP/2 200; TLS 1.0/1.1 rejected; TLS 1.2/1.3 accepted; untrusted CORS rejected; TRACE/PUT/DELETE return 405. | **Informational/pass** |
| Q3-VA-017 | Informational/pass | High | No secret was detected in tracked source at assessment time. | Gitleaks 8.30.1, redacted tracked-source scan. | Continue secret scanning and rotate any credential ever committed regardless of scanner result. | 0 findings across approximately 9.7 MB tracked source. | **Informational/pass** |

## Production action queue

1. Back up PostgreSQL/MongoDB and rehearse rollback before deploying the application and SuperTokens 11.3 changes.
2. Generate/rotate production PostgreSQL, MongoDB and application secrets through the approved secret-handling process.
3. Deploy locally verified dependency, image, Compose, OpenAPI and header remediation.
4. Validate login, OTP/mail, session controls, failed-login controls, upload and core page flows in the approved window.
5. Correct the effective SSH MAC configuration and patch/remove mapped host packages.
6. Run OCI VSS/CIS and external retest after the maintenance window.
7. Monitor Q3-VA-003 and Q3-VA-013 for vendor fixes.

No item in this queue was represented as completed in production during this assessment.
