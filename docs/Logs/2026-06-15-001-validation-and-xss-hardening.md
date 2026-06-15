# Input Validation & XSS Hardening

**Date:** 2026-06-16  
**Scope:** Hardening backend input validation and preventing frontend XSS  
**Repository:** `P2P-V2`  
**Branch:** `umair-backend`  
**Agent:** Antigravity

---

## Summary

Today's session focused on completing a comprehensive security hardening checklist. The goal was to ensure all input endpoints and frontend insertion points safely handle or reject malicious payloads such as XSS tags, junk strings, URLs, and symbol-heavy text.

1. Hardened backend input schemas across Dashboard Drafts, Profile Updates, and Upload validation to aggressively reject junk strings, URL-only values, and symbols.
2. Locked down all query parameters across list endpoints to strictly enforce limits, pagination bounds, and whitelist sorting mechanisms.
3. Updated the frontend Interactive Maps components to properly escape all HTML insertions, specifically neutralizing XSS vulnerabilities within Leaflet popups.

---

## Changes Made

### 1. Backend Input Validation Hardening

- **Dashboard Drafts (`dashboard.py`)**: Modified `DraftCreate` to allow partial or empty fields (preserving the auto-save feature) using `Optional`, while strictly enforcing `max_length`. Added exact allowlists for `post_type` and `category`. Any populated text now strictly passes through `check_safe_text`.
- **Profile Updates (`auth.py`)**: Split field validation to apply a targeted regex constraint on `firstName` and `lastName` (allowing only English letters, Arabic letters, spaces, hyphens, and apostrophes). `title` and `location` enforce minimum meaningful character counts via `check_safe_text`. `expertiseTags` are strictly clamped at a maximum of 10 tags.
- **Upload Validation (`upload_validation.py`)**: Added a critical missing security check that explicitly runs the client-provided `original_filename` metadata through the `check_safe_text` validator, ensuring malicious strings cannot persist in the PostgreSQL media tracking tables.

### 2. Query Parameter Validation

- **Limits and Bounds**: Across both `usecases.py` and `forum.py` list endpoints, explicitly enforced `1 <= limit <= 100` bounds and verified `skip >= 0`. 
- **Sorting & Categories**: Implemented strict backend dictionary allowlists for `sort_by` and `category` parameters. Previously, unrecognized keys would default; they now throw explicit `400 Bad Request` exceptions.
- **Search Query Sanitization**: Validated the `search` query parameter using `check_safe_text(allow_urls=False)`, blocking injection payloads or XSS strings directly from the query URL.

### 3. Frontend XSS Prevention

- **Leaflet Map Popups (`InteractiveMap.tsx`, `UseCasePopup.tsx`)**: Leaflet constructs its map popups using raw `.setContent()` HTML strings, meaning it natively bypasses React's automatic string escaping. 
- Wrapped all user-controlled variables (such as `useCase.image`, `companySlug`, `titleSlug`, and `id`) in a secure `escapeHtml()` helper function prior to HTML injection to ensure malicious payloads cannot break out of attributes like `src="..."`, `href="..."`, and `onclick="..."`.

---

## Files Changed

```text
p2p-backend-app/app/api/v1/endpoints/auth.py
p2p-backend-app/app/api/v1/endpoints/dashboard.py
p2p-backend-app/app/api/v1/endpoints/forum.py
p2p-backend-app/app/api/v1/endpoints/usecases.py
p2p-backend-app/app/core/upload_validation.py
p2p-frontend-app/src/components/InteractiveMap.tsx
p2p-frontend-app/src/components/UseCasePopup.tsx
docs/Logs/2026-06-16-001-validation-and-xss-hardening.md
```

---

## Notes

All modifications specifically targeted payload sanitization without requiring any complex architectural overhauls or database migrations. Automated test payloads simulating XSS, symbolic junk, and broken URLs now consistently return `400` or `422` HTTP errors.
