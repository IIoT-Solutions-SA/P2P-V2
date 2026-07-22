# PeerLink Full Frontend Route Audit

**Date:** 2026-07-18 AST  
**Scope:** Every routed React page plus shared authenticated controls  
**Result:** Full redesign completion pass finished; desktop and mobile acceptance checks passed

## Validation

- `npm run build`: passed
- `git diff --check`: passed
- Docker backend, MongoDB, and PostgreSQL: healthy
- Frontend and SuperTokens: running

BrowserOps evidence:

- Public route audit: `20260718-200531-peerlink-full-frontend-page-audit`
- Authenticated route audit: `20260718-200857-peerlink-authenticated-page-audit-fresh-profile`

## Route Matrix

| Route | State tested | Result |
|---|---|---|
| `/home` | Public | Redesigned and rendered correctly |
| `/login` | Public | Redesigned and functional through credentials/MFA flow |
| `/signup` | Public | Redesigned organization signup page rendered correctly |
| `/join` | Missing invitation token | Redesigned safe invalid-invitation state rendered correctly |
| `/forgot-password` | Public | Redesigned recovery page rendered correctly |
| `/reset-password` | Missing reset token | Redesigned safe invalid-token state rendered correctly |
| `/verify-otp` | Generic and real login MFA | Redesigned; OTP entry and successful backend verification exercised |
| `/verify-email` | Pending state | Redesigned pending-verification state rendered correctly |
| `/auth/verify-email` | Missing token | Redesigned verification state rendered correctly |
| `/dashboard` | Authenticated Member | Redesigned; live data rendered |
| `/forum` | Authenticated Member | Redesigned; live discussions/categories/stats rendered |
| `/connect` | Authenticated Member | Redesigned; 18 external users and 6 separate organization members reported |
| `/usecases` | Authenticated Member | Redesigned; live library and controls rendered |
| `/usecases/:company_slug/:title_slug` | Authenticated Member | Redesigned; detailed live use-case content rendered |
| `/submit` | Authenticated Member | Redesigned seven-step Network Workspace submission flow; desktop and mobile verified |
| `/organization` | Authenticated Member | Redesigned member view rendered correctly |
| `/organization` | Administrator | Previously verified in `20260718-154613-peerlink-member-role-full-acceptance`; admin-only tabs and controls render |
| `/user-management` | Authenticated | Intentionally redirects to `/organization` |
| Unknown route | Public | Intentionally redirects to `/home` |

## Gaps Found During Initial Audit

All five gaps below were resolved in the completion pass documented at the end of this log.

### 1. Submit Use Case is not visually ported

`src/pages/SubmitUseCase.tsx` still uses the previous large centered wizard/form presentation. It sits inside the new authenticated shell, but its content design does not match the new Network Workspace visual system used by Dashboard, Forum, People, Use Cases, Use Case Detail, and Organization.

BrowserOps evidence:

- `screenshots/036-submit-use-case-page.png`

### 2. Header Search is a dead control

The shared `Search workspace` button renders on every authenticated page but has no `onClick` handler. BrowserOps click produced no state, route, modal, or visible change.

Code location:

- `p2p-frontend-app/src/components/layout/AuthenticatedLayout.tsx`

Evidence:

- `screenshots/043-after-search-control.png`

### 3. Header Notifications is a dead control

The shared `Notifications` button and blue unread indicator render, but the button has no `onClick` handler. BrowserOps click produced no panel, route, modal, or state change.

Evidence:

- `screenshots/045-after-notifications-control.png`

### 4. Use Case Detail has two dead CTA buttons

The following buttons render without handlers:

- `Connect with implementation team`
- `View profile`

Other detail actions are wired:

- Save calls bookmark behavior
- Share calls share behavior
- Download PDF calls `window.print()`
- Back returns to the library

Code location:

- `p2p-frontend-app/src/pages/UseCaseDetail.tsx`

### 5. Local 127.0.0.1 authentication origin mismatch

When the frontend is opened as `http://127.0.0.1:5173`, the current environment configuration selects:

- API: `http://localhost:8000`
- Website: `http://localhost:5173`

Credentials and MFA can succeed, but the resulting SuperTokens session is not recognized by the frontend on the `127.0.0.1` origin, causing a return to `/login`. Opening the frontend consistently as `http://localhost:5173` works and reaches `/dashboard`.

This does not affect the Tailscale deployment path, which uses same-origin nginx proxying, but it is a local-development reliability bug because the frontend treats `localhost` and `127.0.0.1` inconsistently.

## Working Shared Features

- Authenticated shell and navigation
- Member profile/account modal
- Email and password account forms render in the modal
- Logout
- Dashboard filters and links
- Forum data and interaction surfaces
- People directory, organization/location filtering, external-only boundary
- Use Cases search/category/sort/library
- Use Case Detail rendering
- Member/admin Organization separation
- Public authentication and recovery states

## Accepted Limitation

Hamza accepted leaving People `Collaborate` as its current `mailto:` action for now. `Collaborate` and `Contact` remain email-based rather than in-platform connection requests.

## Build Note

Vite reports a non-blocking bundle-size warning: the primary JavaScript bundle is approximately 1.34 MB before gzip and 352.60 KB gzip. The build still succeeds, but route-level code splitting remains a future performance optimization.

## Completion Pass

All minimum completion items were implemented and validated:

1. **Submit Use Case** was ported into the Network Workspace system with a seven-step rail, square panels/buttons, responsive horizontal step navigation, preserved validation/draft/submission behavior, and autosave status.
2. **Workspace Search** now opens a searchable command panel and routes to matching workspace sections.
3. **Notifications** now opens a live network-activity panel sourced from dashboard activity; its unread indicator clears after opening.
4. **Use Case Detail contact actions** now open a real implementation-contact profile panel with directory matching, organization/title/location context, email action, and People-directory navigation.
5. **Local origin handling** now keeps frontend/API origins aligned for both `localhost` and `127.0.0.1`. A complete credentials + MFA flow reached `http://127.0.0.1:5173/dashboard` successfully.
6. **Responsive acceptance** was completed at a 390×844 CSS viewport for Dashboard, Forum, People, Use Cases, Submit, Use Case Detail, and Organization. Every tested route reported `documentElement.scrollWidth === innerWidth === 390`; Submit's intended step rail scrolls inside its own bounded container.

Final BrowserOps evidence in authenticated task `20260718-200857-peerlink-authenticated-page-audit-fresh-profile`:

- Submit desktop: `screenshots/087-submit-use-case-desktop-acceptance-final.png`
- Workspace search: `screenshots/052-workspace-search-final.png`
- Notifications: `screenshots/055-notifications-panel-final.png`
- Implementation contact profile: `screenshots/065-implementation-contact-profile-final.png`
- Submit mobile: `screenshots/071-submit-use-case-mobile-acceptance-final.png`
- Dashboard mobile: `screenshots/073-mobile-dashboard-acceptance-final.png`
- Forum mobile: `screenshots/075-mobile-forum-acceptance-final.png`
- People mobile: `screenshots/077-mobile-people-acceptance-final.png`
- Use Cases mobile: `screenshots/079-mobile-use-cases-acceptance-final.png`
- Use Case Detail mobile: `screenshots/083-mobile-use-case-detail-acceptance-final.png`
- Organization mobile: `screenshots/085-mobile-organization-acceptance-final.png`

Origin-normalization evidence in public task `20260718-200531-peerlink-full-frontend-page-audit`:

- Authenticated dashboard on `127.0.0.1`: `screenshots/044-dashboard-127-origin-fixed.png`

### Public Homepage Fidelity Correction

A stakeholder screenshot review exposed that the React public homepage had retained a conventional top navbar even though the approved source mockup, `design-mockups/homepage-redesign/peerlink-homepage-network-workspace.html`, specified a public Network Workspace sidebar. The React route was corrected to restore the approved public sidebar with Overview, Network, Saudi Map, Use Cases, Join, public-preview guidance, and sign-in/join actions.

The same review exposed that the public map rendered no use-case markers. Two causes were confirmed in BrowserOps:

- The component requested `limit=200`, while the backend rejected that query with HTTP 422.
- After reducing the limit, the public route still received HTTP 401 from the authenticated use-case feed.

The map now uses the authenticated live feed when available and curated public preview markers when the protected feed is unavailable. Public clusters visibly represent 4 Riyadh, 2 Jeddah, and 3 Dammam use cases. Teal marker/cluster styling was restored so the dots remain clearly visible in screenshots.

Corrected BrowserOps evidence in task `20260718-204339-peerlink-leadership-public-pack`:

- Public sidebar homepage: `screenshots/014-final-replacement-01-homepage-sidebar.png`
- Public Saudi map with visible use-case clusters: `screenshots/015-final-replacement-02-map-use-case-dots.png`

Final technical validation:

- `npm run build`: passed
- `git diff --check`: passed
- Docker frontend rebuilt and running
- Backend, MongoDB, and PostgreSQL healthy; SuperTokens running
- Remaining non-blocking warning: primary JS bundle is approximately 1.36 MB before gzip / 356.39 KB gzip; route-level code splitting is future optimization

## Forum Image and Video Posting Restoration

The forum media path was restored for both new discussions and nested replies/comments:

- Added multi-file photo/video selection, local previews, removal controls, limits, upload progress copy, and actionable errors to both forum composers.
- Supported JPEG, PNG, WebP, GIF, MP4, and WebM; up to 5 files per post/reply; images up to 5 MB and videos up to 50 MB.
- Wired post media uploads after discussion creation and reply media uploads after reply creation.
- Added responsive image galleries and native video playback to top-level posts and every nested reply.
- Extended the backend upload route to authorize and attach media against either a forum post or a forum reply, enforce the five-file server limit, and serialize reply attachments in thread responses.
- Added a development-only persistent local-media fallback because the configured OCI S3 compatibility credentials currently return `SignatureDoesNotMatch`; production still fails closed rather than storing media locally.
- Rebuilt the frontend and backend containers. TypeScript/Vite build, Python compile, `git diff --check`, backend health, upload-route OpenAPI shape, and local media serving checks passed.
- BrowserOps reached the refreshed site, but its saved PeerLink sessions had expired and redirected to `/login`, so final authenticated click-through remains pending a fresh user sign-in.

## Conclusion

The routed PeerLink frontend redesign and the specifically identified dead-control/origin gaps are complete and acceptance-tested. Forum image/video support is implemented and loaded locally, with final signed-in BrowserOps click-through pending. It is ready for stakeholder review. No commit, push, or production deployment was performed.
