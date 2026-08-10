# PeerLink organization mockup family

Standalone responsive HTML mockups for the shared **IIoT Solutions** organization route, following the selected Network Workspace dashboard and homepage direction.

## Approved role model

Both Members and Administrators open the same conceptual organization route:

- Administrator preview: `index.html?role=admin`
- Member preview: `index.html?role=member`

Both roles can view the organization profile, member count and roster, administrators/contacts, organization use cases and activity, and basic member details.

Administrators additionally see invitations, add/remove/suspend and role-change entry points, role/permission management, exports, and organization settings. These controls are absent from the normal Member view. Direct Member navigation to an administrator-only page renders an access-denied treatment rather than exposing the controls.

Use the **Prototype role** selector in the top bar to compare the two roles.

## Files

- `index.html` — shared role-based organization profile, roster, contacts, use cases and activity
- `member-detail.html` — shared basic member detail with administrator-only actions layered onto the same page
- `invitations.html` — administrator-only pending invitations and history
- `invite-member.html` — administrator-only invitation flow
- `permissions.html` — administrator-only role/capability matrix
- `settings.html` — administrator-only organization settings
- `states.html` — loading, empty, access-denied and error states
- `styles.css` / `app.js` — isolated shared visual, responsive, role and interaction behavior

Every HTML page includes `../prototype-nav.js` so the family remains connected to the wider static PeerLink prototype.

This family does not modify production React, backend code, or any other mockup family.
