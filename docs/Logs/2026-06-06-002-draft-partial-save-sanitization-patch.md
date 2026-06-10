# Draft Partial Save Sanitization Patch

**Date:** 2026-06-06
**Branch:** `hamza-backend`
**Related PR:** #3 — `fix: convert empty strings to null in draft save to fix 422 validation error`

## Issue

PR #3 fixed fully empty draft saves by converting empty scalar fields and all-empty arrays to `null` before sending the draft payload.

During review, Nemo found one remaining gap: partial nested draft sections could still trigger FastAPI/Pydantic `422` validation errors. Example: a user could type only the `metric` field in a quantitative result while leaving `baseline`, `current`, and `improvement` empty. The frontend correctly treated that object as having content and sent it, but the backend draft schema reused the stricter final-submit models and rejected incomplete draft objects.

## Changes

1. Added relaxed draft-only schemas in `p2p-backend-app/app/schemas/usecase.py`:
   - `DraftQuantitativeResult`
   - `DraftChallengeSolution`
2. Relaxed draft `min_length` / `min_items` constraints for partial-save fields while preserving maximum lengths and safe-text validation.
3. Kept the stricter final submission schema unchanged.
4. Improved frontend draft scalar sanitization so whitespace-only strings are sent as `null`.
5. Updated the PR #3 log to remove the stale `Pending — not yet committed` note.

## Validation

Planned/ran validation:

```bash
python3 -m compileall p2p-backend-app/app/schemas/usecase.py
node node_modules/typescript/bin/tsc -b --pretty false
```

Backend schema checks should verify:

- raw empty strings still fail under the original strict shape
- PR-style empty fields converted to `null` pass
- partial nested draft objects now pass draft validation

## Notes

This patch only affects draft-save validation. Final publish/submit validation remains strict so incomplete use cases cannot be published accidentally.
