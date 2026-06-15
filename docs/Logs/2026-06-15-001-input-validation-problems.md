# Input Validation Problems

Summary of observed input validation gaps and recommended backend/frontend hardening for PeerLink/P2P.

## Overview

Recent live application review showed that several user-facing fields still accept meaningless or unsafe-looking input even though some obvious dangerous payloads are already blocked. The remaining issue is not only classic XSS or path traversal; it is also weak semantic validation that allows symbol-heavy, URL-only, or junk content to be saved and displayed as normal user activity.

This can still be reported as lack of input validation because the application accepts values that are not meaningful content for the relevant fields.

## Observed Accepted Inputs

The live activity/feed showed accepted user-generated entries similar to:

```text
<><@#$%^%$#@#$%^%$#@#$%^
!@#$%^&^%$#EWE
https://attacker.com
><@#$%@#$!@#$%
upload malicous file
```

These examples indicate that the current validation blocks some dangerous patterns but does not consistently reject junk input, symbol spam, URL-only text, or low-quality values.

## Current Validation Gap

The backend appears to have some security-oriented validation for high-risk strings such as:

- `<script>`
- `javascript:`
- path traversal patterns
- suspicious upload payloads

However, the application still needs stronger field-level validation for content quality and expected format. A field can be technically non-malicious but still invalid for the application context.

Examples:

- A forum title should not be only symbols.
- A question or reply should contain meaningful words, not random punctuation.
- A title should not be only a URL.
- Tags should not accept arbitrary punctuation.
- Profile names and titles should not be symbol-only.
- Nested use-case objects should not accept raw unvalidated dictionaries.

## Files Requiring Review

```text
p2p-backend-app/app/core/input_validation.py
p2p-backend-app/app/schemas/forum.py
p2p-backend-app/app/api/v1/endpoints/forum.py
p2p-backend-app/app/schemas/usecase.py
p2p-backend-app/app/api/v1/endpoints/usecases.py
p2p-backend-app/app/api/v1/endpoints/dashboard.py
p2p-backend-app/app/api/v1/endpoints/auth.py
p2p-backend-app/app/core/upload_validation.py
p2p-frontend-app/src/components/InteractiveMap.tsx
```

## Recommended Backend Changes

### 1. Central Meaningful Text Validation

Add reusable validation helpers in:

```text
p2p-backend-app/app/core/input_validation.py
```

Recommended checks:

- Trim leading/trailing whitespace.
- Normalize repeated whitespace.
- Require a minimum number of Arabic/English letters or digits.
- Reject text that is only punctuation/symbols.
- Reject values where symbol ratio is too high.
- Reject excessive repeated characters.
- Reject URL-only values for titles/questions/profile fields unless the field explicitly expects a URL.
- Reject raw HTML tags unless the field explicitly supports HTML.
- Keep Arabic and English support.

Suggested baseline rules:

```text
Reject if fewer than 3 Arabic/English alphanumeric characters exist.
Reject if symbols exceed roughly 40-50% of the field value.
Reject if the entire value is a URL and the field is not a URL field.
Reject if the value is mostly repeated characters or repeated punctuation.
Reject raw HTML tags in normal text fields.
```

The exact thresholds can vary by field length. Short fields like names and tags should be stricter; long body fields can tolerate more punctuation but still require meaningful text.

### 2. Forum Question Validation

Review:

```text
p2p-backend-app/app/schemas/forum.py
p2p-backend-app/app/api/v1/endpoints/forum.py
```

Recommended validation:

- `title`
  - 8-150 characters.
  - Must contain meaningful Arabic/English alphanumeric text.
  - Must not be mostly symbols.
  - Must not be URL-only.
  - Must not contain raw HTML tags.
- `content`
  - 20-5000 characters.
  - Must contain meaningful text.
  - Must not be only symbols/repeated punctuation.
  - Must reject dangerous patterns and raw HTML.
- `category`
  - Must be from a backend allowlist.
  - Do not trust frontend dropdown values only.
- `tags`
  - Use a strict pattern: Arabic/English letters, numbers, spaces, and hyphen only.
  - Set max tag length.
  - Set max number of tags.
- `attachments`
  - Do not accept arbitrary dictionaries from the client.
  - Use typed Pydantic models for filename, URL, MIME type, size, and source.

### 3. Forum Reply / Comment Validation

Review:

```text
p2p-backend-app/app/api/v1/endpoints/forum.py
```

Recommended validation:

- `ReplyCreate.content` should use the same meaningful text validator as forum content.
- Reject symbol-only replies.
- Reject URL-only replies unless the feature explicitly allows link-only replies.
- Enforce min/max length.
- Sanitize or reject HTML.

### 4. Dashboard Draft Post Validation

Review:

```text
p2p-backend-app/app/api/v1/endpoints/dashboard.py
```

Current draft-like schemas should not use loose unconstrained strings for fields such as:

```text
title
content
post_type
category
tags
```

Recommended validation:

- Add `Field(min_length=..., max_length=...)` where appropriate.
- Add backend allowlists for `post_type` and `category`.
- Add meaningful-text validation for non-empty draft fields.
- Drafts may allow partial/empty fields, but if a field is provided, it should still reject junk or dangerous content.
- Tags should use the same strict tag validator as forum tags.

### 5. Use Case / Submit Story Validation

Review:

```text
p2p-backend-app/app/schemas/usecase.py
p2p-backend-app/app/api/v1/endpoints/usecases.py
```

Known stronger areas:

- Some length checks already exist.
- Some category/status validation already exists.
- Some fields already call validation helpers.

Remaining gaps to check:

```text
projectTeamInternal: Optional[List[dict]]
projectTeamVendor: Optional[List[dict]]
phases: Optional[List[dict]]
architecture_components: Optional[List[dict]]
images: List[str]
```

Recommended changes:

- Replace raw `dict` fields with typed Pydantic sub-models.
- Validate every nested string field.
- Validate names, roles, company names, phase labels, descriptions, URLs, and image references.
- Add max list lengths.
- Add max string lengths inside each nested object.
- Ensure draft schemas allow partial saves but still reject unsafe/junk values when present.

### 6. Profile Update Validation

Review:

```text
p2p-backend-app/app/api/v1/endpoints/auth.py
```

Fields requiring strong validation include:

```text
firstName
lastName
title
location
expertiseTags
```

Recommended validation:

- Names: letters, Arabic letters, spaces, hyphen, apostrophe only; no symbol-only names.
- Title/location: meaningful text; length limits; no raw HTML; not mostly symbols.
- Expertise tags: strict tag validator, max tag count, max tag length.

### 7. Upload Validation

Review:

```text
p2p-backend-app/app/core/upload_validation.py
p2p-backend-app/app/api/v1/endpoints/media.py
```

Current upload validation appears to be more security-focused than other fields. Keep checking:

- MIME sniffing, not just client-provided Content-Type.
- Extension allowlist.
- File size limits.
- Filename sanitization.
- No executable/script uploads.
- No SVG unless sanitized or explicitly blocked.
- Store files outside executable paths.

The uploaded-file metadata fields should also be validated with the same text validators.

## Recommended Frontend Safety Review

### Leaflet / Interactive Map Popups

Review:

```text
p2p-frontend-app/src/components/InteractiveMap.tsx
```

If user-controlled fields are inserted into Leaflet popup HTML strings or `.setContent(...)`, React escaping does not automatically protect that HTML. Any user-controlled values used in raw popup HTML must be escaped before insertion.

Recommended fix:

- Avoid raw HTML strings when possible.
- If raw HTML is required, escape all user-controlled values before building the string.
- Do not insert untrusted names, descriptions, locations, company fields, or URLs directly into popup HTML.

## Query Parameter Validation

Review list endpoints for query parameters such as:

```text
skip
limit
sort
category
status
search
```

Recommended rules:

- `skip >= 0`
- `limit <= 100`
- `sort` must use an allowlist of known sortable fields.
- `category/status` must use backend allowlists.
- Search string should have max length and reject raw HTML/control characters.

## Test Payloads

The following payloads should be tested against all major text inputs:

```text
<><@#$%^%$#@#$%^%$#@#$%^
!@#$%^&^%$#EWE
https://attacker.com
<script>alert(1)</script>
<img src=x onerror=alert(1)>
javascript:alert(1)
../../etc/passwd
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

Fields/endpoints to test:

- Forum question title.
- Forum question content.
- Forum reply/comment content.
- Dashboard draft title/content/tags.
- Use-case title/subtitle/description/challenge/result fields.
- Use-case nested team/phases/architecture fields.
- Profile first name, last name, title, location, expertise tags.
- Upload filename and upload metadata.

Expected result:

```text
Backend returns 400 or 422.
Invalid content is not saved.
Invalid content does not appear in activity feed.
Frontend shows a clear validation message.
```

## Acceptance Criteria

The issue should be considered fixed only when:

1. Junk strings are rejected by the backend, not only by frontend validation.
2. Symbol-only and mostly-symbol values are rejected in title/name/tag fields.
3. URL-only values are rejected in fields that are not URL fields.
4. Raw HTML tags are rejected or safely escaped in normal text fields.
5. Forum question, forum reply, dashboard draft, use-case, use-case draft, profile, and upload metadata paths all use consistent validators.
6. Nested use-case dictionaries are replaced with typed schemas or equivalent field-by-field validation.
7. Query parameters have numeric caps and allowlists.
8. Frontend raw HTML insertion points escape user-controlled values.
9. Automated or manual tests confirm the listed payloads return 400/422 and are not persisted.

## Short Implementation Direction

Implement this centrally first, then apply it across schemas/endpoints.

Recommended approach:

1. Add reusable validators in `app/core/input_validation.py`.
2. Update Pydantic schemas and endpoint request models to call those validators.
3. Replace raw nested dictionaries with typed models where possible.
4. Add field-specific allowlists for category/status/post type/sort.
5. Add frontend escaping for raw popup HTML.
6. Test all payloads against all affected endpoints.

## Notes

This review focuses on input validation gaps. It does not replace the separate reviews for web server headers, CSP, NGINX version disclosure, MFA, upload security, or dependency vulnerability findings.
