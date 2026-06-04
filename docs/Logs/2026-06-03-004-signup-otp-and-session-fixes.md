# Signup OTP and Session Fixes

**Date:** 2026-06-04  
**Scope:** Fix signup OTP edge cases and auto-login session persistence bugs  
**Repository:** `P2P-V2`  
**Branch:** `umair-backend`  

---

## Summary

Implemented multiple fixes across the frontend and backend to address issues with the signup OTP workflow, unverified account collisions, and broken auto-login after OTP verification. 

These fixes ensure that:
1. Admins and members can restart an abandoned signup process without hitting "Account already exists" conflicts.
2. Member invitations are not prematurely burned before successful OTP verification.
3. The SuperTokens session is correctly established and persisted on the client after successful signup OTP verification, allowing an immediate, seamless redirect to the dashboard.

---

## Fixes Implemented

1. **Unverified Account Cleanup:** Added logic to `/custom-signup` to safely delete stale records (SuperTokens, PG, Mongo) when a user abandons OTP and tries to sign up again.
2. **Member Invitation Preservation:** Moved `mark_invitation_used` from signup form submission to successful OTP verification, preventing members from being locked out if they miss the OTP.
3. **Frontend Session Persistence:** Added `credentials: 'include'` to the `/verify-signup-otp` fetch request to ensure the browser saves the session cookies.
4. **Dashboard Redirect:** Added `await fetchProfile()` after successful OTP verification to correctly update React auth state before navigating to `/dashboard`.

---

## Files Changed

```text
p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py
p2p-frontend-app/src/pages/OtpVerification.tsx
```
