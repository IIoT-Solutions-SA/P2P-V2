# Session Log: 2026-04-27-008 - Local Domain Cutover Prep

> **Date:** 2026-04-27
> **Repo:** `P2P-V2`
> **Branch:** `hamza-backend`
> **Scope:** Local repo-only preparation for future `PeerLink.c4ir.sa` cutover
> **Status:** Local code/config prepared; live instance/runtime/DNS/TLS work intentionally deferred

---

## Objective

Prepare every safe local/tracked repo change now so that once DNS, TLS, and instance-side prerequisites exist, the remaining work is limited to runtime/server cutover and verification.

This session intentionally avoids the parts that cannot safely be completed locally yet:
- nginx dual-host configuration on the OCI instance
- TLS certificate issuance
- instance-only backend `.env` updates
- final live verification against the real hostname

---

## Files Changed Locally

### 1) `p2p-frontend-app/.env.production`
Changed the production frontend URLs from direct OCI IP to the future canonical public hostname.

**Before**
```env
VITE_API_BASE_URL=http://145.241.154.18
VITE_WEBSITE_BASE_URL=http://145.241.154.18
```

**After**
```env
VITE_API_BASE_URL=https://peerlink.c4ir.sa
VITE_WEBSITE_BASE_URL=https://peerlink.c4ir.sa
```

### 2) `p2p-frontend-app/src/config/environment.ts`
Changed the production host detection and fallback URLs from raw OCI IP to the future canonical public hostname.

**Before**
```ts
const isProductionServer = window.location.hostname === '145.241.154.18';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isProductionServer ? 'http://145.241.154.18' : 'http://localhost:8000');

export const WEBSITE_BASE_URL = import.meta.env.VITE_WEBSITE_BASE_URL ||
  (isProductionServer ? 'http://145.241.154.18' : 'http://localhost:5173');
```

**After**
```ts
const isProductionServer = window.location.hostname === 'peerlink.c4ir.sa';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isProductionServer ? 'https://peerlink.c4ir.sa' : 'http://localhost:8000');

export const WEBSITE_BASE_URL = import.meta.env.VITE_WEBSITE_BASE_URL ||
  (isProductionServer ? 'https://peerlink.c4ir.sa' : 'http://localhost:5173');
```

### 3) `docker/docker-compose.yml`
Changed the backend public-domain-related environment values from raw OCI IP to the future canonical public hostname.

**Before**
```yaml
- BACKEND_CORS_ORIGINS=["http://145.241.154.18"]
- API_DOMAIN=http://145.241.154.18
- WEBSITE_DOMAIN=http://145.241.154.18
```

**After**
```yaml
- BACKEND_CORS_ORIGINS=["https://peerlink.c4ir.sa"]
- API_DOMAIN=https://peerlink.c4ir.sa
- WEBSITE_DOMAIN=https://peerlink.c4ir.sa
```

### 4) `p2p-backend-app/app/main.py`
Added `TrustedHostMiddleware` so the backend is ready for the future hostname-based access while still allowing the current direct-IP path and local development.

**Allowed hosts added**
- `localhost`
- `127.0.0.1`
- `145.241.154.18`
- `peerlink.c4ir.sa`
- `p2p.iiotsolutions.sa`

This is intentionally transition-safe.

---

## What Was NOT Changed Here

These parts are still pending because they depend on the live instance, DNS readiness, or certificate issuance:

### Instance/runtime-only items
- `p2p-backend-app/.env` on the OCI instance
- `PRODUCTION_URL=https://peerlink.c4ir.sa`
- any instance-local `.env` or runtime reload steps

### Web server / proxy items
- nginx `server_name` update for both hosts
- canonical redirect from `p2p.iiotsolutions.sa` to `peerlink.c4ir.sa`
- proxy header adjustments for canonical host behavior

### TLS / certificate items
- Let's Encrypt / certbot issuance
- SSL listener and certificate file wiring
- renewal verification

### Final verification items
- external DNS resolution checks
- API via hostname
- frontend bundle inspection after live build
- invite/reset URL checks
- cookie/CORS/websocket checks against the real hostname

---

## Why These Local Changes Were Done Now

The purpose of this prep is to avoid doing code/config edits at the last minute when the DNS side is ready.

Once the DNS and server prerequisites are in place, the remaining work should mainly be:
1. apply instance-only runtime changes
2. configure nginx/TLS
3. verify end-to-end behavior

---

## Important Caution

These local repo changes should **not** be blindly pushed/deployed to the live environment until the DNS/runtime side is ready.

At the time of this log, `peerlink.c4ir.sa` still resolves to the old AWS Bahrain IP instead of the OCI server, so a premature live cutover would break traffic.

---

## Summary

All safe local repo preparation requested for the future domain cutover has now been completed in `P2P-V2`.

Prepared locally:
- frontend production env
- frontend runtime environment detection
- backend domain/CORS settings in compose
- backend trusted host allowlist
- this session log

Still pending later on the live environment:
- instance `.env`
- nginx
- TLS
- DNS-backed live verification
