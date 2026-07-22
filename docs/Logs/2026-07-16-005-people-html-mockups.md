# People HTML Mockups Implementation Log

**Date:** 2026-07-16  
**Work area:** `design-mockups/people-redesign/`  
**Status:** Complete

## Scope

Created a static HTML mockup family for the PeerLink People experience using the selected Network Workspace visual direction from the dashboard redesign and the matching homepage mockup. The work focused only on design mockups and did not change production application code.

The mockup covers:

- Member directory available to both members and administrators.
- Search across people, skills, and companies.
- Expertise, organization, and location filters.
- Organization and location context for both the page and individual people.
- Member profile preview and expanded profile detail treatment.
- Collaborator and contact actions.
- Representative loading, empty, and error states.
- Explicit separation between People and Manage Team.

## Files Created

- `design-mockups/people-redesign/index.html`
  - Main reviewable People mockup page.
  - Includes the directory, filters, profile preview, profile detail, and state examples.
  - Uses Lucide icons from the same CDN pattern as the selected dashboard mockup.

- `design-mockups/people-redesign/styles.css`
  - Local stylesheet for the People mockups.
  - Reuses the selected Network Workspace design tokens and layout language.
  - Contains responsive rules for desktop, tablet rail collapse, and mobile navigation.

## Design Decisions

The People mockups intentionally follow the selected Network Workspace direction rather than introducing a separate visual system.

Key visual decisions:

- Reused the same paper background, navy rail, teal highlights, blue actions, amber warning/admin accents, and compact bordered sections.
- Kept the fixed left navigation rail on desktop with a compact icon rail at medium widths and a top mobile navigation bar at small widths.
- Used the same typography stack: `DM Sans` for body/UI text and `Manrope` for headings.
- Kept cards and panels restrained, square-edged, and operational rather than marketing-oriented.
- Made People a workspace-level item in the main navigation.
- Kept Manage Team in a separate Organization navigation group to reinforce that People is a shared directory, while team administration remains a distinct admin surface.
- Used role pills only as lightweight context, not as team-management controls.

## Responsive Behavior

The mockups include responsive behavior through CSS media queries:

- Desktop:
  - Fixed navy sidebar.
  - Two-column People layout with the directory on the left and sticky profile preview on the right.
  - Expanded profile detail spans the full content grid.

- Medium widths:
  - Sidebar compresses to icon-only navigation.
  - Directory and preview stack into a single column.
  - Filter toolbar wraps to preserve usable input widths.

- Mobile:
  - Sidebar becomes a 66px top navigation bar with a menu toggle.
  - Directory filters stack vertically.
  - Member rows collapse so actions sit below the member details.
  - Profile actions stack into full-width buttons.
  - Profile fact rows switch from two-column labels to single-column layout.

## Interactions And States

The HTML includes lightweight JavaScript for mockup-level interactions:

- Mobile navigation open/close behavior.
- Toast feedback for collaborator, contact, filter, retry, and navigation actions.
- Clickable member rows that visually select a profile preview.
- Search input feedback after entering query text.
- Escape key closes the mobile navigation when open.

Representative states included:

- Loading:
  - Skeleton rows with avatar and line placeholders.

- Empty:
  - No people match the active filters.
  - Includes reset filter action.

- Error:
  - Directory request failure treatment.
  - Includes retry action while preserving filter context.

## Validation Performed

Performed a lightweight HTML parsing check on the new mockup page:

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
class Parser(HTMLParser):
    pass
p = Path('design-mockups/people-redesign/index.html')
Parser().feed(p.read_text())
print('HTML parsed:', p)
PY
```

Result:

```text
HTML parsed: design-mockups/people-redesign/index.html
```

Also checked that the expected People mockup files exist:

```text
design-mockups/people-redesign/index.html
design-mockups/people-redesign/styles.css
```

## Known Limitations

- This is a static HTML mockup, not a production React implementation.
- Filters and member selection are illustrative; they do not perform real data filtering.
- Profile preview content does not dynamically update based on the selected member.
- External font and icon resources require network access when opened in a browser.
- No browser screenshot pass or automated visual regression test was run.
- No backend API integration was added.

## Production And Shared Mockup Confirmation

Production React was not modified.

No files under `p2p-frontend-app/` were edited.

No backend files under `p2p-backend-app/` were edited.

The existing shared dashboard and homepage mockups were not modified:

- `design-mockups/dashboard-redesign/concept-c-network-workspace.html`
- `design-mockups/homepage-redesign/peerlink-homepage-network-workspace.html`

Only new People mockup files were added under:

- `design-mockups/people-redesign/`

