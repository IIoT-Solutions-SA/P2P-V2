# PeerLink Network Workspace Direction Selection

**Date:** 2026-07-16 AST  
**Status:** Selected direction for further design exploration  
**Scope:** Design decision only; no production React implementation authorized yet

## Decision

Hamza confirmed that the preferred PeerLink frontend direction is the third standalone HTML dashboard concept:

**Concept C — Network Workspace**

Source mockup:

`design-mockups/dashboard-redesign/concept-c-network-workspace.html`

The rendered dashboard was reviewed by Hamza, his colleagues, and his boss. The group agreed that this concept is the preferred direction for continuing the frontend redesign.

## What Was Selected

The selection concerns the overall product and interface direction demonstrated by the Network Workspace dashboard, including:

- A clear workspace-oriented information architecture.
- A permanent desktop navigation rail with distinct product destinations.
- Strong separation between shared member capabilities and administrator-only controls.
- Visible access to questions, use cases, knowledge, people, drafts, and organization tools.
- A dashboard centered on useful actions, knowledge activity, collaborators, contribution progress, and unfinished work.
- A structured layout that gives different roles to actions, activity, network information, and metrics instead of presenting a uniform wall of generic cards.
- A professional manufacturing-network identity suitable for PeerLink.
- Responsive behavior that should preserve important information and actions rather than hiding major sections on mobile.

This decision does not require every word, sample person, statistic, icon, or component in the standalone mockup to be copied literally. Representative content in the mockup must eventually be replaced by real PeerLink data and production behavior.

## Product Requirements Preserved

The selected direction must retain the product decisions established during discovery:

1. **People / Find collaborators** is available to all authenticated members, including administrators.
2. **Manage team** remains a separate administrator-only capability.
3. Member and administrator experiences use the same main product shell, with role-specific tools added where appropriate.
4. The dashboard should help users continue work, discover manufacturing knowledge, and connect with relevant people.
5. Desktop and mobile should preserve the same essential capabilities with responsive reorganization.
6. Loading, empty, error, and retry states must be intentionally designed.
7. Stale, test, contradictory, or fabricated production content must not be carried into the redesign.

## Current Artifacts

### Selected HTML concept

`design-mockups/dashboard-redesign/concept-c-network-workspace.html`

### Generated visual reference

`design-mockups/dashboard-redesign/images/network-workspace.png`

The generated PNG is a visual exploration asset, not a screenshot of the production website and not a source of production truth. The HTML concept is the current interactive reference for the selected direction.

### Related discovery log

`docs/Logs/2026-07-16-001-frontend-redesign-discovery-and-dashboard-mockups.md`

## Immediate Next Design Step

Before changing the production React frontend, create matching authentication mockups for:

- Login
- Sign up / organization registration

The authentication concepts should feel like part of the selected Network Workspace product direction while preserving the actual PeerLink authentication requirements, including corporate identity, organization context, passwords, OTP/MFA, validation, and responsive behavior.

Image-generation may be used first for visual exploration. Any selected authentication design should then be recreated as a responsive HTML mockup before production implementation so layout, fields, states, accessibility, and mobile behavior can be validated.

## Implementation Boundary

At this stage:

- Do not replace the production React dashboard.
- Do not modify live authentication behavior.
- Do not change backend contracts or validation.
- Do not treat generated UI imagery as production-ready specifications.
- Do not remove any required login, signup, organization, invitation, OTP, or security step for visual simplicity.

Production implementation should begin only after the authentication mockups are reviewed and the shared design foundations are explicitly defined.

## Next Approval Point

Hamza will review the login and signup mockups and confirm the preferred authentication direction. After that approval, the team can define the shared design system and plan the page-by-page React implementation.
