# Update Email Validation and UI Fixes

**Date:** 2026-06-03  
**Scope:** Email change validation, organization domain matching, SuperTokens 401 retry loop fix, and frontend UI state management.
**Repository:** `P2P-V2`  
**Branch:** `umair-backend`

---

## Summary

Implemented strict validation for the email update flow to prevent users from changing their email to personal domains and to enforce organization domain matching. Also resolved a UI bug where all form buttons would spin during any request, and fixed an infinite retry loop caused by SuperTokens intercepting 401 responses.

Key changes include:
1. **Email Domain Validation:** The email change endpoint now strictly blocks personal email domains (e.g., Gmail, Yahoo) and enforces that the new email matches the user's organization domain.
2. **Safe Database Updates:** The backend now ensures that all validation passes (including password verification) before updating any of the three data stores (SuperTokens, PostgreSQL, MongoDB).
3. **SuperTokens Retry Loop Fix:** Changed the HTTP status code for invalid password errors from `401` to `400` in both email and password update endpoints. This prevents the SuperTokens frontend SDK from interpreting the error as a session expiration and entering a 10-retry refresh loop.
4. **Independent Form Loading States:** Split the shared `loading` state in the frontend `EditProfilePanel` into three independent states (`profileLoading`, `emailLoading`, `passwordLoading`), ensuring only the clicked button shows a loading spinner.
5. **Client-Side Validation UI:** Added inline visual feedback to the email change form, highlighting the input in red when a blocked domain is entered and displaying the required organization domain as a hint.

---

## Files Changed

```text
p2p-backend-app/app/api/v1/endpoints/auth.py
p2p-frontend-app/src/components/EditProfilePanel.tsx
```

---

## Key Implementation Details

### 1. Backend Validation and Safe Updates

**Path:** `p2p-backend-app/app/api/v1/endpoints/auth.py`

- Rewrote the `/email` PUT endpoint to implement a "validate-then-write" pattern.
- Added checks using `get_email_domain` and `is_blocked_domain` to block personal domains.
- Added logic to fetch the user's organization from MongoDB and enforce domain matching.
- Changed `HTTPException` status codes from `401` to `400` for invalid passwords in both `/email` and `/password` endpoints.
- SuperTokens, PostgreSQL, and MongoDB are updated sequentially only after all checks pass.

### 2. Frontend UI and Independent Loading States

**Path:** `p2p-frontend-app/src/components/EditProfilePanel.tsx`

- Separated `loading` into `profileLoading`, `emailLoading`, and `passwordLoading`.
- Added client-side domain validation mirroring the backend logic to prevent unnecessary API calls.
- Updated the "New Email" input field with dynamic CSS classes (`border-red-300`) and inline error messages to provide real-time feedback on domain validation.

---

## Verification

1. **Email Change Validation:**
   - Attempting to use a personal email (e.g., `@gmail.com`) triggers an inline error on the frontend and is blocked by the backend.
   - Attempting to use a domain different from the organization domain triggers an inline error and is blocked.
2. **SuperTokens Retry Fix:**
   - Entering an incorrect password during an email or password change results in a single `400 Bad Request` response, with no repeated session refresh retries visible in DevTools.
3. **UI Loading States:**
   - Clicking "Update Password" only shows a loading spinner on the password button; the email button remains inactive but unchanged. The close (X) button is disabled during any loading state.
