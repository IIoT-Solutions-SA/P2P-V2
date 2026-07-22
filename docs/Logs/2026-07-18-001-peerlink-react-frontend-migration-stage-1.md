# PeerLink React Frontend Migration Stage 1

**Date:** 2026-07-18  
**Scope:** Shared React frontend foundation for the approved Network Workspace migration  
**Backend changes:** None  
**Commit/push:** Not performed

## Objective

Begin Stage 1 of the approved PeerLink React frontend migration by creating reusable frontend foundations that later feature-family migrations can build on without changing the shared shell.

The authoritative references reviewed for this stage were:

- `design-mockups/dashboard-redesign/concept-c-network-workspace.html`
- `design-mockups/homepage-redesign/peerlink-homepage-network-workspace.html`
- `design-mockups/auth-redesign/html/`
- `design-mockups/forum-redesign/`
- `design-mockups/people-redesign/`
- `design-mockups/usecases-redesign/`
- `design-mockups/manage-team-redesign/`
- `docs/Logs/2026-07-16-001` through `docs/Logs/2026-07-16-009`

## Audit Findings

### Existing frontend structure

- The React app uses React 19, TypeScript, Vite, React Router DOM v7, Tailwind CSS 4, Radix primitives, and lucide-react icons.
- Before this work, `App.tsx` rendered one global `Navigation` and `MobileBottomNav` outside the route tree.
- Protected routes were individually wrapped with `ProtectedRoute`.
- Auth state is centralized in `AuthContext` and uses SuperTokens session detection plus `/api/v1/auth/me`.
- Feature pages currently own most of their fetch calls directly:
  - `Dashboard.tsx`
  - `Forum.tsx`
  - `UseCases.tsx`
  - `UseCaseDetail.tsx`
  - `SubmitUseCase.tsx`
  - `UserManagement.tsx`
  - `Connect.tsx`
  - several profile/media/auth surfaces

### Existing routing behavior

- Public routes: `/home`, `/login`, `/signup`, `/join`, `/forgot-password`, `/reset-password`, `/verify-otp`, `/verify-email`, `/auth/verify-email`.
- Authenticated routes: `/dashboard`, `/forum`, `/submit`, `/usecases`, `/usecases/:company_slug/:title_slug`, `/organization`, `/user-management`, `/connect`.
- Unknown routes previously had no intentional designed fallback.

### Authentication behavior preserved

- `ProtectedRoute` still blocks unauthenticated access and redirects to `/login` with `state.from`.
- `AuthContext` still:
  - checks SuperTokens session existence on load,
  - fetches `/api/v1/auth/me`,
  - supports trusted-device signin,
  - supports `MFA_REQUIRED` signin response,
  - verifies login MFA OTP,
  - resends signup/login OTPs,
  - creates admin/member signup payloads with the existing backend field names,
  - signs out through `/api/v1/auth/custom-signout` and `Session.signOut()`.

### Backend endpoint contracts inventoried

Mounted router prefixes are defined in `p2p-backend-app/app/api/v1/api.py`:

- `/api/v1/auth`
- `/api/v1/health`
- `/api/v1/dashboard`
- `/api/v1/forum`
- `/api/v1/use-cases`
- `/api/v1/invites`
- `/api/v1/media`

Important contract groups reviewed:

- Auth/session: `custom-signup`, `verify-signup-otp`, `custom-signin`, `verify-login-otp`, `resend-otp`, `forgot-password`, `reset-password`, `custom-signout`, `me`, `profile`, `email`, `password`, `users/organization`.
- Dashboard: stats, activities, bookmarks, drafts, draft CRUD, recalculate stats.
- Forum: post CRUD, categories, post detail, likes, replies, stats, contributors, bookmarks.
- Use cases: list/detail, create/update/delete, drafts, publish draft, like, bookmark, categories, stats, contributors.
- Invitations: send, validate, all, pending, mark-used, delete.
- Media: profile picture, forum attachment, use-case media, delete media, user media.

No backend blocker was found for Stage 1. No backend files were modified.

## Implementation

### Design tokens and global styling

Updated `p2p-frontend-app/src/index.css` with Network Workspace tokens:

- Warm paper workspace background.
- Deep navy rail color.
- Off-white surfaces.
- Teal, blue, amber, success, and danger accents.
- Shared border, ring, shadow, rail width, compact rail width, and topbar height variables.
- Tailwind CSS 4 `@theme inline` bindings for existing shadcn-style primitives.
- Shared utility classes:
  - `.peer-workspace`
  - `.peer-panel`
  - `.peer-eyebrow`
  - `.font-display`

### Shared route shell

Added `p2p-frontend-app/src/components/layout/`:

- `navigation.ts`
  - Shared navigation definitions for Workspace, Organization, and Public groups.
  - Canonical authenticated destinations: Dashboard, Forum, People, Use Cases, Submit Story.
  - Organization destination is visible to members and administrators and points to canonical `/organization`.
  - The Organization sidebar label uses the authenticated organization name when available.

- `BrandMark.tsx`
  - Shared PeerLink brand mark used by public and authenticated layouts.

- `PublicLayout.tsx`
  - Fixed public header with PeerLink branding, public navigation, and signin/signup/workspace actions.
  - `AuthLayout` provides a stable wrapper for authentication routes.

- `AuthenticatedLayout.tsx`
  - Desktop dark rail at `232px`.
  - Tablet compact icon rail.
  - Mobile slide-out menu.
  - Sticky workspace topbar with breadcrumb, network status, search, and notification affordances.
  - Shared user/profile rail wired to the existing `EditProfilePanel`.
  - Shared logout behavior.
  - Organization navigation is always present for authenticated users and dynamically labeled.

- `Organization.tsx`
  - Truthful role-aware placeholder for the shared organization route.
  - Members receive a read-only organization/member route boundary.
  - Administrators receive the same shared route with explicit extension points for later management controls.
  - The placeholder does not redirect members to People or claim organization access is denied.

Updated `App.tsx` so routes are grouped by layout:

- Public routes render inside `PublicLayout`.
- Auth routes render inside `PublicLayout` + `AuthLayout`.
- Authenticated routes render inside `ProtectedRoute` + `AuthenticatedLayout`.
- `/organization` is the canonical shared organization route for both roles.
- `/user-management` is preserved as a compatibility redirect to `/organization`.
- Unknown routes redirect to `/home`.

The existing page components are intentionally still rendered as-is inside the new shell. This preserves current feature behavior while giving later migration stages stable layout boundaries.

### People route correction

Updated `Connect.tsx` only enough to remove contradictions against the approved navigation model:

- Administrators are no longer redirected away from People.
- The route no longer remains permanently stuck in `Loading members...`.
- The existing coming-soon placeholder can render for both members and administrators until the People feature migration replaces it.

### Shared states

Added `p2p-frontend-app/src/components/shared/AppState.tsx`:

- `LoadingState`
- `EmptyState`
- `ErrorState`
- `AccessDeniedState`

Updated `ProtectedRoute.tsx` to use the shared `LoadingState` for session checking.

### Typed API foundation

Added `p2p-frontend-app/src/lib/api/`:

- `types.ts`
  - Shared response types for current user, auth OK, signup, MFA required, OTP errors, and message responses.

- `client.ts`
  - `apiFetch<T>()` wrapper around native fetch.
  - Defaults `credentials: "include"` to preserve session-cookie behavior.
  - JSON body handling for object payloads.
  - `ApiError` carrying HTTP status and parsed backend payload.
  - `api.get/post/put/delete` helpers.

- `auth.ts`
  - Typed auth API methods for:
    - `/api/v1/auth/me`
    - `/api/v1/auth/custom-signin`
    - `/api/v1/auth/custom-signup`
    - `/api/v1/auth/verify-login-otp`
    - `/api/v1/auth/resend-otp`
    - `/api/v1/auth/custom-signout`

Updated `AuthContext.tsx` to use `authApi` for shared auth/session calls. Direct feature-family fetch calls were not broadly migrated in Stage 1 to avoid changing individual feature behavior before their dedicated sessions.

## Files Changed

Modified:

- `p2p-frontend-app/src/App.tsx`
- `p2p-frontend-app/src/components/ProtectedRoute.tsx`
- `p2p-frontend-app/src/contexts/AuthContext.tsx`
- `p2p-frontend-app/src/index.css`
- `p2p-frontend-app/src/pages/Connect.tsx`

Added:

- `p2p-frontend-app/src/components/layout/AuthenticatedLayout.tsx`
- `p2p-frontend-app/src/components/layout/BrandMark.tsx`
- `p2p-frontend-app/src/components/layout/PublicLayout.tsx`
- `p2p-frontend-app/src/components/layout/navigation.ts`
- `p2p-frontend-app/src/components/shared/AppState.tsx`
- `p2p-frontend-app/src/lib/api/auth.ts`
- `p2p-frontend-app/src/lib/api/client.ts`
- `p2p-frontend-app/src/lib/api/types.ts`
- `p2p-frontend-app/src/pages/Organization.tsx`
- `docs/Logs/2026-07-18-001-peerlink-react-frontend-migration-stage-1.md`

## Validation

### Restored worktree limitation

The restored repository worktree has a stale tracked `node_modules` tree:

- Some npm shims under `p2p-frontend-app/node_modules/.bin` lack execute permissions.
- The restored dependency tree can fail direct Vite execution because a stale Rollup optional native package is absent.
- A clean Vite 8 install uses `@rolldown/binding-linux-x64-gnu`; the stale Rollup failure is therefore an environment/dependency-tree issue, not a source-code build error.

No `node_modules`, `package.json`, or `package-lock.json` changes are part of this Stage 1 work.

### Reproducible clean validation method

To validate without dirtying the repository dependency tree, the frontend source was copied to `/tmp/p2p-frontend-stage1-validate` excluding `node_modules` and `dist`, then dependencies were installed there:

```bash
rm -rf /tmp/p2p-frontend-stage1-validate
mkdir -p /tmp/p2p-frontend-stage1-validate
tar --exclude='./node_modules' --exclude='./dist' -cf - . | tar -xf - -C /tmp/p2p-frontend-stage1-validate
cd /tmp/p2p-frontend-stage1-validate
npm ci --include=optional
```

Result: Passed.

Notes:

- `npm ci --include=optional` added 243 packages in the temp copy.
- Audit found 0 vulnerabilities.
- npm warned that `@simplewebauthn/types@12.0.0` is deprecated.
- npm warned that `browser-tabs-lock@1.3.0` has an install script not yet covered by `allowScripts`.

```bash
npx tsc -b
```

Result: Passed.

```bash
npm run build
```

Result: Passed.

Build output:

- `dist/index.html`
- `dist/assets/LOGIN-B6CKtIse.png`
- `dist/assets/index-B-yK9zRL.css`
- `dist/assets/index-DDZWABlS.js`

Vite reported the existing large chunk warning for the application bundle.

```bash
npx eslint src/App.tsx src/components/ProtectedRoute.tsx src/components/layout/AuthenticatedLayout.tsx src/components/layout/PublicLayout.tsx src/components/layout/BrandMark.tsx src/components/layout/navigation.ts src/components/shared/AppState.tsx src/lib/api/client.ts src/lib/api/auth.ts src/lib/api/types.ts src/pages/Organization.tsx src/pages/Connect.tsx
```

Result: Passed.

### Full lint baseline

The earlier full `npm run lint` from the repository worktree ran but failed due to pre-existing repository lint issues. It reported 103 problems across existing files, including:

- existing `any` usage,
- existing empty blocks,
- existing hook dependency warnings,
- existing fast-refresh export warnings in shared shadcn files,
- existing unused variables,
- existing regex lint violations.

Those baseline lint issues were not broadened into this Stage 1 correction.

## Extension Points For Later Feature Sessions

### 1. Homepage

- Implement in an isolated homepage feature directory, then keep route `/home` inside `PublicLayout`.
- Reuse `BrandMark`, global tokens, and public navigation behavior.
- Do not alter `AuthenticatedLayout` for homepage-specific presentation.

### 2. Authentication

- Implement login, signup, invite signup, OTP/MFA, forgot password, reset password, success, and error screens inside an authentication feature directory.
- Reuse `AuthLayout`, `authApi`, `ApiError`, and shared state primitives.
- Preserve current backend payload names and response statuses.

### 3. Dashboard

- Replace only the `/dashboard` page body.
- Keep `AuthenticatedLayout` unchanged.
- Use `api.get` for dashboard stats, activities, bookmarks, and drafts.
- Use `LoadingState`, `EmptyState`, and `ErrorState` for request phases.

### 4. Forum

- Replace Forum screens inside a Forum feature directory.
- Use shared shell navigation and keep route `/forum`.
- Add typed wrappers for forum endpoints in `src/lib/api/forum.ts`.
- Preserve post, reply, like, bookmark, draft, and media contracts.

### 5. People

- Replace existing `Connect.tsx` through a People feature directory while preserving route `/connect`.
- People is available to all authenticated users, including administrators.
- Add typed wrappers for people/member discovery endpoints once the backend contract is confirmed.

### 6. Use Cases

- Replace `/usecases`, detail, and submission surfaces in a Use Cases feature directory.
- Add typed wrappers for use-case list/detail/draft/bookmark/like/media endpoints.
- Keep public map/homepage use-case discovery separate unless explicitly approved.

### 7. Organization

- Replace the placeholder page at `/organization` with the full shared organization experience.
- Keep `/organization` available to both members and administrators.
- Members should receive the read-only organization profile, roster, administrators/contact, organization use cases, and organization activity.
- Administrators should receive the same shared route plus invitations, permissions, settings, member administration, and role-management controls.
- Keep `/user-management` as a compatibility redirect unless a later migration deliberately retires it.
- Add typed wrappers for invitation and organization-member endpoints.
- Reuse `AccessDeniedState` for direct attempts to open admin-only organization views.

## Known Boundaries

- Existing feature pages still contain their original card-heavy styling and direct fetch calls. This is intentional for Stage 1 and should be addressed feature-by-feature.
- `Navigation.tsx` remains in the tree for now but is no longer used by `App.tsx`.
- Notification and search controls in the topbar are visual shell affordances only; no notification/search backend wiring was added in Stage 1.
- No backend changes were made.
- No commit or push was performed.
