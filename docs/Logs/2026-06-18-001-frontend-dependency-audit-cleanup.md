# Frontend Dependency Audit Cleanup

**Date:** 2026-06-18  
**Scope:** KACST M1 — Outdated and vulnerable front-end libraries  
**Repository:** `/home/hamza-minipc/Documents/P2P-V2`  
**Frontend path:** `p2p-frontend-app`  

## Summary

Cleared the remaining frontend dependency audit issue found during the full PeerLink penetration-test PDF cross-check.

Before this cleanup, `npm audit` showed one low-severity advisory through Vite's `esbuild` dependency:

```text
esbuild allows arbitrary file read when running the development server on Windows
GHSA-g7r4-m6w7-qqqr
severity: low
range: >=0.27.3 <0.28.1
```

The frontend dependency tree was upgraded so the audit now reports zero vulnerabilities.

## Changes Made

Updated frontend build tooling:

| Package | New version range |
|---|---|
| `vite` | `^8.0.16` |
| `@vitejs/plugin-react` | `^6.0.2` |
| `@tailwindcss/vite` | `^4.3.1` |
| `tailwindcss` | `^4.3.1` |

Adjusted `vite.config.ts` for Vite 8 / React plugin 6 compatibility:

- React plugin now returns an array, so the plugin list is flattened.
- Removed the old top-level `esbuild` option that is no longer compatible with Vite 8 typing.
- Changed production minification config to boolean `true` instead of `'esbuild'`.

## Files Changed

```text
p2p-frontend-app/package.json
p2p-frontend-app/package-lock.json
p2p-frontend-app/vite.config.ts
```

## Validation

Installed from lockfile and verified:

```bash
cd /home/hamza-minipc/Documents/P2P-V2/p2p-frontend-app
npm ci --ignore-scripts
npm run build
npm audit --audit-level=low
```

Build result:

```text
vite v8.0.16 building client environment for production...
✓ 1995 modules transformed.
✓ built in 829ms
```

Audit result:

```text
found 0 vulnerabilities
```

## Notes

- Build prints the existing large bundle warning for the main app chunk. This is a performance/code-splitting warning, not a security vulnerability.
- `node_modules` is tracked in this repository, so after validation it was restored from git to avoid committing local dependency tree churn. The intended source changes are only `package.json`, `package-lock.json`, and `vite.config.ts`.
