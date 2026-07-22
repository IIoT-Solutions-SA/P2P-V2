# Simplified Three-Step Use Case Submission Mockup

**Date:** 2026-07-20  
**Status:** Submission and simplified detail HTML prototypes complete; React/backend implementation pending approval  
**Repository:** `/home/hamza-minipc/Documents/P2P-V2`

## Context

Feedback from an actual assisted use-case submission showed that the current seven-step workflow can take approximately 30 minutes and can still leave the contributor uncertain whether the work was saved. Hamza, his boss, and Amro Abouzied agreed that PeerLink should request less information, use broader questions, and reduce the workflow to no more than three pages.

The agreed direction is not one unrestricted narrative field. It is a short three-page workflow with a small number of generally worded questions that contributors can answer freely.

## Agreed Workflow

### Step 1 — Organization Information

PeerLink should prefill known workspace/profile information so the contributor only confirms or corrects it:

- Organization name
- Factory or site name
- City/location
- Submitter name
- Job title
- Contact email

### Step 2 — Use Case Details

The form retains a short use-case title and asks five broad questions:

1. Problem or opportunity to address
2. Technology, equipment, software, or approach used
3. Approximate budget, with ranges plus `Unknown` and `Prefer not to disclose`
4. Outcomes and results
5. Challenges experienced

Problem, technology, and outcomes are proposed as required. Budget and challenges are optional. Detailed architecture, vendor-selection criteria, project phases, multiple mandatory metrics, and long technical-report fields are removed from the contributor workflow.

### Step 3 — Attachments and Submit

The final page provides:

- Images
- Videos
- PDF and Office documents
- CSV files
- Drag-and-drop selection
- File preview/list and removal controls
- Compact submission summary
- Authorization confirmation
- Save draft and submit controls

There is no separate fourth review page.

## Mockup Implementation

The existing submission mockup was replaced with the new interactive design:

`design-mockups/usecases-redesign/submission.html`

The matching published-detail mockup was also updated:

`design-mockups/usecases-redesign/detail.html`

It demonstrates how the simplified submission becomes a clear public use-case page organized around Problem, Technology, Outcomes, Challenges, budget, organization, contributor, and supporting attachments. It intentionally does not invent mandatory percentages, ROI calculations, architecture, project phases, or other information the contributor was not asked to provide.

The prototypes include:

- Three-step clickable navigation
- Completed/current step states
- Prefilled verified organization fields
- Required/optional question labels
- Broad plain-language prompts
- Budget privacy/unknown options
- Drag-and-drop attachment interaction
- Dynamic attachment list and removal
- Dynamic review summary
- Autosave status simulation
- Save confirmation and submit confirmation toasts
- Responsive behavior using the existing Network Workspace visual system

## Validation

- HTML parsed successfully with Python's standard HTML parser.
- All three steps rendered and were inspected using BrowserOps.
- Step rail navigation was verified.
- Organization, use-case question, and attachment/review states rendered correctly.
- The matching simplified Use Case Detail page rendered successfully with all five-answer content, organization metadata, budget range, contributor, review status, and attachment presentation.

BrowserOps evidence task:

`20260720-141556-peerlink-three-step-submission-html-check`

Key evidence:

- `screenshots/002-step-1-organization.png`
- `screenshots/004-step-2-use-case.png`
- `screenshots/008-step-3-attachments-review-final.png`
- `screenshots/013-simplified-use-case-detail-final.png`

## Next Implementation Work

After Hamza approves the HTML direction:

1. Port the approved three-step interface into `p2p-frontend-app/src/pages/SubmitUseCase.tsx`.
2. Simplify the backend create/update schema so removed legacy fields are no longer mandatory.
3. Preserve compatibility when reading existing richly structured use cases.
4. Extend use-case attachments to the approved document formats with secure server-side MIME validation.
5. Create server drafts immediately and autosave changes independently of step validation.
6. Test refresh recovery, failed-submit recovery, duplicate prevention, desktop/mobile layouts, and a complete authenticated submission.

## Source Control

No commit, push, or production deployment was performed. The mockup and this log remain working-tree changes pending Hamza's approval.
