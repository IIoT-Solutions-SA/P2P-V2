# 2026-07-18 - PeerLink Production Brand Assets

## Summary
- Created transparent light and dark-sidebar PeerLink combined-logo variants from the official source asset at `p2p-frontend-app/src/assets/LOGIN.png`.
- Preserved the original 1180 x 211 proportions, wording, mark placement, and official blue pixels.
- Converted only the dark navy/gray lettering, dividers, and antialiasing pixels in the dark-sidebar asset to light tones for the authentication sidebar.

## Assets
- `p2p-frontend-app/src/assets/peerlink-logo-light.svg`
- `p2p-frontend-app/src/assets/peerlink-logo-light.png`
- `p2p-frontend-app/src/assets/peerlink-logo-dark-sidebar.svg`
- `p2p-frontend-app/src/assets/peerlink-logo-dark-sidebar.png`

The SVG files wrap the generated transparent PNG derivatives because the official source provided in the repository is a raster PNG rather than vector artwork.

## Usage
- Authentication scaffold now imports `peerlink-logo-dark-sidebar.svg` and places it directly on the dark sidebar gradient.
- The oversized light-background logo band was removed.
- The light variant remains available for white and light surfaces.

## Background Verification
- Light surfaces use `--peer-paper: #f3f0e8`.
- Authentication sidebar uses `linear-gradient(160deg, var(--peer-navy) 0%, #06252d 100%)`.
- `--peer-navy` resolves to `#0b2f39`.
