# Single retained use case and guided simplified submission

**Date:** 2026-07-21 AST  
**Project:** PeerLink / P2P-V2  
**Status:** Implemented and validated locally; not committed or pushed

## Request

Temporarily remove the legacy/seeded use cases from the active MongoDB library, keep only the use case submitted through the React frontend, and add simple guidance to the five-question submission experience.

## Active database cleanup

The active `p2p_sandbox.use_cases` collection contained 35 documents. The following frontend-created case was retained:

- ID: `6a5e3282b47cf1157a5333dd`
- Title: `AI-Powered Drone Arm Color Verification Station`
- Organization: `IIoT Solutions`
- Factory: `KACST Industry 4.0 Capability Center`
- Location: `24.720501, 46.646789`
- Media: 3 existing project images retained

Deleted 34 other use-case documents. A post-operation query confirmed exactly one use case remains. Seed source files were not deleted; this cleanup applies to the active development database and therefore does not destroy the historical seed assets.

No user, organization, forum, profile, draft, or media documents were deleted.

## Removed synthetic result handling

The previous simplified payload created two placeholder quantitative-result rows named `Observed outcome` and `Operational benefit`, using generic `Before` and `After` values. This could make narrative text look like structured KPI data.

Changes:

- New simplified submissions now send an empty `quantitativeResults` list unless genuine structured measurements are implemented later.
- Backend `UseCaseCreate.quantitativeResults` now accepts an empty list.
- The retained KACST case was cleaned to remove the placeholder quantitative-result rows, duplicated outcome text, the synthetic `Component 1` prefix, and generated challenge-response wording.
- The contributor's genuine narrative outcomes remain unchanged, including the measurements already supplied in the submitted source text.
- PeerLink no longer manufactures KPI rows from a free-text outcome answer.

## Simple contributor guidance

Added compact **You could include** guidance blocks to Step 2 without adding more pages or turning the form back into a technical report.

### Problem

- What was happening before?
- Who or what was affected?
- Why did it need to improve?

### Technology and approach

- Equipment or hardware
- Software, platforms, or AI models
- How the parts worked together
- The implementation approach

### Outcomes

- What became faster, safer, cheaper, or more reliable?
- If measured: metric, before value, after value, and unit
- Any savings or operational benefits
- Qualitative improvements or lessons

### Challenges

- What was difficult?
- How was it handled?
- What did the team learn?

The budget question remains a straightforward range selector with an optional exact amount.

## Files changed

- `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- `p2p-backend-app/app/schemas/usecase.py`
- `docs/Logs/2026-07-21-004-single-use-case-guided-submission.md`

## Validation

- MongoDB verification: exactly 1 active use-case document remains.
- Retained use-case ID, organization, location, and all 3 media URLs verified.
- Frontend TypeScript and Vite production build passed.
- Backend schema Python compilation passed.
- Targeted `git diff --check` passed.
- Backend remained healthy and loaded the schema change through development auto-reload.
- Updated production frontend assets copied into the running frontend container.
- BrowserOps rendered library confirmed `1 use cases`, `Page 1 of 1`, and only the KACST drone-arm case.
- BrowserOps rendered Step 2 confirmed all four compact guidance blocks.

## BrowserOps evidence

Task: `20260721-124535-peerlink-single-usecase-guided-submission`

- `screenshots/002-single-usecase-library.png`
- `texts/002-single-usecase-library.txt`
- `screenshots/006-guided-five-questions.png`
- `texts/006-guided-five-questions.txt`

## Source-control status

No commit and no push were performed.
