# Frontend Redesign Discovery and Dashboard Mockups

**Date:** 2026-07-16  
**Scope:** Production frontend review and dashboard design exploration  
**Implementation constraint:** Do not modify the React application during this phase

## Objective

Establish a clearer, more credible visual direction for PeerLink before changing production React components. The current frontend was reviewed in the live authenticated website as both a member and an organization administrator. Three standalone dashboard mockups were then created so the team can compare distinct directions using the same content and data.

## Product decisions established in this phase

1. **Connecting and browsing people is not an administrator-only capability.** Members and administrators should both be able to discover collaborators. Administration adds a separate **Manage team** capability; it does not replace the network experience.
2. **The dashboard should help the user decide what to do next.** It should prioritize open work, useful knowledge, collaborators, and recent activity rather than lead with a generic welcome banner and a wall of colored statistics.
3. **Admin and member experiences should share one product shell.** Role-specific tools should appear as additional capabilities, not as a completely different navigation model.
4. **Desktop and mobile must preserve the same essential information and actions.** Mobile should reorganize content rather than hide major dashboard sections.
5. **Live, trustworthy content is part of the visual design.** Stale events, test payloads, contradictory metrics, and permanent loading screens make even polished components feel unfinished.

## Production frontend findings

### Global navigation and visual system

- The authenticated header does not provide a strong desktop navigation system.
- A mobile-style bottom navigation remains visible on desktop and can cover page content.
- The hamburger menu, bottom navigation, and page-specific actions duplicate one another.
- Many icon-only controls have no accessible label or tooltip.
- The notification indicator appears active but does not open a useful notification surface.
- Unknown routes can render a blank page instead of a designed not-found state.
- Styling relies heavily on repeated white cards, rounded corners, blue/gray blocks, and generic gradients. This makes different pages feel generated from the same component recipe instead of designed around their purpose.

### Dashboard

- The large welcome panel consumes prime space without helping the user complete a task.
- Quick actions are role-dependent in the wrong way: the administrator sees Manage Users where a member sees Connect. Administrators should have both network access and organization management.
- The dashboard repeats card patterns for quick actions, statistics, profile, shortcuts, events, and activities.
- Important mobile content is hidden rather than reorganized.
- The production event card still displays December 15, 2024.
- Draft panels can open after a delay without immediate feedback.
- Activity data contains duplicate/test-like entries and weakens trust.

### Connect and people discovery

- Member Connect currently remains on `Loading members...` indefinitely because the data-loading implementation is disabled while the loading state is permanently true.
- Administrators are redirected from Connect to User Management, preventing them from using the people-discovery experience.
- The future information architecture should contain two distinct destinations:
  - **People / Network:** available to every authenticated user.
  - **Manage team:** administrator-only organization controls.

### User management

- Live organization statistics currently show seven active users, one administrator, and zero pending invitations.
- Search and role filtering work.
- Combining filters with no matching users produces a blank list without a no-results explanation.
- Invite User is functional in structure and all invitations currently create members.
- Edit and delete icons are visible but have no click handlers. They are unfinished placeholders.
- Member and invitation data have no loading skeleton, retry state, or visible request error. Failed requests can misleadingly look like an empty organization.
- Action icons lack accessible names and the invitation overlay is not represented as a semantic dialog.
- Mobile layout is usable but the title/action row, filters, member details, and persistent bottom navigation are cramped.

### Forum

- Production contains security-testing strings, attacker URLs, upload-testing content, random text, and other unsuitable public feed entries.
- The content is escaped, but content hygiene and moderation are visibly poor.
- The post composer exposes a very long category list.
- Filtering provides weak or unclear feedback.
- Search operates only on the posts already loaded by the client.
- Mobile removes useful category and community context instead of adapting it.

### Use-case library and case study

- The library reports 36 use cases and 16 companies while simultaneously displaying zero success stories.
- The left category list represents only a subset of the categories used by the cards.
- Test/script content is visible in production records.
- Library loading can take several seconds with limited feedback.
- Mobile sort labels can collapse into ambiguous repeated labels such as `Most`.
- The detailed case-study page is the strongest current screen on desktop.
- Its mobile hero is critically crowded: title, tags, metrics, and actions overlap or clip.
- A currency symbol/glyph is corrupted and view-count values are inconsistent.

### Use-case submission

- The seven-step form captures substantial and useful information.
- Its desktop stepper clips the first and last labels.
- On mobile the step labels disappear and the edge steps are clipped.
- The form needs clearer progressive disclosure, save feedback, and a less intimidating information hierarchy before implementation work begins.

### Landing page and account surfaces

- The landing-page hero is acceptable on mobile, but map use-case requests fail and live/static metrics disagree.
- Footer links include placeholder behavior and the footer year is stale.
- Profile, password, bookmark, and draft drawers are generally usable but inherit the global navigation and accessibility problems.

## Dashboard mockup requirements

All three concepts intentionally use the same representative content:

- User: Aadil Feroze, Chief Technology Officer, Administrator, Iiotsolutions
- Questions: 0
- Answers: 0
- Saved items: 0
- Reputation: 30
- Use cases shared: 3
- Forum drafts: 1
- Activity level: 15%
- Shared actions: Ask a question, Share a use case, Find collaborators
- Administrator action: Manage team
- Recent knowledge activity and one featured use case
- No stale event card and no fabricated high-growth analytics

## Design directions

### A. Manufacturing Command Center

A serious industrial workspace with a graphite/navy navigation rail, bright working canvas, restrained cobalt and amber accents, compact operational summaries, and a clear list of next actions. It favors speed and information density without turning into an analytics console.

### B. Knowledge Desk

An editorial, human-centered professional network using warm paper tones, ink/navy typography, a desktop top navigation, and feed-led composition. Statistics are integrated into the page rhythm instead of being presented as a generic KPI-card wall.

### C. Network Workspace

A task-oriented collaboration environment with a slim navigation rail, sand/stone canvas, deep teal/navy structure, and a visible collaborator area. Its asymmetric composition gives knowledge, people, and ongoing work different visual roles.

## Files produced

The standalone HTML concepts are stored in:

`design-mockups/dashboard-redesign/`

The React application under `p2p-frontend-app/src/` was not modified.

## Validation performed

- Opened the comparison page and each concept through a local browser preview.
- Reviewed every concept at a 1440 × 1000 desktop viewport.
- Reviewed every concept at a 390 × 844 mobile viewport.
- Confirmed the concepts use semantic landmarks and labeled interactive controls.
- Confirmed UTF-8 punctuation renders correctly.
- Corrected the Knowledge Desk mobile quick actions from a clipped horizontal strip to a two-column grid.
- Corrected the Knowledge Desk mobile navigation button so the menu can be opened and closed.
- Confirmed no files under `p2p-frontend-app/src/` were changed.

## Recommended next step

Review all three dashboard directions at desktop and mobile sizes. Select one direction or specify which elements to combine. Once a direction is approved, define shared foundations—navigation, typography, colors, spacing, buttons, forms, cards, empty/loading/error states, and responsive rules—before implementing page-by-page React changes.
