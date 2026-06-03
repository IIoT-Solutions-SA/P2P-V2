# Backend Input Validation Hardening

**Date:** 2026-06-03
**Scope:** Backend-enforced validation for forum & use case schemas — XSS/injection prevention, length/numeric/list constraints, category allow-listing.
**Repository:** `P2P-V2`
**Branch:** `umair-backend`

---

## Summary

Added centralized backend validation to block scanner/injection payloads and malformed data via direct API calls. Previously, Pydantic schemas accepted arbitrary input — validation only existed on the frontend (Zod). Now 14 dangerous pattern categories, field-length bounds, list limits, lat/lng ranges, and strict category allow-listing are enforced at the Pydantic schema layer before data reaches MongoDB.

---

## Files Changed

### New Files
| File | Lines | Purpose |
|---|---|---|
| `p2p-backend-app/app/core/input_validation.py` | 59 | Shared validation module — `DANGEROUS_PATTERNS` regex list, `check_safe_text()`, `check_safe_tag()`, category allow-list |
| `p2p-backend-app/test_validation.py` | 545 | 109 tests covering all validation paths |

### Modified Files
| File | Δ Lines | Purpose |
|---|---|---|
| `app/schemas/usecase.py` | +263/-132 | Field constraints + validators on all use case schemas |
| `app/schemas/forum.py` | +27 | Length constraints + validators on `ForumPostCreate` |
| `app/api/v1/endpoints/forum.py` | +32 | `ReplyCreate` + `PostUpdate` schemas with validation |
| `app/api/v1/endpoints/usecases.py` | +127 | `UseCaseUpdate` + nested update schemas with optional-field validation |

**Total: ~604 lines added across 6 files**

---

## Validation Coverage

### `check_safe_text()` — 14 Dangerous Patterns Blocked
`<script>`, `javascript:`, `onerror=`/`onload=`/`onclick=`/`onmouseover=`/`onkeydown=`/`onsubmit=`/`onfocus=`/`onblur=`/`onchange=`, `../`, `..\\`, `/etc/passwd`, `oastify.com`, XXE (`<!DOCTYPE`, `<xi:include`), SSI (`<!--#exec cmd=`), LDAP (`objectClass=*`), null bytes.

### `check_safe_tag()` — Tags: 2–30 chars, alphanumeric/hyphens/Arabic

### Forum
| Field | Constraint |
|---|---|
| `title` | 8–150 chars + safe |
| `content` | 20–5000 chars + safe |
| `tags` | max 5, each safe-tag |
| Reply `content` | 2–3000 chars + safe |

### Use Case (`UseCaseCreate` & drafts/updates)
- **11 text fields** — min/max length + safe text
- **3 list fields** — `specificProblems` (2–5), `selectionCriteria` (2–5), `technologyComponents` (1–15); each item length-validated
- **Numeric** — lat ±90, lng ±180
- **Category** — validated against 10 frontend categories
- **Tags** — `industryTags`/`technologyTags`: max 10, each safe-tag
- **Nested models** — `QuantitativeResult` (4 fields), `ChallengeSolution` (4 fields), `TechnicalArchitecture`, `FutureRoadmapItem`, `LessonLearned` — all safe-text validated
- **Drafts/Updates** — all fields optional, same validation when present

---

## Test Results

```
109 tests — 109 passed, 0 failed
```

| Section | Tests | What's Covered |
|---|---|---|
| Dangerous Patterns | 26 | All 14 regex patterns + valid inputs |
| Tags | 5 | Min/max, special chars, valid |
| Forum | 17 | Lengths, XSS, reply, updates |
| Use Case Lengths | 9 | All text field bounds |
| Use Case Lists | 6 | Problem/criteria/component limits |
| Numeric Bounds | 5 | lat/lng ranges |
| Use Case XSS | 8 | XSS across 8 fields |
| Category | 12 | All 10 valid + invalid |
| Nested Models | 4 | QuantitativeResult + ChallengeSolution |
| Drafts | 6 | Empty, partial, XSS, bounds |
| Updates | 6 | XSS, category, bounds, tags |

---

## Key Design Decisions

1. **Centralized `input_validation.py`** — avoids regex duplication across schemas
2. **Schema-layer validation** — Pydantic rejects bad input before services/MongoDB
3. **All 10 frontend categories allowed** — backend `/categories` only had 6
4. **Forum categories unrestricted** — they grow organically; only normalized, not rejected
5. **Optional fields validated when present** — drafts & updates get same scrutiny as creates

---

## Verification

```text
Unit tests:           python test_validation.py         → 109/109 passed
Swagger UI /docs:
  POST forum post with <script> in title                → 422 ✓
  POST use case with short title                        → 422 ✓
  POST use case with invalid category                   → 422 ✓
  POST use case with lat=100                            → 422 ✓
  POST forum post with valid data                       → 200 ✓
```

---

## Git Status

```text
Branch: umair-backend
Uncommitted:
  new:    app/core/input_validation.py
  new:    test_validation.py
  mod:    app/schemas/usecase.py
  mod:    app/schemas/forum.py
  mod:    app/api/v1/endpoints/forum.py
  mod:    app/api/v1/endpoints/usecases.py
```

---

## What Was NOT Changed

- Frontend code — untouched
- Service layer (`usecase_service.py`, `forum_service.py`) — no changes
- Response/read schemas — no validation on outgoing data
- MongoDB models — not modified
- Docker/config — no infrastructure changes
