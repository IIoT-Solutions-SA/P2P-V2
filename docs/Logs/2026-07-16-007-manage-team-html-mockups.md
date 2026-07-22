# PeerLink Role-Based Organization HTML Mockup Family

Detailed implementation and revision log for the isolated responsive PeerLink organization mockups completed and revised on 2026-07-16.

## Overview

The original Manage Team mockup family was revised to implement the approved PeerLink organization role model.

The organization experience is now one conceptual route for both normal Members and Administrators. In these mockups, the organization is **IIoT Solutions**, so the sidebar Organization item is labeled **IIoT Solutions** instead of the generic label **Manage team**.

Both roles can open the same organization profile and view:

- Organization identity and profile
- Verified organization information
- Member count and roster
- Administrators and organization contacts
- Basic member details
- Published organization use cases
- Recent organization activity

Administrators see the same shared organization content plus additional organization-administration controls:

- Invitations and pending invitations
- Full invitation flow
- Add/remove/suspend member entry points
- Role-change entry points
- Roles and permissions
- Organization settings
- Administrative member controls
- Export and profile-edit controls

Normal Members receive a clear read-only organization view. Invite, add, remove, suspend, role-change, permission-edit, organization-settings, and destructive controls are absent. If a Member directly attempts to open an administrator-only page, the page renders an access-denied treatment explaining what remains available and how to contact the organization administrator.

The revision remains a standalone static prototype. It does not change production authentication, authorization, APIs, React components, backend code, or data.

## Assigned Scope and Isolation

All revised implementation files remain under:

`/home/hamza-minipc/Documents/P2P-V2/design-mockups/manage-team-redesign/`

The only documentation file revised was:

`/home/hamza-minipc/Documents/P2P-V2/docs/Logs/2026-07-16-007-manage-team-html-mockups.md`

No production React or backend files were edited. A later explicitly approved prototype-wide consistency pass updated organization navigation labels in the dashboard, People, and use-case HTML mockups and extended the shared static prototype router to recognize the company-name label.

## Approved Role Model

### Shared organization route

The role previews use the same organization route and query-based prototype role:

- Administrator: `index.html?role=admin`
- Member: `index.html?role=member`

A **Prototype role** selector in the top bar allows reviewers to switch between Administrator and Member views without opening unrelated designs.

### Member organization view

The Member view is read-only and includes:

- IIoT Solutions organization profile
- Verification, industry, location, domain, and join-date information
- Member count
- Administrator/contact count
- Published use-case count
- Monthly contribution count
- Searchable member roster
- Role and status filters
- Basic member-detail links
- Organization administrator contact information
- Organization use cases
- Recent organization activity

The Member view does not render:

- Invitations navigation
- Permissions navigation
- Organization-settings navigation
- Invite member button
- Organization profile editing
- Pending-invitation and available-seat administration metrics
- Member export
- Member action menus
- Role-management buttons
- Suspend/remove controls
- Permission toggles
- Organization-settings forms
- Administrator console

### Administrator organization view

The Administrator view begins with the same organization information available to Members. It layers administration onto the shared route rather than becoming a separate visual product.

Administrator-only additions include:

- Invitations, Permissions, and Organization settings navigation
- Invite member action
- Organization profile editing
- Pending-invitation and available-seat metrics
- Member export
- Member action menus
- Role/permission access
- Organization administration console
- Invitation management
- Membership status and role controls
- Organization settings

### Access-denied behavior

The following pages are considered administrator-only:

- `invitations.html`
- `invite-member.html`
- `permissions.html`
- `settings.html`

When opened with `?role=member`, the normal administrative page content is replaced with a role-aware access-denied treatment. It confirms that the Member account is active, lists the organization information still available, provides a return action to IIoT Solutions, and offers the organization administrator contact.

## Files Revised and Created

### `index.html`

Rebuilt as the shared organization route.

It now contains:

- Dynamic IIoT Solutions sidebar label
- Shared organization profile
- Verified-organization metadata
- Role-specific context banner
- Shared role selector
- Shared organization metrics
- Searchable/filterable member roster
- Basic member-detail links for both roles
- Administrators and contacts panel
- Organization use cases
- Organization activity
- Administrator-only action console
- Administrator-only quick invitation modal

The Member and Administrator views use the same content structure, visual hierarchy, and shell. Role-specific controls are layered with `data-admin-only` and `member-only` visibility behavior.

### `member-detail.html`

Revised from an administration-only presentation into a shared basic member-detail page.

Members can view:

- Identity
- Position
- Organization membership
- Role and status
- Join date
- Contact information
- Location
- Last-active information
- Verification status
- General activity tab

Administrators additionally see:

- Change-role controls
- Member action menu
- Access tab
- Administrative-log tab
- Account-help control
- Suspend-membership control

### `invitations.html`

Preserved as the Administrator invitation-management page and integrated with role enforcement.

It includes:

- Pending invitation list
- Recipient, role, inviter, sent date, and expiry information
- Representative resend/cancel action surfaces
- Invitation history
- Company-domain protection summary
- Link-validity information
- Entry into the complete invitation flow

Member access renders the shared access-denied treatment instead of this content.

### `invite-member.html`

Preserved as the Administrator invitation flow and integrated with role enforcement.

It includes:

- Company-email recipient
- Optional display name
- Team/function
- Role selection
- Optional message
- Confirmation
- Recipient preview
- Seven-day expiration explanation

Member access renders the access-denied treatment.

### `permissions.html`

Preserved as the Administrator capability matrix and integrated with role enforcement.

It presents organization capabilities for Administrator and Member roles but does not represent production authorization logic. Member direct access renders the access-denied treatment.

### `settings.html`

New Administrator-only organization-settings page containing:

- Organization name
- Industry
- Headquarters
- Organization summary
- Verified email domain
- Default invitation role
- Company-domain invitation requirement
- Administrator join notifications
- Current organization summary

Member direct access renders the access-denied treatment.

### `states.html`

Updated to reflect the approved model.

Representative states include:

- Loading
- No members
- No search results
- No pending invitations
- Member attempt at an Administrator action
- Recoverable service error

The access-denied example now clearly states that Members may view IIoT Solutions while Administrator actions remain restricted.

### `styles.css`

Extended with role-based organization styles:

- Member/Admin visibility behavior
- Prototype role selector
- Role-context banners
- Organization profile hero
- Organization metadata and tags
- Contacts panel
- Shared roster layout
- Organization use-case list
- Organization activity list
- Administrator action console
- Access-denied panel
- Responsive behavior for the new sections

The existing Network Workspace design tokens remain unchanged:

- Paper: `#f3f0e8`
- Surface: `#fbfaf6`
- Ink: `#142d34`
- Navy: `#0b2f39`
- Teal: `#0f5d5b`
- Teal soft: `#dce9e5`
- Blue action/focus accent: `#1769df`
- DM Sans interface typography
- Manrope headings

### `app.js`

Revised into the shared role-aware interaction layer.

It now:

- Reads `?role=admin` or `?role=member`
- Defaults to Administrator for existing prototype links
- Applies role state to the document
- Adds the Prototype role selector
- Dynamically displays IIoT Solutions in organization navigation
- Updates the representative signed-in identity by role
- Propagates role parameters across local organization pages
- Hides all `data-admin-only` controls for Members
- Preserves shared Member and Administrator content
- Replaces administrator-only pages with access-denied content for Members
- Keeps mobile navigation behavior
- Keeps member search and filtering
- Keeps state switching
- Keeps administrator mock form behavior
- Keeps toast and Escape-key interactions

### `README.md`

Rewritten to document:

- The shared organization route
- Administrator and Member preview URLs
- Shared Member-visible organization content
- Administrator-only capabilities
- Access-denied behavior
- Prototype role selector
- `prototype-nav.js` integration

## Sidebar and Prototype Navigation

The sidebar Organization section now uses the actual organization name:

`IIoT Solutions`

It is no longer labeled `Manage team`.

For Members, the Organization section contains only IIoT Solutions.

For Administrators, the section additionally contains:

- Invitations
- Permissions
- Organization settings

Every HTML page in the family includes:

```html
<script src="../prototype-nav.js"></script>
```

The existing shared `prototype-nav.js` file was used without modification. This keeps Dashboard, Forum, People, Use cases, authentication, homepage, and other static prototype destinations connected while preserving explicit role-aware links within this folder.

## Visual Direction

The revision continues to follow the selected Network Workspace dashboard and homepage shell:

- Navy left navigation
- Warm paper background
- Off-white working surfaces
- Teal active-navigation and verified-state accents
- Fine neutral borders
- Restrained shadows
- Geometric PeerLink brand mark
- Compact organization metadata
- Editorial page introductions
- Dense but readable administrative tables
- Responsive top bar and mobile drawer

The Member and Administrator modes deliberately look like the same product and same organization route. The distinction comes from authorization and available actions, not from unrelated visual concepts.

## Responsive Behavior

### Desktop

- Full navigation rail
- Organization name visible in the Organization section
- Role selector in the top bar
- Organization profile spans the working area
- Administrator view supports six summary metrics
- Member view shows four shared metrics
- Roster and organization contact panel display side by side
- Use cases and activity display in a lower grid
- Administrator console displays a four-action grid

### Compact desktop and tablet

- Navigation collapses to the compact icon rail
- Summary metrics reflow
- Roster and contacts stack when width is constrained
- Use cases and activity stack
- Administration console becomes a two-column layout
- Tables retain horizontal overflow to preserve all fields

### Mobile

- Navigation becomes a top brand bar with drawer
- Opening the Member mobile drawer shows IIoT Solutions and does not show Invitations, Permissions, or Organization settings
- Role selector remains accessible in the top bar
- Page actions stack
- Organization profile becomes a single-column card
- Metadata and tags stack
- Summary metrics become two columns
- Roster remains scrollable rather than dropping information
- Contacts, use cases, activity, and Administrator actions stack vertically
- Administrator-only controls remain absent in Member mode

## BrowserOps Evidence and Validation

BrowserOps task:

`20260716-214634-peerlink-role-based-organization-review`

Evidence directory:

`/home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260716-214634-peerlink-role-based-organization-review/`

Key evidence:

- `screenshots/002-admin-organization-desktop.png`
  - Administrator organization view at desktop size
  - Shared organization information plus Administrator controls

- `screenshots/006-member-organization-desktop.png`
  - Member organization view at desktop size
  - Shared organization information with administration controls absent

- `screenshots/007-member-admin-action-access-denied.png`
  - Member direct attempt to open Permissions
  - Role-aware access-denied treatment

- `screenshots/012-final-admin-organization-mobile-390px.png`
  - Final Administrator organization route at 390-pixel mobile width
  - Includes the revised Organization profile route label

- `screenshots/009-member-organization-mobile-390px.png`
  - Member organization route at 390-pixel mobile width

- `screenshots/011-member-mobile-navigation-open.png`
  - Member mobile drawer showing IIoT Solutions without Administrator navigation

Matching rendered text and structured snapshots were stored alongside each screenshot.

### Validation completed

- All seven HTML pages parsed successfully.
- `app.js` passed `node --check`.
- All seven pages returned HTTP 200 from the local review server.
- All local HTML references resolved.
- Every family page includes `../prototype-nav.js`.
- Administrator desktop organization view rendered successfully.
- Member desktop organization view rendered successfully.
- Member rendered interactive-element inspection confirmed Administrator controls were absent.
- Member direct access to Permissions rendered the access-denied treatment.
- Administrator mobile organization view rendered at 390 by 844 pixels.
- Member mobile organization view rendered at 390 by 844 pixels.
- Member mobile navigation was opened and inspected; only IIoT Solutions appeared in the Organization section.
- Member and Administrator views remained the same visual route and shell.
- Whitespace validation completed with `git diff --check`.

## Known Limitations

- These are static HTML prototypes, not production React components.
- Data is representative and hard-coded.
- The prototype role selector is for design review only and is not authentication.
- Query-string role switching is not production authorization.
- Production must enforce every role boundary on the backend as well as in the frontend.
- Search and filters operate only on sample rows.
- Forms do not call APIs.
- Invitation, profile, member-status, role, permission, export, and settings actions are illustrative.
- The member detail tabs demonstrate information architecture rather than complete datasets.
- External Google Fonts and Lucide icons require network access.
- Narrow tables use horizontal scrolling to preserve fields.

## Prototype-Wide Organization Label Consistency Pass

After the role-based organization family was completed, Hamza explicitly approved updating the connected HTML mockups that still displayed the obsolete label **Manage team**.

The consistency pass changed only static prototype navigation/copy:

- Selected Network Workspace dashboard: organization navigation and organization action now display **IIoT Solutions**.
- Alternative dashboard concepts: organization labels/actions now display **IIoT Solutions** for comparison consistency.
- People mockup: organization navigation now displays **IIoT Solutions**, and explanatory copy points to the organization area while retaining Administrator-only controls.
- Use-case library, detail, submission, and states mockups: organization navigation now displays **IIoT Solutions**.
- Shared `prototype-nav.js`: recognizes `iiot solutions`, `organization`, `organization profile`, and `open organization`, while retaining old label aliases for compatibility.
- Manage-team family document metadata and remaining explanatory copy were renamed to the IIoT Solutions organization model.

No visual redesign or production behavior was introduced into those other families; the changes were restricted to organization naming, route recognition, and directly related explanatory wording.

### Consistency-pass BrowserOps evidence

BrowserOps task:

`20260716-215719-peerlink-organization-label-consistency`

Evidence confirmed:

- Selected Network Workspace dashboard renders **IIoT Solutions** in the Organization sidebar and organization action.
- Clicking the company-name navigation successfully routes through `prototype-nav.js` to the IIoT Solutions organization view.
- People renders **IIoT Solutions** in its Organization sidebar and revised explanatory copy.
- Use Cases renders **IIoT Solutions** in its Organization sidebar.

Key screenshots:

- `screenshots/002-dashboard-iiot-solutions-label.png`
- `screenshots/004-routed-organization-view.png`
- `screenshots/006-people-iiot-solutions-label.png`
- `screenshots/008-usecases-iiot-solutions-label.png`

A repository-wide static search confirmed there are no remaining visible `Manage team` or `Manage Team` labels in HTML or JavaScript. The lowercase `manage team` string remains only as a backward-compatible alias inside `prototype-nav.js`.

## Explicit Modification Confirmation

The primary role-based implementation remains under:

`design-mockups/manage-team-redesign/`

The later approved consistency pass additionally touched static HTML labels/copy in:

- `design-mockups/dashboard-redesign/`
- `design-mockups/people-redesign/`
- `design-mockups/usecases-redesign/`
- `design-mockups/prototype-nav.js`

and this implementation log:

`docs/Logs/2026-07-16-007-manage-team-html-mockups.md`

**Production React was not modified.** No file under `p2p-frontend-app/src/` was changed.

**Production backend code was not modified.** No endpoint, service, model, schema, database, or authorization implementation was changed.

**The selected homepage mockup was not modified.** It already used the organization-aware visual direction and required no Manage team label replacement.

**No production application files were modified.** All follow-up changes remained inside static design mockups and the shared static prototype router.
