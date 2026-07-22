# Use-case location picker and organization brand casing

**Date:** 2026-07-20  
**Status:** Implemented and validated locally; uncommitted and unpushed

## Request

Make every future use-case submission mappable from the homepage by exposing location selection in the simplified workflow, and preserve exact organization brand casing (for example, `IIoT Solutions`) instead of recreating display names from lowercase slugs or email domains.

## Changes

### Submission location

- Reused and enhanced `src/components/LocationPicker.tsx`.
- Added Saudi Arabia-restricted OpenStreetMap/Nominatim location search with selectable results.
- Preserved map click and draggable-marker positioning.
- Added clear instructions and loading/error/empty-result states.
- Initially added the picker to submission step 1, then moved the exact-location experience to step 3 after UX review.
- Step 1 retains the city field; step 3 is now **Location & files**, followed by review and submit.
- Added editable latitude and longitude inputs for manual coordinate entry.
- Added finite-number validation at final submission.
- City selection seeds sensible default coordinates, while an exact searched/dragged/manual location is preserved across draft reloads instead of being overwritten by the city default.

### Canonical organization display names

- Added `organization_name` to the MongoDB `UseCase` model as canonical display text.
- Use-case creation now snapshots the exact organization name while keeping lowercase slugs only as route identifiers.
- Organization creation now prefers the exact company name entered during signup instead of title-casing the email domain.
- Legacy use-case organization creation now prefers the user profile's exact `company` value.
- User-profile fallback organization rendering now prefers the exact Mongo profile company value.
- Use-case detail rendering now prefers `organization_name` and backend organization display fields before any last-resort slug reconstruction.

## Local data correction

- Corrected existing organization records from stored user/company names where available.
- Backfilled `organization_name` for existing use cases through their submitter's organization.
- Verified `iiotsolutions.sa` now stores `IIoT Solutions`.
- Updated the submitted KACST use case (`6a5e3282b47cf1157a5333dd`) to the selected KACST coordinates:
  - Latitude: `24.720501`
  - Longitude: `46.646789`

## Validation

- `npm run build`: passed.
- Python compilation for modified backend modules: passed.
- Docker frontend image rebuilt and loaded successfully.
- Backend and frontend containers remained healthy/running.
- BrowserOps evidence task: `20260720-183300-peerlink-map-picker-organization-casing-fix`.
- Confirmed in rendered UI:
  - Step 1 displays `IIoT Solutions` exactly and remains compact without the map.
  - Step 3 displays the location picker before supporting files and final review.
  - Location search returns KACST results.
  - Selecting KACST updates the map marker and coordinates to `24.720501, 46.646789`.
  - Exact coordinates persist after reloading a saved local draft.
- Final relocation evidence task: `20260720-230723-peerlink-map-moved-to-final-step`.
  - Homepage Saudi map marker count increased after the submitted use case received its location.
  - Submitted use-case detail displays `IIoT Solutions` in the header, organization card, project information, and contributor section.

## Files changed for this fix

- `p2p-frontend-app/src/components/LocationPicker.tsx`
- `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- `p2p-frontend-app/src/pages/UseCaseDetail.tsx`
- `p2p-backend-app/app/models/mongo_models.py`
- `p2p-backend-app/app/services/usecase_service.py`
- `p2p-backend-app/app/services/database_service.py`
- `p2p-backend-app/app/api/v1/endpoints/auth.py`

## Notes

- Display names are now treated as canonical user/organization data; slugs remain lowercase URL identifiers only.
- No commit or push was performed.
