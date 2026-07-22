# Development demo OTP autofill

**Date:** 2026-07-21  
**Status:** Implemented and loaded locally; uncommitted and unpushed

## Request

Make PeerLink demonstrations smoother by automatically filling the six-digit signup/login verification code in the local development environment.

## Implementation

- Added a development-only fixed OTP setting (`123456`).
- OTP generation uses this fixed code only when:
  - `ENVIRONMENT=development`, and
  - `DEV_EMAIL_VERIFICATION_ENDPOINT=true`.
- Added `GET /api/v1/auth/dev-otp`, guarded by the same development-only conditions.
- The OTP page requests the demo code and fills all six input boxes automatically.
- Added a visible “Demo mode” confirmation message.
- Resending a code also refills the demo code automatically.
- Development verification accepts the configured demo code for already-active challenges created before this feature was loaded.
- Production environments return `404` for the demo endpoint and continue using cryptographically random codes.

## Validation

- Frontend production build passed.
- Modified backend modules compile successfully.
- Backend development endpoint returned `123456` with `demo: true`.
- Loaded the rebuilt static frontend into the running container.
- BrowserOps confirmed all six boxes contain `123456` and the verification button is enabled.
- BrowserOps evidence: `20260721-110310-peerlink-demo-otp-autofill`.

## Files changed

- `p2p-backend-app/app/core/config.py`
- `p2p-backend-app/app/services/otp_service.py`
- `p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py`
- `p2p-frontend-app/src/lib/api/auth.ts`
- `p2p-frontend-app/src/pages/OtpVerification.tsx`

## Notes

- This behavior is deliberately unavailable in production.
- No commit or push was performed.
