# Session Log: 2026-05-10-010 - Company Email Restrictions and Dev Password Reset

> **Date:** 2026-05-10
> **Repo:** `P2P-V2`
> **Branch:** `umair-backend`
> **Scope:** Company-only signup/invite rules, admin/member domain matching, dev password reset email suppression
> **Status:** Implemented

---

## Objective

- Restrict signups to company emails by blocking common personal providers.
- Ensure invited members use the same domain as the admin (match after `@`).
- In dev, do not send real password reset emails; log local reset link instead.
- Improve invite error visibility in the UI.

---

## Files Changed Locally

### 1) `p2p-backend-app/app/core/config.py`
Added new settings for blocked email domains and dev email sending toggle.

**Added**
```py
BLOCKED_EMAIL_DOMAINS: List[str] = [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "protonmail.com",
    "icloud.com",
    "live.com",
    "msn.com"
]
DEV_SEND_EMAILS: bool = False
```

### 2) `p2p-backend-app/app/core/email_domains.py`
Added helpers for domain extraction and blocklist checks.

### 3) `p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py`
Enforced company email rules at signup:
- Blocked personal domains.
- Invited member email domain must match inviter/admin domain.

### 4) `p2p-backend-app/app/api/v1/endpoints/invites.py`
Validated invite target email:
- Blocked personal domains.
- Invited member domain must match admin domain.

### 5) `p2p-backend-app/app/services/password_reset_service.py`
Suppressed real password reset emails in dev unless enabled explicitly.

**Behavior**
- Logs localhost reset link to terminal.
- Skips sending when `ENVIRONMENT != "production"` and `DEV_SEND_EMAILS=false`.

### 6) `p2p-frontend-app/src/pages/UserManagement.tsx`
Invite errors are shown inline under the email field instead of a global toast.

### 7) `README.md`
Documented `BLOCKED_EMAIL_DOMAINS` usage for configuration.

---

## Notes / Configuration

**Recommended dev backend .env**
```env
ENVIRONMENT=development
DEV_SEND_EMAILS=false
BLOCKED_EMAIL_DOMAINS=gmail.com,yahoo.com,hotmail.com,outlook.com,protonmail.com,icloud.com,live.com,msn.com
```

**Enable real emails in dev (if needed)**
```env
DEV_SEND_EMAILS=true
```

---

## Summary

Signups and invitations now enforce company-only domains (with admin/member domain matching) and block common personal providers. Password reset emails are suppressed in development by default, while still logging the localhost reset link. Invite error messaging is now shown directly under the invite email field.
