# Story 10: Use Case Submission (End‑to‑End)

## Overview
Implements the end‑to‑end “Submit Use Case” flow so authenticated users can submit complete case studies that immediately appear in the Use Cases list and a detailed view. The solution includes strong client‑side step validation, a server‑side schema, and service logic that links submissions to the author’s organization.

## Implementation Status: ✅ COMPLETED (Initial E2E)

## Acceptance Criteria
- [x] Authenticated user can open `/submit` and complete a multi‑step form
- [x] Required fields enforced per step; can’t proceed with missing/invalid inputs
- [x] Submit posts JSON to `POST /api/v1/use-cases` using the current session
- [x] Backend validates request and persists a `UseCase` document
- [x] Submissions are published immediately and visible in the list (sorted by newest)
- [x] Use Case detail page renders the full submitted content

## Backend Changes

### New Schema (`app/schemas/usecase.py`)
Adds strict Pydantic models to validate request payloads:
- `UseCaseCreate` (top‑level)
- `QuantitativeResult`, `ChallengeSolution`
- Optional structured sections: `TechnicalArchitecture`, `FutureRoadmapItem`, `LessonLearned`

Key validated fields (subset):
- Basic: `title`, `subtitle`, `description`, `category`, `factoryName`, `city`, `latitude`, `longitude`
- Business challenge: `industryContext`, `specificProblems[]`, `financialLoss`
- Solution & implementation: `selectionCriteria[]`, `selectedVendor`, `technologyComponents[]`, `implementationTime`, `totalBudget`, `methodology`
- Results & challenges: `quantitativeResults[]`, `challengesSolutions[]`
- Media: `images[]` (URLs – currently provided by the frontend as placeholders)

### Service (`app/services/usecase_service.py`)
- `UseCaseSubmissionService.create_use_case(db, user_supertokens_id, data)`
  - Resolves session → PG user (by `supertokens_id`) → Mongo user (by email)
  - Auto‑links an `Organization` if the Mongo user is missing `organization_id` (derived from email domain) and persists it
  - Maps request to the `UseCase` document with slugs (`title_slug`, `company_slug`)
  - Populates structured sections (business challenge, solution details, implementation details, results)
  - Sets `published = true` so the case appears immediately in the list

### Endpoint (`app/api/v1/endpoints/usecases.py`)
- `POST /api/v1/use-cases` (session‑required) uses `UseCaseCreate` and the service to persist the document and returns the id
- Existing `GET /api/v1/use-cases` unchanged; it returns only published, non‑detailed items and is consumed by the list page

## Frontend Changes

### Page: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- Multi‑step form with strict zod schema mirroring backend types
- Step gating: clicking Next triggers validation for the current step’s fields (`react-hook-form` + `trigger`) and prevents progress on errors
- Sections covered:
  - Basic info (title, subtitle, summary, category, factory)
  - Business challenge (industry context, specific problems, financial loss)
  - Solution & implementation (selection criteria, selected vendor, vendor process & selection reasons – optional, technology components, duration, total budget, methodology)
  - Results & challenges (quantitative results, challenge cards with description/solution/outcome split)
  - Location & media (city, map pin to set lat/lng, image files – currently converted to placeholder URLs)
- Submission posts to `POST /api/v1/use-cases` with credentials; success shows the confirmation screen
- Added category: “Artificial Intelligence” to the dropdown

### Page: `p2p-frontend-app/src/pages/UseCases.tsx`
- Long description text safely wraps in cards (`word-break: break-word; overflow-wrap: anywhere`)

### Page: `p2p-frontend-app/src/pages/UseCaseDetail.tsx`
- Safe wrapping applied to prevent overlap in long strings across sections (solution overview, vendor evaluation, meta grids)

## Data Model Notes (Mongo)
- Uses existing `UseCase` document with rich sections and indexes
- Submissions are created as a single document and shown as a list projection and a full detail view; no separate “basic vs. detailed” pair is created at submit time

## API Summary (updated)
- `POST /api/v1/use-cases` — Submit a new use case (session required)
- `GET /api/v1/use-cases` — List use cases (published, non‑detailed; filter/sort options)
- `GET /api/v1/use-cases/{company_slug}/{title_slug}` — Detailed view by slugs

## Testing
- Verified client‑side step validation blocks progress when any required field is incomplete
- Verified `POST /api/v1/use-cases` returns 201 and the document is persisted in Mongo
- Verified auto‑linking of `Organization` for legacy users without org links
- Verified new submissions are visible in the Use Cases list (Newest) and open in the detailed route

## Migration/Deployment Notes
- No SQL migration; Mongo collections already include `use_cases`
- Ensure SuperTokens and session middleware are running; the route requires a valid session
- If running seed data, drafts can be published via a small script (`scripts/publish_last_draft.py`)

## Production Readiness – Follow‑ups (Planned)

### 1) Search & Filters (List UX)
- Backend: extend `GET /api/v1/use-cases` with robust search across `title`, `factory_name`, `industry_tags`, `technology_tags`, and category; add pagination
- Frontend: search box debounced, filter chips (category, tags), sort (newest/most viewed/most liked), and client URL state (query params)

### 2) Likes & Bookmarks for Use Cases
- Backend: `POST /api/v1/use-cases/{id}/like` and `POST /api/v1/use-cases/{id}/bookmark` with user‑specific toggles; track `liked_by[]`, `bookmark_count`
- Frontend: buttons on list and detail that reflect current state; optimistic UI followed by server reconciliation

### 3) View Count & Engagement
- Backend: increment `view_count` on `GET /api/v1/use-cases/{company_slug}/{title_slug}` (middleware or service hook)
- Frontend: ensure duplicate increments are minimized (simple debounce or server‑side IP/session window)

### 3.1) Dashboard Activity Integration
- Backend: emit a `UserActivity` entry on successful submission (type: `use_case_submitted`, `target_id`, `target_title`, `target_category`) and recalc user stats; reuse `UserActivityService` pattern from forum posts
- Frontend (Dashboard): fetch recent activities and include “Submitted use case: {title}” with link to the detail route; ensure counters (use_cases_submitted) reflect the latest value

### 4) Media Uploads
- Add `/api/v1/uploads` (pre‑signed URL or direct store) so image `File`s are uploaded and `images[]` in submissions are real URLs

### 5) Authoring Lifecycle
- Draft vs. Publish toggle on submit; default publish ON (current behavior)
- Edit & Delete endpoints (author/admin), with audit and soft delete
- Admin moderation queue (optional) for verifying high‑visibility stories

### 6) Redirect UX after Submit
- After success, return `company_slug` & `title_slug` and auto‑navigate to the detail page with a toast (“Published successfully”)

### 7) Rate Limiting & Abuse Controls
- Basic rate limits on `POST /api/v1/use-cases` and likes/bookmarks endpoints; server‐side validation for field sizes and arrays

These items will be tracked in the next story to complete the submission feature set and platform engagement loop.


