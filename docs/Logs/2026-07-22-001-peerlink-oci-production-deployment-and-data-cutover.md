# PeerLink OCI Production Deployment and Data Cutover

**Date:** 2026-07-22 AST  
**Status:** Completed and verified  
**Production:** `https://p2p.iiotsolutions.sa`  
**OCI VM:** `p2p-server` / `145.241.154.18`  
**Deployed commit:** `631fc0464eb05c59df919330800feb4344389f1d`

## Scope

Deploy the redesigned PeerLink frontend and simplified use-case workflow to the OCI production VM, remove the temporary automatic OTP code-filling feature, retain only the frontend-created drone-arm use case in production, move its three uploaded images into OCI Object Storage, and verify the live system.

## Automatic OTP Filling Removed

The temporary development demonstration behavior was removed before deployment:

- Removed fixed `DEV_OTP_CODE` configuration.
- Removed the development `/api/v1/auth/dev-otp` endpoint.
- Removed fixed-code acceptance from OTP verification.
- Removed the frontend `getDevelopmentOtp` API call.
- Removed initial and resend-time code autofill.
- Removed the “Demo mode” autofill notice.

Production verification:

- `ENVIRONMENT=production`
- `DEBUG=False`
- `DEV_EMAIL_VERIFICATION_ENDPOINT=False`
- `/api/v1/auth/dev-otp` returns HTTP `404`.
- A deployed-source scan found no `DEV_OTP_CODE`, `dev-otp`, `getDevelopmentOtp`, or autofill notice.
- Normal cryptographically random emailed OTP behavior remains active.

## Code Deployment

The application changes and implementation logs were committed and pushed to `origin/hamza-backend`:

```text
631fc04 feat: deploy redesigned PeerLink workspace and simplified use cases
```

GitHub Actions deployment:

```text
Workflow: Deploy to OCI
Run: 29934626439
Result: success
URL: https://github.com/IIoT-Solutions-SA/P2P-V2/actions/runs/29934626439
```

The Mini-PC-only `docker/docker-compose.yml` development override was deliberately excluded from the commit, preventing local development values from replacing OCI production settings.

## Production Data Cutover

Before changing production data, full MongoDB and PostgreSQL backups were created on the VM:

```text
/home/ubuntu/P2P-V2/deploy-backups/20260722-184506-AST/
  mongodb-pre-single-usecase.archive.gz
  postgres-pre-single-usecase.dump
```

Production previously contained 36 use-case documents. They were replaced with the single use case created and validated through the frontend:

```text
ID: 6a5e3282b47cf1157a5333dd
Title: AI-Powered Drone Arm Color Verification Station
Owner: Hamza Feroze / hamza@iiotsolutions.sa
Organization: IIoT Solutions
```

The production document retains the simplified contributor fields:

- Problem
- Technology and approach
- Budget
- Outcomes
- Challenges

During import, the installed `mongoimport` version rejected the optional `--jsonFormat=canonical` argument after the old collection had been cleared. The document was immediately imported successfully without that unsupported option. The pre-change database backups were already complete and available before mutation. Final production count was verified as exactly one use case.

## OCI Object Storage

The three frontend-uploaded use-case images were copied from local development storage to the production bucket:

```text
Bucket: p2p-usecase-media
Prefix: usecase-images/6a5e3282b47cf1157a5333dd/
```

Verified objects:

| Object | MIME type | Size |
|---|---|---:|
| `42227b3c-639c-4609-816d-5b7c3324e0c4.png` | `image/png` | 505,844 bytes |
| `fbd9f038-66d5-4d2e-8812-0a083c3f7fe0.jpg` | `image/jpeg` | 196,944 bytes |
| `505adbb7-b882-4ee4-8694-b8159167c3dc.jpg` | `image/jpeg` | 74,145 bytes |

All three public OCI object URLs returned HTTP `200` with the correct content type and byte size. The MongoDB use-case image list now contains only these OCI Object Storage URLs. PostgreSQL contains three corresponding `user_media` records owned by Hamza's production account.

Production media record verification:

| Type | Records | OCI Object Storage URLs |
|---|---:|---:|
| Forum attachments | 31 | 31 |
| Profile pictures | 2 | 2 |
| Use-case media | 3 | 3 |

New production uploads continue to use OCI Object Storage for profile pictures, forum attachments, and use-case images/videos. Production fails closed if object storage is unavailable; local filesystem fallback applies only outside production.

## Validation

Local checks:

- Frontend TypeScript/Vite production build passed.
- Backend modules compiled successfully.
- OTP/invitation unit suite passed: 13 tests.
- `git diff --check` passed after whitespace cleanup.

Production checks:

- `p2p-backend`: healthy.
- `p2p-frontend`: running.
- `p2p-supertokens`: running.
- `p2p-postgres`: healthy.
- `p2p-mongodb`: healthy.
- VM repository at commit `631fc046`.
- No recent backend errors or tracebacks found after deployment.
- Production use-case count: 1.
- Production use-case media records: 3.
- All three image objects returned HTTP `200`.

BrowserOps rendered validation:

```text
Task: 20260722-184639-peerlink-oci-production-deployment-validation
Evidence: /home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260722-184639-peerlink-oci-production-deployment-validation
```

The live HTTPS site loaded the redesigned PeerLink public workspace and the redesigned sign-in page successfully.

## Notes

- Historical object-storage files were not destructively deleted; they remain recoverable but are no longer referenced by the active use-case library.
- The production data cutover is reversible using the timestamped MongoDB and PostgreSQL backups.
- Local development still has its separate one-use-case database and local upload files; production now has its own copied document and OCI-hosted media.
