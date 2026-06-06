# Draft Save 422 Validation Fix

**Date:** 2026-06-06 | **Branch:** `umair-backend`
**Issue:** "Failed to save draft" 422 error on Save Draft click

## What & Why

`mapFormDataToDraft()` sent raw form values — `react-hook-form` initializes fields as `""`, but Pydantic validates `""` against `min_length` and rejects it (unlike `null` which skips validation). Arrays like `["", ""]` had the same issue at item level. Error messages were generic.

## Changes

Modified `p2p-frontend-app/src/pages/SubmitUseCase.tsx`:

1. **`emptyToNull()`** — converts `""`/`undefined` to `null` for all scalar fields
2. **`arrayWithContent()`** — returns `null` if no array item has real content (checks string `.trim().length`, object values)
3. **Better error parsing** — maps FastAPI 422 `detail` array (`e.msg`) into readable text

## Result

Empty/partial drafts save successfully. Arrays with real content preserved. Actionable error messages.

## Commit

Implemented in PR #3 and merged into `hamza-backend`.
