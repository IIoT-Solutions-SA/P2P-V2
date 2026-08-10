# PeerLink Use-Case Submission — Complete Field Inventory

**Date:** 2026-07-16 AST  
**Scope:** Current seven-step **Submit Your Success Story** form in `p2p-frontend-app/src/pages/SubmitUseCase.tsx`, cross-checked against backend schemas, persistence mapping, upload validation, and draft support.

## Purpose

This is the baseline inventory of every user-editable field currently exposed by PeerLink’s use-case submission form. It records the actual UI grouping, required/optional status, repeatable structures, validation limits, payload names, and known frontend/backend mismatches before any requested redesign.

## Source of Truth Reviewed

- `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- `p2p-frontend-app/src/components/ui/FileDropZone.tsx`
- `p2p-backend-app/app/schemas/usecase.py`
- `p2p-backend-app/app/services/usecase_service.py`
- `p2p-backend-app/app/api/v1/endpoints/media.py`
- `p2p-backend-app/app/core/input_validation.py`
- `p2p-backend-app/app/models/mongo_models.py`

## Wizard Structure

| Step | Screen | Required to move forward? |
|---:|---|---|
| 1 | Basic Information | Yes |
| 2 | Business Challenge | Yes |
| 3 | Solution & Implementation | Core fields required; extended subsections optional |
| 4 | Technical Architecture | Entire step optional |
| 5 | Results & Challenges | Quantitative results and challenges required; other subsections optional |
| 6 | Location & Contact | Location required; media/contact/tags effectively optional |
| 7 | Review & Submit | Review screen; no new data fields |

Drafts may be saved partially at any step. Published submissions use stricter validation.

---

## Step 1 — Basic Information

| UI field | Payload key | Required | Current validation / options |
|---|---|---:|---|
| Use Case Title | `title` | Yes | 10–100 chars; at least 2 English/Arabic letters; no URL; no 6+ consecutive digits; max 3 special characters; safe-text checks |
| Subtitle | `subtitle` | Yes | 10–150 chars; no URLs; safe-text checks |
| Category | `category` | Yes | Must be one of the 10 fixed categories below |
| Factory Name | `factoryName` | Yes | 2–80 chars; title-style safety validation |
| Executive Summary | `description` | Yes | Frontend 50–500 chars; backend allows 50–5000; URLs allowed by description validator |

### Category options

1. Quality Control
2. Predictive Maintenance
3. Factory Automation
4. Artificial Intelligence
5. Sustainability
6. Process Optimization
7. Supply Chain
8. Innovation & R&D
9. Training & Safety
10. Energy Efficiency

---

## Step 2 — Business Challenge

| UI field | Payload key | Required | Current validation / behavior |
|---|---|---:|---|
| Industry Context | `industryContext` | Yes | Frontend 50–500 chars; backend allows 50–5000; URLs allowed |
| Specific Problems Addressed | `specificProblems[]` | Yes | Repeatable list; minimum 2, maximum 5; each 10–500 chars |
| Financial Impact | `financialLoss` | Yes | Minimum 5 chars; backend maximum 500; no URLs |

---

## Step 3 — Solution & Implementation

### Solution and vendor fields

| UI field | Payload key | Required | Current validation / behavior |
|---|---|---:|---|
| Selection Criteria | `selectionCriteria[]` | Yes | Repeatable; minimum 2, maximum 5; each 10–500 chars |
| Selected Vendor/Partner | `selectedVendor` | Yes | Minimum 2 chars; backend maximum 120; title-style validation |
| Vendor Evaluation Process | `vendorProcess` | No | Free text; backend maximum 2000; URLs allowed |
| Vendor Selection Reasons | `vendorSelectionReasons[]` | No | Repeatable list; each item backend max 500 |
| Technology Components | `technologyComponents[]` | Yes | Repeatable; minimum 1, maximum 15; each 20–500 chars |

### Implementation core fields

| UI field | Payload key | Required | Current validation / behavior |
|---|---|---:|---|
| Implementation Duration | `implementationTime` | Yes | Minimum 3 chars; backend maximum 120 |
| Total Budget | `totalBudget` | Yes | Minimum 3 chars; backend maximum 120 |
| Implementation Methodology | `methodology` | Yes | Minimum 20 chars; backend maximum 5000; URLs allowed |

### Internal project team — optional repeatable group

Payload: `projectTeamInternal[]`

| Nested field | Key | Validation |
|---|---|---|
| Role | `role` | 2–100 chars |
| Name | `name` | 2–100 chars |
| Title | `title` | 2–100 chars |

### Vendor project team — optional repeatable group

Payload: `projectTeamVendor[]`

| Nested field | Key | Validation |
|---|---|---|
| Role | `role` | 2–100 chars |
| Name | `name` | 2–100 chars |
| Title | `title` | 2–100 chars |

### Implementation phases — optional repeatable group

Payload: `phases[]`

| Nested field | Key | Validation / input style |
|---|---|---|
| Phase Name | `phase` | 2–100 chars |
| Duration | `duration` | 2–100 chars |
| Budget | `budget` | Optional; max 100 chars |
| Objectives | `objectives[]` | Comma-separated UI converted to list; max 10 items; each max 500 |
| Key Activities | `keyActivities[]` | Comma-separated UI converted to list; max 10 items; each max 500 |

---

## Step 4 — Technical Architecture (Entire Step Optional)

Payload object: `technical_architecture`

| UI field | Nested key | Required | Current validation / behavior |
|---|---|---:|---|
| System Overview | `system_overview` | No | Max 5000 chars; URLs allowed |
| Architecture Components | `architecture_components[]` | No | Repeatable compound group |
| Security Measures | `security_measures[]` | No | Repeatable list; each max 500 |
| Scalability Design | `scalability_design[]` | No | Repeatable list; each max 500 |

### Architecture component fields

| Nested field | Key | Validation / input style |
|---|---|---|
| Layer Name | `layer` | 2–100 chars |
| Components | `components[]` | Comma-separated UI converted to list; max 20 items; each max 200 |
| Specifications | `specifications` | Optional; max 1000 chars; URLs allowed |

The frontend only includes `technical_architecture` in the submission payload when at least one architecture value is entered.

---

## Step 5 — Results & Challenges

### Quantitative results — required repeatable group

Payload: `quantitativeResults[]`  
Minimum 2 entries; maximum 4.

| Nested field | Key | Required | Validation |
|---|---|---:|---|
| Metric Name | `metric` | Yes | 5–200 chars |
| Baseline | `baseline` | Yes | 1–200 chars |
| Current | `current` | Yes | 1–200 chars |
| Improvement | `improvement` | Yes | 2–200 chars |

### ROI and qualitative impact

| UI field | Payload key | Required | Validation / behavior |
|---|---|---:|---|
| ROI Percentage | `roiPercentage` | No | Max 100 chars |
| Annual Savings | `annualSavings` | No | Max 100 chars; UI description says “number only,” but validation stores a string |
| Total Investment | `roiTotalInvestment` | No | Max 100 chars |
| 3-Year ROI | `roiThreeYearRoi` | No | Max 100 chars |
| Qualitative Impacts | `qualitativeImpacts[]` | No | Repeatable list; each max 500 |

### Challenges & Solutions — required repeatable group

Payload: `challengesSolutions[]`  
Minimum 1 entry; maximum 4.

| Nested field | Key | Required | Validation |
|---|---|---:|---|
| Challenge Name | `challenge` | Yes | 10–300 chars |
| Challenge Description | `description` | Yes | 20–1000 chars |
| Solution | `solution` | Yes | 20–1000 chars |
| Outcome | `outcome` | Yes | 10–500 chars |

### Lessons Learned — optional repeatable group

Payload: `lessons_learned[]`. An item is submitted only when **Lesson Title** is populated.

| Nested field | Key | Required if item submitted | Validation / options |
|---|---|---:|---|
| Category | `category` | Yes | 2–100 chars; UI options: Technical, Process, People, Budget, Timeline, Vendor |
| Lesson Title | `lesson` | Yes | 5–500 chars |
| Description | `description` | No | Max 1000 chars; URLs allowed |
| Recommendation | `recommendation` | No | Max 1000 chars; URLs allowed |

### Future Roadmap — optional repeatable group

Payload: `future_roadmap[]`. An item is submitted only when **Initiative** is populated.

| Nested field | Key | Required if item submitted | Validation |
|---|---|---:|---|
| Timeline | `timeline` | Yes | 2–100 chars |
| Initiative | `initiative` | Yes | 5–300 chars |
| Description | `description` | No | Max 1000 chars; URLs allowed |
| Expected Benefit | `expected_benefit` | No | Max 500 chars; URLs allowed |

---

## Step 6 — Location, Media, Contact and Tags

### Factory location

| UI field | Payload key | Required | Validation / options |
|---|---|---:|---|
| City | `city` | Yes | Fixed Saudi-city dropdown; backend accepts 2–50 chars |
| Latitude | `latitude` | Yes | Number from -90 to 90; six-decimal input; default 24.7136 |
| Longitude | `longitude` | Yes | Number from -180 to 180; six-decimal input; default 46.6753 |
| Interactive Map Pin | updates latitude/longitude | Yes indirectly | Clicking map sets the same coordinate fields |

### Saudi-city dropdown options

Abha, Al-Bahah, Al-Kharj, Arar, Buraydah, Dammam, Dhahran, Hail, Hofuf, Jeddah, Jizan, Jubail, Khamis Mushait, Khobar, Madinah, Makkah, Najran, Qatif, Riyadh, Sakaka, Tabuk, Taif, Unaizah, Yanbu.

### Media upload

| UI field | Payload/storage | Effective requirement | Current behavior |
|---|---|---:|---|
| Images/Videos | files uploaded to `/api/v1/media/usecase-media`; resulting URLs stored in `images` | Optional in current schema | Drag/drop or picker; multiple files; previews and removal; existing media shown in edit mode |

**Frontend component settings:** up to 10 files, wildcard `image/*` and `video/*`, 50 MB per selected file.  
**Backend accepted MIME types:** JPEG, PNG, WebP, MP4, WebM.  
**Backend size limits:** images 5 MB; videos 50 MB.  
**Published schema URL-list limit:** `images` maximum 5 entries.

### Contact information — optional

| UI field | Payload key | Validation |
|---|---|---|
| Contact Person | `contactPerson` | Max 120 chars; title-style validation |
| Title/Position | `contactTitle` | Max 120 chars; title-style validation |

### Tags — optional repeatable lists

| UI field | Payload key | Validation |
|---|---|---|
| Industry Tags | `industryTags[]` | Max 10 tags; each 2–30 chars; letters/numbers/spaces/hyphens only |
| Technology Tags | `technologyTags[]` | Max 10 tags; each 2–30 chars; letters/numbers/spaces/hyphens only |

---

## Step 7 — Review & Submit

No new editable business fields are introduced. The screen displays a review of the entered values and provides workflow actions such as back, save draft, submit/update, and start a new use case.

---

## Draft and Workflow-Only Data

These are not business-content fields displayed as normal form questions, but they are part of the workflow:

| Field/state | Purpose |
|---|---|
| `draftId` | Identifies a server-side draft for updating/deleting/publishing |
| `currentStep` | Saves wizard progress from 1–7 |
| local-storage form key | Browser autosave under `usecase_form_<id-or-new>` |
| uploaded/new media state | Tracks files before upload |
| existing media state | Preserves/removes existing media during edit |
| submission/edit mode | Selects POST create vs PUT update behavior |

Draft schemas make all content fields optional so incomplete progress can be saved. Final publication revalidates the required fields.

## General Security Validation Applied

Across applicable fields, the frontend and backend reject or constrain:

- Script tags and dangerous HTML/event handlers
- `javascript:` URLs
- Path-traversal/system-file patterns
- Null characters and server-side include patterns
- Excessive repeated characters
- Excessive consecutive special characters
- Excessive consecutive consonants in non-URL fields
- URLs in fields that do not explicitly allow them
- Unsafe tags and invalid categories

## Important Current Inconsistencies to Review Before Changes

1. **Executive Summary and Industry Context limits differ:** frontend caps both at 500; backend permits up to 5000.
2. **Media limits differ across layers:** UI allows 10 files and 50 MB each; backend allows only specific formats, caps images at 5 MB, and the published URL schema caps `images` at 5.
3. **The UI section is titled “Images” but accepts videos too.**
4. **Media is effectively optional**, despite an old field document describing images as required and an error fallback saying “Please upload at least 1 image.” The Zod schema does not require a minimum.
5. **Optional project-team and phase groups initialize with blank rows and are sent without filtering.** Backend nested schemas require minimum lengths when those rows are present, so untouched blank rows can cause final 422 validation errors.
6. **Architecture, lessons, and roadmap are filtered conditionally**, while project teams/phases are not handled with the same filtering strategy.
7. **Annual Savings says “number only” in the UI but is validated and stored as free-form text.**
8. **ROI Percentage is stored both as a top-level field and ROI analysis has separate optional values**, making the ROI model uneven.
9. **Step 6 gates on `images`, but `images` itself is optional**, so this does not make media mandatory.
10. **The existing January 2025 field document is stale** in several limits, especially technology components and media behavior; this inventory reflects the current code as of 2026-07-16.

## Current Field Summary

- 7 wizard steps
- 26 direct top-level content inputs/lists in the final create schema
- 8 optional extended top-level inputs/lists
- 7 repeatable compound structures
- 28 nested compound-item fields across teams, phases, architecture, metrics, challenges, lessons, and roadmap
- 10 fixed categories
- 24 fixed Saudi cities
- Draft saving, edit mode, local autosave, server drafts, media upload, and final publication

This inventory is intended as the before-change baseline. No form functionality was changed while preparing it.
