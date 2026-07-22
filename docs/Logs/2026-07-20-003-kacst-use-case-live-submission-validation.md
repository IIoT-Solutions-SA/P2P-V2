# KACST Use Case Live Submission Validation

**Date:** 2026-07-20  
**Status:** Completed locally; not committed or pushed

## Scope

Completed the simplified three-step PeerLink submission workflow as Hamza Feroze using the KACST source use case `AI-Powered_Drone_Arm_Color_Verification_Station.txt` from `/home/hamza-minipc/Documents/Drone Line/source_use_cases/`.

## Submitted Data

- Organization: IIoT Solutions
- Factory/site: KACST Industry 4.0 Capability Center
- City: Riyadh
- Contributor: Hamza Feroze
- Job title: AI Developer
- Title: AI-Powered Drone Arm Color Verification Station
- Category: Quality Control
- Budget: SAR 50,000–250,000; exact amount SAR 150,000
- Added concise problem, technology, outcomes, and challenges from the source document
- Added three real supporting project images from the matching Drone Line picture folder

## Media Upload Issue and Fix

The use case record saved successfully, but the first attachment upload attempted OCI Object Storage in the local development environment and failed because the configured compatibility credentials were not accepted.

Updated `p2p-backend-app/app/api/v1/endpoints/media.py` so development use-case media follows the same safe local-storage pattern already used by development forum attachments:

- Local root: `/app/uploads/usecases`
- Authenticated upload endpoint remains `/api/v1/media/usecase-media`
- Local read endpoint: `/api/v1/media/usecase-files/{usecase_id}/{filename}`
- Production continues to use OCI Object Storage and fails closed if unavailable
- Object IDs and filenames are validated before local reads

After the fix, all three files uploaded successfully and were attached to the saved use case.

## Verification

- Python compilation: passed
- `git diff --check`: passed
- Use case visible as newest library result
- Detail page displays the uploaded hero image
- Detail page reports three attachments
- Detail page identifies Hamza Feroze as the contributor
- Use case ID: `6a5e3282b47cf1157a5333dd`
- Draft ID used during entry: `6a5e31a1b47cf1157a5333dc`

## BrowserOps Evidence

Task: `20260720-173110-peerlink-kacst-filled-submission-screenshots`

Primary screenshots:

1. `screenshots/009-screenshot-1-organization-filled.png`
2. `screenshots/018-screenshot-2a-use-case-top-filled.png`
3. `screenshots/030-screenshot-2b-use-case-lower-filled.png`
4. `screenshots/035-screenshot-3-attachments-review-filled.png`
5. `screenshots/045-corrected-category-library-verification.png`
6. `screenshots/047-corrected-category-detail-verification.png`

The six workflow screenshots were sent to the Agent Chat WhatsApp group with numbered captions. Corrected final library/detail screenshots were then sent after verifying the category as `Quality Control`.

## Generic New-Use-Case Library Fix

After live validation exposed the simplified free-text outcome being forced into the legacy KPI-card layout, `p2p-frontend-app/src/pages/UseCases.tsx` was updated generically for all current and future use cases:

- KPI cards now render only for concise structured metrics containing a numeric value.
- Duplicate generated metrics are removed before rendering.
- Long free-text outcomes no longer become fake KPI values such as `The`.
- Cases without genuine structured metrics omit the KPI block entirely.
- Featured evidence falls back to a concise case summary instead of repeating a full outcome paragraph.
- Library thumbnails use a fixed 104×104 frame so images cannot stretch into narrow vertical strips.
- Existing use cases with genuine metrics such as `32% reduction in energy consumption` retain their KPI cards.

Validation:

- TypeScript/Vite production build: passed
- `git diff --check`: passed
- Local Docker frontend rebuilt and recreated successfully
- BrowserOps confirmed the new KACST card has no fake/duplicated KPI boxes, uses a properly proportioned thumbnail, and shows a concise featured summary
- Existing structured KPI cards remain visible on other cases
- BrowserOps task: `20260720-175023-peerlink-generic-new-usecase-card-fix`
- Screenshot: `screenshots/002-fixed-live-library.png`

## Repository State

No commit or push was performed.
