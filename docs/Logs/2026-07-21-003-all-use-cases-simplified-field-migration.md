# All use cases simplified-field migration

**Date:** 2026-07-21  
**Status:** Applied locally and validated; uncommitted and unpushed

## Request

Convert all existing PeerLink use cases to the new easier submission fields, either by editing them or deleting and reseeding them.

## Decision

Used a non-destructive in-place migration rather than deleting and reseeding. This preserved:

- MongoDB document IDs
- route slugs and existing links
- submitter ownership
- images and supporting media
- views, likes, bookmarks, and other interactions
- publication state and timestamps
- legacy rich detail sections for backward compatibility

## Canonical simplified fields

Added first-class fields to every use case:

1. `problem`
2. `technology`
3. `budget`
4. `outcomes`
5. `challenges`

The migration derives these fields only from information already stored in each use case. It does not invent claims, results, budgets, or technologies.

## Application changes

- Added canonical simplified fields to the MongoDB `UseCase` model.
- Added optional simplified fields to the create schema.
- New three-step submissions now send and store the five answers directly.
- Use-case detail pages prefer canonical simplified fields and retain legacy fallbacks.
- Edit mode restores canonical simplified answers directly.
- Added an idempotent migration script with preview and apply modes.
- Updated all use-case seed JSON files with the simplified fields.
- Updated the root and per-user seed scripts to persist simplified fields during future reseeding.

## Migration result

- MongoDB use cases processed: **35**
- MongoDB use cases changed: **35**
- Use cases with all five canonical fields populated: **35**
- Existing use cases deleted: **0**
- Second preview after migration: **0 changes**, confirming idempotency

Seed JSON updated:

- `use-cases.json`: 15 cases
- `scripts/usecases/aadil_usecases.json`: 3 cases
- `scripts/usecases/abdulrahman_usecases.json`: 3 cases
- `scripts/usecases/amro_usecases.json`: 3 cases
- `scripts/usecases/firas_usecases.json`: 3 cases
- `scripts/usecases/hamad_usecases.json`: 3 cases
- `scripts/usecases/hamza_usecases.json`: 4 cases

## Validation

- Frontend production build passed.
- Modified backend and migration/seed Python modules compiled successfully.
- `git diff --check` passed for the targeted files.
- Backend remained healthy.
- Live MongoDB verification confirmed all 35 documents contain all five fields.
- BrowserOps validated a previously legacy use case using the simplified presentation:
  - `AI Quality Inspection System`
  - BrowserOps task: `20260721-123118-peerlink-all-usecases-simplified-migration`
  - Screenshot: `screenshots/002-legacy-case-now-simplified.png`

## Main files changed

- `p2p-backend-app/app/models/mongo_models.py`
- `p2p-backend-app/app/schemas/usecase.py`
- `p2p-backend-app/app/services/usecase_service.py`
- `p2p-backend-app/scripts/migrate_usecases_to_simplified_fields.py`
- `p2p-backend-app/scripts/seed_usecases.py`
- `p2p-backend-app/scripts/usecases/seed_*.py`
- `p2p-backend-app/use-cases.json`
- `p2p-backend-app/scripts/usecases/*_usecases.json`
- `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- `p2p-frontend-app/src/pages/UseCaseDetail.tsx`

## Notes

- Future submissions store simple answers directly rather than relying only on duplicated legacy placeholders.
- Legacy sections remain available so no existing data is lost.
- No commit or push was performed.
