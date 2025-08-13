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
- Added scroll-to-top behavior when use case data loads to ensure users start at the top of the page

### Component: `p2p-frontend-app/src/components/ScrollToTop.tsx`
- Global scroll-to-top component that automatically scrolls to top on any route change
- Integrated into App.tsx to provide consistent navigation behavior across all pages

### Navigation UX Improvements
- Fixed issue where clicking on use cases would navigate to middle/bottom of detail page
- Implemented dual scroll-to-top mechanism: global route-based + specific use case load-based
- Ensures users always start at the top when viewing use case details

## Data Model Notes (Mongo)
- Uses existing `UseCase` document with rich sections and indexes
- Submissions are created as a single document and shown as a list projection and a full detail view; no separate "basic vs. detailed" pair is created at submit time
- **Unified Model**: All use cases (seeded and user-submitted) now use the same complete data structure with full detailed fields
- **Realistic Metrics**: All engagement metrics (views, likes, bookmarks) start at 0 and increment only through actual user interactions

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

## Production Readiness – Follow‑ups (Implemented in this sprint)

### A) Likes, Bookmarks and Views for Use Cases — DONE

Backend
- Model: extended `UseCase` (Mongo) with `liked_by: List[str]` and existing counters (`view_count`, `like_count`, `bookmark_count`).
- Seeding: All use cases now start with realistic counts (0 views, 0 likes, 0 bookmarks) instead of random values
- Endpoints (FastAPI, `app/api/v1/endpoints/usecases.py`):
  - `GET /api/v1/use-cases/{company_slug}/{title_slug}` increments `view_count` with a 30‑minute per‑user dedupe using `UserActivity` entries of type `view` (prevents dev StrictMode double bumps).
  - `POST /api/v1/use-cases/{company_slug}/{title_slug}/like` toggles like for the session user, maintains `liked_by`, and updates `like_count`. Activity logged via `UserActivityService`.
  - `POST /api/v1/use-cases/{company_slug}/{title_slug}/bookmark` toggles bookmark for the session user, persists a `UserBookmark`, and updates `bookmark_count`. Activity + stats handled via `UserActivityService.add_bookmark`.
  - `GET /api/v1/use-cases/bookmarks` returns a list of saved use cases (id, title, slugs, counts, created_at) for the current user.

Frontend
- List page `p2p-frontend-app/src/pages/UseCases.tsx`:
  - Card is only clickable on the header/content area; the bottom action row no longer navigates.
  - Left cluster shows solid black counters (views, like, save). Like/Save are buttons that call the new endpoints, update counts in place, and visually highlight when active (blue with filled icon). Buttons use `stopPropagation()`.
  - Bookmarked/liked state is hydrated once on mount using `GET /api/v1/use-cases/bookmarks`.

### B) Forum Saved Posts — DONE

Backend
- View tracking: Forum post views are now deduplicated per user using `UserActivity` records; users who reply to a post are automatically considered to have viewed it
- Seeding: Forum posts start with realistic view counts based on actual user activities instead of random values
- Endpoints (FastAPI, `app/api/v1/endpoints/forum.py`):
  - `GET /api/v1/forum/bookmarks` returns bookmarked forum posts for the current user.
  - `POST /api/v1/forum/posts/{post_id}/bookmark` toggles bookmark via `UserActivityService.add_bookmark(...)` and recalculates `UserStats` (also on unbookmark) so dashboard totals stay in sync.

Frontend
- `p2p-frontend-app/src/pages/Forum.tsx`:
  - Moved replies/views/likes to the left in solid black; like button fills blue when active.
  - Added Save button beside author on list cards and in detail header; button highlights when saved and toggles via the new bookmark endpoint.

### C) Dashboard Saved Items Separation — DONE

- Sidebar quick‑access now shows two distinct counters:
  - “Saved Posts” → `GET /api/v1/forum/bookmarks`
  - “Saved Use Cases” → `GET /api/v1/use-cases/bookmarks`
- Clicking either opens the bookmarks modal filtered to that type with a matching title. Counts are preloaded on mount and refreshed after opening each modal.
- Refactored `Dashboard.tsx` to use stable loader functions (`loadDashboard`, `preloadBookmarkCounts`) to avoid HMR edge cases and to fix a duplicate state bug.

---

## Notes
The above changes finalize Story 10 and the associated engagement features delivered in this sprint.


