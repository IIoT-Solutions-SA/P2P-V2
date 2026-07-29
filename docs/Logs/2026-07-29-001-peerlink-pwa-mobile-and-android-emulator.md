# PeerLink PWA, Mobile Layout, and Android Emulator Readiness

**Date:** 2026-07-29 AST

**Project:** `/home/hamza-minipc/Documents/P2P-V2`

**Branch:** `hamza-backend`

## Objective

Convert the existing PeerLink React frontend into an installable Progressive Web App, harden the authenticated workspace for a proper phone-style experience, and reproduce the proven MaintOptix Pixel 7 emulator workflow from Hamza's personal Windows laptop while PeerLink continues running on the personal Mini PC.

## PWA implementation

Added:

- `p2p-frontend-app/public/manifest.webmanifest`
- `p2p-frontend-app/public/sw.js`
- official-brand-derived 192px, 512px, and maskable launcher icons under `p2p-frontend-app/public/icons/`
- manifest, mobile theme, Apple mobile-app metadata, and safe viewport handling in `index.html`
- service-worker registration in `src/main.tsx`

The service worker provides:

- cached application shell and launcher assets;
- network-first page navigation with cached-shell fallback;
- runtime caching for same-origin static resources;
- deliberate exclusion of `/api/` requests so PeerLink never pretends that uncached authenticated writes succeeded offline.

Authentication, current discussions, use cases, organization data, uploads, and write operations still require the backend.

## Phone application layout

The existing responsive workspace already contained a mobile navigation drawer. This pass validated and hardened it:

- phone top bar with page title, menu, search, and notifications;
- full-height left drawer with PeerLink branding;
- Workspace links for Dashboard, Forum, People, and Use Cases;
- separate Organization navigation;
- account and logout actions at the bottom;
- automatic drawer close after navigation;
- correct safe-area padding for Android/iOS status and navigation areas;
- 44px phone menu target;
- 16px mobile form controls to prevent browser zoom;
- `100dvh` app-shell sizing and horizontal overscroll prevention;
- corrected tablet behavior so the hamburger is not shown when the compact sidebar is already active;
- replaced the Use Cases horizontal sort strip with full-width stacked phone controls.

## Android emulator launcher

Added:

- `scripts/start_peerlink_android_demo.cmd`
- `scripts/start_peerlink_android_demo.ps1`

Copied the launchers to Hamza's personal laptop:

```text
C:\Users\hamza\Documents\PeerLinkDemo\start_peerlink_android_demo.cmd
C:\Users\hamza\Documents\PeerLinkDemo\start_peerlink_android_demo.ps1
```

The launcher:

1. verifies the laptop Android SDK and ADB;
2. starts an SSH tunnel from laptop port `5173` to Mini PC PeerLink port `5173`;
3. boots the `Pixel_7` AVD;
4. waits for Android startup;
5. applies `adb reverse tcp:5173 tcp:5173`;
6. opens `http://127.0.0.1:5173` in Android Chrome.

The emulator origin deliberately uses port `5173`, which is already authorized by PeerLink's local authentication CORS policy. An initial port `5183` launcher caused SuperTokens sign-in to fail with `Failed to fetch` because that origin was not authorized.

Localhost is required because service workers and installable PWAs need a trustworthy origin. Android emulator localhost maps to laptop localhost through ADB, and laptop localhost maps to Mini PC localhost through SSH.

## Validation

### Build and application

- TypeScript/Vite production build: passed.
- Manifest JSON parse: passed.
- Service-worker JavaScript syntax: passed.
- Local frontend container received the rebuilt assets.
- Manifest endpoint: HTTP 200.
- Service-worker endpoint: HTTP 200.
- 512px icon endpoint: HTTP 200.
- Chrome `Page.getAppManifest`: zero manifest errors.
- Service-worker registration: present.
- Active service-worker controller: present.

### BrowserOps phone validation

Task:

```text
20260729-110744-peerlink-pwa-mobile-baseline
```

Validated at a Pixel-class `412 × 915` viewport:

- Dashboard phone layout;
- complete left navigation drawer;
- Forum phone layout and filters;
- People directory phone layout;
- Use Cases phone layout and final stacked sort controls;
- zero horizontal document overflow on validated pages.

Key BrowserOps screenshots:

- `screenshots/003-mobile-pwa-dashboard.png`
- `screenshots/005-mobile-navigation-drawer.png`
- `screenshots/007-mobile-forum.png`
- `screenshots/013-mobile-people.png`
- `screenshots/016-final-mobile-use-cases.png`

### Real Windows Android emulator validation

The launcher was executed against Hamza's personal laptop and successfully reported:

```text
PeerLink opened in the Android emulator: http://127.0.0.1:5173
```

Verified:

- laptop Android SDK available;
- `Pixel_7` AVD available;
- emulator boot completed;
- ADB mapping `tcp:5183 tcp:5183` active;
- Android Chrome was the foreground application;
- PeerLink rendered through the Mini PC tunnel at the emulator-localhost URL.

Real ADB screenshot:

```text
docs/Logs/evidence/2026-07-29-peerlink-pixel7-emulator.png
```

## Current deployment boundary

The new PWA/mobile build is loaded in the Mini PC's local PeerLink frontend container for testing. It has not yet been committed, pushed, or deployed to the OCI production site in this work session.

## Demo instructions

On Hamza's personal laptop, double-click:

```text
C:\Users\hamza\Documents\PeerLinkDemo\start_peerlink_android_demo.cmd
```

Then in Android Chrome:

1. Open the three-dot menu.
2. Select **Install app** or **Add to Home screen**.
3. Confirm installation.
4. Launch PeerLink from the Android home screen for standalone app mode.
