# PeerLink Authentication HTML Mockup Family

Responsive, strictly pre-authentication mockups following the selected **Network Workspace** dashboard and homepage direction.

## Open

Start with:

```text
index.html
```

## Screens

| File | Purpose |
|---|---|
| `login.html` | Default sign-in |
| `login-validation.html` | Summary and inline validation errors |
| `login-loading.html` | Credential/organization loading state |
| `signup.html` | Invitation-based member signup |
| `organization-registration.html` | Organization administrator registration |
| `otp-mfa.html` | New-device OTP/MFA verification |
| `otp-mfa-error.html` | Invalid or expired OTP state |
| `forgot-password.html` | Password recovery request |
| `forgot-password-sent.html` | Privacy-safe recovery request confirmation |
| `reset-password.html` | New password and strength requirements |
| `email-verification.html` | Pending work-email verification |
| `auth-success.html` | Verification success boundary |
| `auth-error.html` | Expired/invalid authentication-link error |

## Shared Mockup Assets

- `auth-system.css` — Network Workspace colors, typography, layout, controls and responsive behavior.
- `auth-system.js` — Mockup-only password visibility, OTP input, countdown and password-strength interactions.

## Boundaries

- These files do not call production APIs.
- No authenticated dashboard, organization switcher, member profile, activity feed or workspace data is rendered.
- The revised login/signup images under `../images/` were used only as visual references.
- Production React and shared dashboard/homepage mockups remain unchanged.
