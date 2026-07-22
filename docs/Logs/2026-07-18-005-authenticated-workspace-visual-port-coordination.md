# PeerLink Authenticated Workspace Visual Port Coordination

Date: 2026-07-18 AST  
Coordinator: Nemo  
Project: `/home/hamza-minipc/Documents/P2P-V2`

## Objective

Complete the authenticated React workspace visual migration after the corrected Concept C Dashboard. Port the approved HTML mockups faithfully while preserving live APIs, authentication, permissions, routes, mutations, and payload contracts.

## Product clarification

- **People** is the broader PeerLink collaborator-discovery surface, not merely a duplicate of the current organization roster.
- **Organization / IIoT Solutions** is the current organization workspace: its own members, invitations, permissions, and supported settings.
- Organization members may appear in People as known/internal collaborators, but People must visually and conceptually support broader network discovery.
- Dashboard, Forum, People, Use Cases, and Organization use the shared Network Workspace shell.
- Submit Story remains an action, not a sidebar tab.

## Parallel ownership

| Agent | Ownership | Authoritative mockups | React files | Shared-file restriction |
|---|---|---|---|---|
| Nemo | Forum first, then People | `design-mockups/forum-redesign/`, `design-mockups/people-redesign/` | `src/pages/Forum.tsx`, `src/pages/Connect.tsx`, page-local additions only | Coordinate before modifying shared layout/styles |
| Kyle | Use Cases library and detail | `design-mockups/usecases-redesign/` | `src/pages/UseCases.tsx`, `src/pages/UseCaseDetail.tsx`, page-local additions only | Do not modify Dashboard, Forum, People, Organization, shared layout, or global CSS |
| Void | Organization / IIoT Solutions | `design-mockups/manage-team-redesign/` | `src/pages/Organization.tsx`, page-local additions only | Do not modify Dashboard, Forum, People, Use Cases, shared layout, or global CSS |

## Required workflow for every owner

1. Read the relevant 2026-07-16 design log and all authoritative HTML/CSS/JS mockup files for the assigned feature.
2. Inspect current React behavior and API modules before editing.
3. Port the approved structure and visual hierarchy faithfully; do not produce a generic interpretation.
4. Preserve live backend behavior and truthful capability boundaries.
5. Keep responsive/mobile behavior intentional.
6. Run `npm run build` and `git diff --check`.
7. Add a dedicated implementation log under `docs/Logs/` listing changed files, preserved functionality, validation, and remaining issues.
8. Do not commit, push, deploy, or rebuild Docker. Nemo will integrate and perform BrowserOps acceptance checks.

## Integration sequence

1. Nemo completes and verifies Forum.
2. Nemo reviews Kyle and Void outputs for scope conflicts and functionality.
3. Nemo completes People with the clarified network-vs-organization distinction.
4. Nemo rebuilds the frontend once after integration.
5. Each page is verified through BrowserOps against its authoritative HTML before acceptance.

## Status

- Dashboard: corrected and accepted direction; live in Docker.
- Forum: assigned to Nemo; in progress.
- People: assigned to Nemo after Forum.
- Use Cases: assigned to Kyle in parallel.
- Organization: assigned to Void in parallel.
- Submission workflow: remains for a later pass after these four surfaces.
