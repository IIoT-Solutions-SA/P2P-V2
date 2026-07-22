# People Network Directory React Port

Date: 2026-07-18 AST  
Owner: Nemo  
Status: Implemented and build-validated

## Product correction

The People route is now a PeerLink-wide collaborator directory rather than a duplicate of the current organization roster.

- People: discovery by expertise, organization, industry, and location across the authenticated PeerLink network.
- Organization / IIoT Solutions: current organization membership, invitations, permissions, and administration.
- Current-organization colleagues may still appear in People, but are labeled separately from network peers.

## Authoritative sources

- `docs/Logs/2026-07-16-005-people-html-mockups.md`
- `design-mockups/people-redesign/index.html`
- `design-mockups/people-redesign/styles.css`

## Files changed

- `p2p-backend-app/app/api/v1/endpoints/auth.py`
- `p2p-frontend-app/src/lib/api/people.ts`
- `p2p-frontend-app/src/pages/Connect.tsx`
- `docs/Logs/2026-07-18-009-people-network-directory-react-port.md`

## Backend capability added

Added authenticated `GET /api/v1/auth/users/directory`.

The endpoint returns active MongoDB profiles across PeerLink, enriches them with PostgreSQL status/IDs, and marks profiles that share the current user's organization. The existing organization-scoped endpoint remains unchanged for Organization management.

## React visual port

- Network Workspace editorial introduction and live directory totals.
- Explicit copy separating People from Organization administration.
- Search across names, roles, companies, industries, locations, and expertise.
- Live expertise, organization, and location filters.
- Dense collaborator rows with profile, organization relationship, manufacturing context, and skills.
- Sticky dark profile preview with collaborator/contact actions.
- Expanded profile-context panel.
- Responsive stacked behavior and shared loading/error/empty states.

## Truthful behavior boundaries

- Collaborate and Contact use available email profile data because no private-messaging backend contract exists.
- People does not expose invitation, role, suspension, removal, or organization-settings controls.
- Directory data remains limited to real registered profiles; no fabricated external people were added.

## Validation

- Backend `py_compile`: passed.
- Frontend `npm run build`: passed.
- `git diff --check`: passed.
- Existing large JavaScript chunk advisory remains non-failing.

## Remaining integration validation

- Rebuild backend and frontend Docker services.
- Authenticate and verify People through BrowserOps.
- Verify Forum, Use Cases, and Organization in the same integrated build.
