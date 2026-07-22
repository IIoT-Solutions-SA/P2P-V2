# External People Seed and Acceptance

Date: 2026-07-18 AST  
Owner: Nemo

## Purpose

Validate that the People workspace excludes the six IIoT Solutions organization members while showing registered people from external organizations.

## Seed correction

The existing `seed_db_users.py` retained 18 external demo profiles only as commented data and wipes all user and organization records when executed. It was not safe to run against the integrated environment.

Added an additive, idempotent script:

- `p2p-backend-app/scripts/seed_external_demo_users.py`

The script:

- Preserves all existing IIoT Solutions users, posts, use cases, drafts, activities, and organization data.
- Adds the 18 established external demo profiles through the real custom-signup contract.
- Creates external organizations through the live organization linkage behavior.
- Uses the real invitation/member path when a second user shares an existing organization domain.
- Skips profiles already present on repeated execution.

## Database result

- Total registered profiles: **24**
- IIoT Solutions profiles: **6**
- External profiles: **18**
- Total organizations: **18**
- Gulf Plastics Industries correctly contains:
  - Sara Hassan — Administrator
  - Bandar Al-Harbi — Member
  - Both linked to the same organization ID

## People acceptance result

Logged in as `hamza@iiotsolutions.sa` (Member):

- People reports **18 people to connect with**.
- The six IIoT Solutions members remain excluded and are reported separately.
- All 18 external seeded profiles render as Network peers.
- Organization and location filter options derive from external profiles only.
- Search for `Gulf Plastics` correctly returns Sara Hassan and Bandar Al-Harbi.
- Corrected profile selection so filtering cannot leave a hidden, nonmatching profile in the preview.
- Organization administration remains under the IIoT Solutions workspace.

## Validation

- Frontend production build passed.
- `git diff --check` passed.
- Frontend rebuilt and running.
- BrowserOps final page inspection completed in about 0.21 seconds.

## BrowserOps evidence

Task: `20260718-160853-peerlink-people-external-seed-final`

- Full 18-person directory: `screenshots/002-all-18-external-users-final.png`

Filter evidence from the preceding integrated task:

Task: `20260718-160745-peerlink-people-18-external-users`

- Gulf Plastics search returning exactly two external people: `screenshots/005-gulf-plastics-two-external-people.png`

No commit, push, or production deployment performed.
