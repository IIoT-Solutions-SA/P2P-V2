# Production Organization Loading and Real People Cleanup

**Date:** 2026-07-22 AST  
**Status:** Completed and deployed  
**Production:** `https://p2p.iiotsolutions.sa`  
**Commit:** `d831287fe2f07a2139206dff1f8e1594775edadc`

## Reported Problems

1. Opening Organization briefly replaced the entire route content with a loading state, which looked like a blank page transition.
2. The production People directory included 18 generated demonstration identities and two obvious security-test accounts. Production must show real registered people only.

## Organization Route Fix

`p2p-frontend-app/src/pages/Organization.tsx` previously returned early while its organization requests were loading. That removed the route header and all organization context until the requests completed.

The route now renders the organization header immediately and keeps it visible while the data panel loads. Loading and error states appear inside the stable organization shell instead of replacing the whole route.

Validation:

- TypeScript/Vite production build passed.
- `git diff --check` passed.
- Authenticated local BrowserOps rendering showed the complete IIoT Solutions organization route, six organization members, organization profile, roster, member detail, administrators, and knowledge panels.
- BrowserOps task: `20260722-190520-peerlink-organization-loading-shell-local-validation`.

## Production People Cleanup

The 18 identities created by `seed_external_demo_users.py` were removed from production:

- Ahmed Al-Faisal
- Sara Hassan
- Mohammed Rashid
- Fatima Ali
- Khalid Abdul
- Sarah Ahmed
- Mohammed Al-Shahri
- Fatima Al-Otaibi
- Hessa Al-Sabah
- Faisal Al-Ghamdi
- Nouf Al-Mutawa
- Tarek Mansour
- Omar Bakr
- Aisha Al-Jameel
- Sameer Khan
- Rania Al-Abdullah
- Bandar Al-Harbi
- Layla Iskandar

Two obvious security-test accounts were also removed:

- `fahikot893@nuitx.com`
- `salehhamad@gmail.com`

Cleanup covered:

- SuperTokens accounts for all generated demo identities and both test identities.
- PostgreSQL user records.
- MongoDB user profiles.
- Orphaned generated organizations.
- Matching pending invitations, where present.

The active demo-user seeding script was deleted from the repository so it cannot be accidentally rerun in production.

## Remaining Production People

Production now contains ten real profiles across the known real organizations:

### IIoT Solutions

- Aadil Feroze
- Abdulrahman Bajabir
- Amro Abouzied
- Firas Al-Siddiqi
- Hamad Ali
- Hamza Feroze
- Mreefah Al-tukhaim

### KACST

- Saleh Almohaimeed
- Turki Al-Nasser

### Yomnai

- Hamza Feroze

For an IIoT Solutions user, the People page therefore has three real external network profiles: the two KACST profiles and the Yomnai profile. The IIoT Solutions colleagues remain correctly separated into Organization.

## Backups

Fresh backups were created before the production cleanup:

```text
/home/ubuntu/P2P-V2/deploy-backups/20260722-190043-AST/
  mongodb-pre-real-people-only.archive.gz
  postgres-pre-real-people-only.dump
```

## Deployment and Verification

GitHub Actions:

```text
Run: 29936187066
Result: success
URL: https://github.com/IIoT-Solutions-SA/P2P-V2/actions/runs/29936187066
```

Live OCI verification:

- Deployed commit: `d831287f`
- Frontend: running
- Backend: healthy
- SuperTokens: running
- PostgreSQL: healthy
- MongoDB: healthy
- MongoDB users: 10
- PostgreSQL users: 10
- Active use cases: 1

Production public/login BrowserOps evidence was captured under:

```text
20260722-190356-peerlink-production-organization-real-people-fix
```

The production sign-in page rendered normally. An authenticated production click-through could not be completed from the isolated BrowserOps testing profile because it does not possess Hamza's current production password/session; no password or OTP was requested from Hamza. The authenticated organization route itself was validated against the same deployed frontend build on the Mini PC, while production data and service state were verified directly on the OCI VM.
