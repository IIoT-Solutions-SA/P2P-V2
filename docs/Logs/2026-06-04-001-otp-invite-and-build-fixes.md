# OTP, Invite, and Build Fixes

**Date:** 2026-06-04  
**Scope:** OTP verification flow, invite consumption timing, production build cleanup  
**Repository:** `P2P-V2`  
**Branch:** `umair-backend`

---

## Summary

Fixed 5 issues : OTP state management, invite timing, production build errors, log leakage, and post-OTP success message accuracy.

---

## Issues Fixed

### 1. Frontend production build fails (pre-existing fix, verified)
Cleaned unused imports in 4 files — `App.tsx`, `FileDropZone.tsx`, `Forum.tsx`, `Signup.tsx`.

### 2. Login MFA resend OTP does not update challengeId
- `OtpVerification.tsx:26`: Changed `const challengeId` to `useState`
- `OtpVerification.tsx:182-184`: `setChallengeId(data.challengeId)` after resend

### 3. OTP codes printed to production logs
- `email_verification_service.py:216-223`: Gated `print()` behind `settings.ENVIRONMENT == "development"`
- Logger line no longer references the code

### 4. Post-OTP "signed in" success on session failure
- `supertokens_auth.py:273`: Added `auto_login_success = False`
- `supertokens_auth.py:304`: Set `True` after all steps succeed
- Response now returns `requiresManualLogin: true` + correct message on failure
- Frontend redirects to `/login` when session creation fails

### 5. Invite consumed before OTP verification
- Removed `mark_invitation_used` from `custom-signup`
- Added invite marking in `verify-signup-otp` after OTP verification succeeds
- Unverified invites expire naturally after 7 days

---

## Files Changed

```text
p2p-frontend-app/src/pages/OtpVerification.tsx
p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py
p2p-backend-app/app/services/email_verification_service.py
```

## Tests

```text
p2p-backend-app/tests/test_fixes.py  —  13 tests, all pass
```
