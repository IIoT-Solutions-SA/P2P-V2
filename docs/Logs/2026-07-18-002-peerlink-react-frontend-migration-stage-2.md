# PeerLink React Frontend Migration Stage 2

**Date:** 2026-07-18  
**Scope:** Public homepage and complete pre-authentication feature family  
**Backend changes:** None  
**Commit/push:** Not performed

## Objective

Implement Stage 2 of the PeerLink React migration on top of the accepted Stage 1 foundation.

Authoritative references:

- `design-mockups/homepage-redesign/peerlink-homepage-network-workspace.html`
- `design-mockups/auth-redesign/html/`
- `docs/Logs/2026-07-16-001-frontend-redesign-discovery-and-dashboard-mockups.md`
- `docs/Logs/2026-07-16-002-network-workspace-direction-selection.md`
- `docs/Logs/2026-07-16-006-authentication-html-mockups.md`
- `docs/Logs/2026-07-16-009-clickable-html-prototype-integration.md`
- `docs/Logs/2026-07-18-001-peerlink-react-frontend-migration-stage-1.md`

## Implementation Summary

### Homepage

Rebuilt `p2p-frontend-app/src/pages/LandingPage.tsx` in the selected Network Workspace direction:

- Preserved the existing simulation video asset: `/Video_Redo_Realistic_Technology.mp4`.
- Preserved the existing public headline statistics and figures:
  - `1,200+` connected factories
  - `89` proven use cases
  - `SAR 45M+` cost savings achieved via the existing `SaudiRiyalCurrency` component
  - `67%` average efficiency gain
- Preserved the existing interactive Saudi map by keeping `InteractiveMap` in the homepage route.
- Preserved the existing featured case-study route targets and success-story figures.
- Replaced the old generic blue/white landing-page composition with warm workspace surfaces, deep navy/teal structure, compact sections, and responsive production layouts.

### Authentication UI Foundation

Added `p2p-frontend-app/src/components/auth/AuthScaffold.tsx`:

- Shared Network Workspace pre-auth rail.
- Shared form card and context panel structure.
- Shared alert, heading, field-error, and password-requirement primitives.
- Responsive desktop/mobile behavior matching the auth mockup family.
- Uses existing local React/lucide/Tailwind stack and does not introduce CDN assets or backend assumptions.

### Authentication Routes Migrated

Migrated these route components to the Stage 2 auth family:

- `/login` -> `Login.tsx`
- `/signup` -> `Signup.tsx`
- `/join` -> `MemberSignup.tsx`
- `/forgot-password` -> `ForgotPassword.tsx`
- `/reset-password` -> `ResetPassword.tsx`
- `/verify-otp` -> `OtpVerification.tsx`
- `/verify-email` -> `EmailVerificationPending.tsx`
- `/auth/verify-email` -> `EmailVerificationSuccess.tsx`

Covered states include:

- default form states
- inline validation states
- backend error states
- loading/progress states
- invalid invitation state
- invalid/missing reset token state
- password-reset success state
- OTP invalid-code, expired-code, max-attempts, resend cooldown, and success states
- email-verification pending, success, and secure-link error states

## Backend Contract Audit

No backend behavior was changed.

### Preserved contracts

- Login still calls `POST /api/v1/auth/custom-signin` through `AuthContext.login()`.
- Trusted-device/session behavior remains owned by the backend and SuperTokens.
- `MFA_REQUIRED` login responses still navigate to `/verify-otp?purpose=login_mfa&email=...` with `challengeId` in route state.
- Login MFA still calls `POST /api/v1/auth/verify-login-otp`.
- Organization signup still calls `POST /api/v1/auth/custom-signup` with the existing backend payload names mapped by `authApi.signup()`:
  - `companyName`
  - `industrySector`
  - `companySize`
  - `city`
- Signup verification still calls `POST /api/v1/auth/verify-signup-otp`.
- Invitation signup still validates `GET /api/v1/invites/validate/{token}` and carries `inviteToken` into signup and signup OTP verification.
- Password recovery still calls `POST /api/v1/auth/forgot-password`.
- Password reset still calls `POST /api/v1/auth/reset-password` with `{ token, newPassword }`.
- Email-link verification route still calls the existing frontend contract for `/api/v1/auth/user/email/verify`.
- Authenticated feature-family routes were not migrated in this stage.

### API client changes

Extended `p2p-frontend-app/src/lib/api/auth.ts` and `types.ts` with typed methods for:

- `verifySignupOtp`
- `forgotPassword`
- `resetPassword`
- `verifyEmailToken`
- `validateInvitation`

Changed Stage 2 auth pages to use `authApi` instead of duplicating fetch logic. Direct auth/invite fetches that remain are in authenticated feature files outside this stage's scope.

## Route Semantics

- Public routes still render under the Stage 1 `PublicLayout`.
- Auth routes still render under the Stage 1 `AuthLayout`.
- `/verify-otp` remains the shared route for `signup_verify` and `login_mfa`.
- `/verify-email` now renders the pending verification screen instead of being a dead redirect.
- `/auth/verify-email` remains the secure link verification route.
- Authenticated routes and Stage 1 shell behavior were not expanded into unrelated feature-family migration work.

## Files Changed

Modified:

- `p2p-frontend-app/src/App.tsx`
- `p2p-frontend-app/src/lib/api/auth.ts`
- `p2p-frontend-app/src/lib/api/types.ts`
- `p2p-frontend-app/src/pages/LandingPage.tsx`
- `p2p-frontend-app/src/pages/Login.tsx`
- `p2p-frontend-app/src/pages/Signup.tsx`
- `p2p-frontend-app/src/pages/MemberSignup.tsx`
- `p2p-frontend-app/src/pages/ForgotPassword.tsx`
- `p2p-frontend-app/src/pages/ResetPassword.tsx`
- `p2p-frontend-app/src/pages/OtpVerification.tsx`
- `p2p-frontend-app/src/pages/EmailVerificationPending.tsx`
- `p2p-frontend-app/src/pages/EmailVerificationSuccess.tsx`

Added:

- `p2p-frontend-app/src/components/auth/AuthScaffold.tsx`
- `docs/Logs/2026-07-18-002-peerlink-react-frontend-migration-stage-2.md`

## Validation

### Local source checks

The repository-local npm shims still have the Stage 1 permission issue:

```bash
npm run build
```

Result: Failed before source validation with `sh: 1: tsc: Permission denied`.

Direct TypeScript entrypoint:

```bash
node node_modules/typescript/bin/tsc -b
```

Result: Passed.

Targeted lint:

```bash
node node_modules/eslint/bin/eslint.js \
  src/pages/LandingPage.tsx \
  src/pages/Login.tsx \
  src/pages/Signup.tsx \
  src/pages/MemberSignup.tsx \
  src/pages/ForgotPassword.tsx \
  src/pages/ResetPassword.tsx \
  src/pages/OtpVerification.tsx \
  src/pages/EmailVerificationPending.tsx \
  src/pages/EmailVerificationSuccess.tsx \
  src/components/auth/AuthScaffold.tsx \
  src/lib/api/auth.ts \
  src/lib/api/types.ts \
  src/App.tsx
```

Result: Passed.

Direct Vite build in the repository dependency tree:

```bash
node node_modules/vite/bin/vite.js build
```

Result: Failed before source build because the stale local dependency tree is missing Rollup's optional native package `@rollup/rollup-linux-x64-gnu`.

### Clean production build

To avoid modifying repo dependencies, the frontend source was copied to `/tmp/p2p-frontend-stage2-validate` excluding `node_modules` and `dist`.

```bash
npm ci --include=optional
```

Result: Passed.

Notes:

- 243 packages installed.
- 0 vulnerabilities.
- npm warned that `@simplewebauthn/types@12.0.0` is deprecated.
- npm warned that `browser-tabs-lock@1.3.0` has an unapproved install script.

```bash
npx tsc -b && npm run build
```

Result: Passed.

Build output:

- `dist/index.html`
- `dist/assets/index-dYh_uDq-.css`
- `dist/assets/index-DbQjy22m.js`

Vite emitted the existing large-chunk warning because the app is bundled as one large client chunk. No code-splitting changes were made in Stage 2.

## Boundaries

- No backend files were modified.
- No Docker files were modified.
- No authenticated dashboard, forum, people, use-case, submit, organization-management, or team-management feature-family migration was implemented.
- No commit or push was performed.
