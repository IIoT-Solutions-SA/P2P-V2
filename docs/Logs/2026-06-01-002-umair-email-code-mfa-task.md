# Umair Task — Email Code Verification and Login MFA

**Date:** 2026-06-01 13:48 AST  
**Repo:** P2P-V2  
**Branch to start from:** `hamza-backend`

## Summary

KACST wants MFA/2FA when users log in.

Current signup email verification uses a link. If we add login OTP separately, a new user may first click a verification link, then receive another code during login. That is awkward.

Change the flow so email verification also uses a short email code. First signup verifies by entering the code. Later logins also send a fresh email code before creating the session.

The code is only needed for a new login/session, not every page refresh while the user is already signed in.

## Task

Implement a code-based auth flow for signup verification and login MFA.

### Signup email verification code flow

- Replace link-style verification UX with a 6-digit email code.
- After signup, send the code to the user's email.
- User enters the code in the app.
- Backend verifies the code and marks the SuperTokens email as verified.
- Store only the hashed code server-side, not plaintext.
- Code should expire after about 5–10 minutes.
- Limit attempts, about 5 attempts.
- Add resend with rate limiting.

### Login MFA email OTP flow

- User enters email + password.
- Backend verifies the password.
- Backend checks the email is already verified.
- Backend sends a fresh 6-digit login OTP.
- Do not create the SuperTokens session yet.
- Return `MFA_REQUIRED` with a temporary `challengeId`.
- User enters the OTP.
- Backend verifies `challengeId` + code.
- Only after a valid OTP, create the SuperTokens session and allow dashboard access.

Open a PR from Umair's branch into `hamza-backend`.
