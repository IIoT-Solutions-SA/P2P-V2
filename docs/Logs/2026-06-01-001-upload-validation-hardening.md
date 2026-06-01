# Upload Validation Hardening

**Date:** 2026-06-01  
**Scope:** KACST penetration test issue 03 — Unrestricted File Upload Vulnerability  
**Repository:** `P2P-V2`  
**Branch:** `hamza-backend`  
**Commit:** `22befe9 fix: harden media upload validation`  
**Live environment:** OCI production instance `145.241.154.18`, app path `/home/ubuntu/P2P-V2`  
**Public URL:** `https://p2p.iiotsolutions.sa`

---

## Summary

Implemented and deployed backend upload hardening for the P2P media upload endpoints. The fix prevents content-type spoofing, renamed dangerous files, extension/content mismatches, and unauthorized uploads to another user's forum post or use case.

This change was made in the app repo on `hamza-backend`, committed, pushed, deployed to OCI, and verified live through BrowserOps.

---

## Upload Routes Covered

| Endpoint | Purpose | Coverage |
|---|---|---|
| `POST /api/v1/media/profile-picture` | Profile picture upload | Content validation and safe extension enforcement |
| `POST /api/v1/media/forum-attachment` | Forum post attachments | Content validation, safe extension enforcement, owner/admin authorization |
| `POST /api/v1/media/usecase-media` | Use case media uploads | Content validation, safe extension enforcement, owner/admin authorization |

---

## Files Changed

```text
p2p-backend-app/app/core/upload_validation.py
p2p-backend-app/app/api/v1/endpoints/media.py
p2p-backend-app/app/services/s3_service.py
```

Key implementation details:

- Added `validate_upload_file` shared backend validator.
- Added `ValidatedUpload` dataclass.
- Added magic-byte/signature checks for allowed media types.
- Stopped trusting only browser-provided `file.content_type`.
- Rejected empty uploads and oversize uploads.
- Rejected MIME/content mismatches.
- Rejected extension/content mismatches such as JPEG bytes uploaded with a `.php` filename.
- Forced object-storage extension from verified MIME type using `SAFE_CONTENT_TYPE_EXTENSIONS`.
- Added ownership checks before upload for forum and use case media.

Allowed types:

| Upload flow | Allowed MIME types |
|---|---|
| Profile pictures | `image/jpeg`, `image/png`, `image/webp` |
| Forum attachments | `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `video/mp4`, `video/webm` |
| Use case media | `image/jpeg`, `image/png`, `image/webp`, `video/mp4`, `video/webm` |

---

## Local Validation Smoke Test

The validator was smoke-tested before deployment:

```text
Valid JPEG accepted: valid: image/jpeg jpg profile.jpg
Fake PHP as JPEG blocked: Invalid test file type
JPEG bytes with .php extension blocked: Uploaded file extension does not match its content
JPEG bytes declared as PNG blocked: Uploaded file content does not match its declared file type
```

---

## Live Deployment Verification

Live OCI repo state:

```text
/home/ubuntu/P2P-V2
branch: hamza-backend
HEAD: 22befe9d
```

Confirmed live:

- `p2p-backend-app/app/core/upload_validation.py` exists.
- `media.py` imports and uses `validate_upload_file`.
- `s3_service.py` has `SAFE_CONTENT_TYPE_EXTENSIONS`.
- Backend container is healthy.

---

## Live BrowserOps Tests

### Profile Picture Upload

BrowserOps evidence:

```text
/home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260601-125358-p2p-upload-hardening-test
```

Endpoint:

```text
POST /api/v1/media/profile-picture
```

Results:

```text
Fake PHP file claiming image/jpeg -> 400 blocked
JPEG-like bytes but filename bad.php -> 400 blocked
JPEG bytes declared as image/png -> 400 blocked
```

Response snippets:

```text
Invalid profile picture file type
Uploaded file extension does not match its content
Uploaded file content does not match its declared file type
```

### Forum Attachment Upload

BrowserOps evidence:

```text
/home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260601-125707-p2p-forum-usecase-upload-hardening-test
```

Endpoint:

```text
POST /api/v1/media/forum-attachment
```

Results:

```text
Fake PHP claiming image/jpeg -> 400 blocked
JPEG bytes with .php filename -> 400 blocked
Valid PNG to someone else’s forum post -> 403 blocked
```

Response snippets:

```text
Invalid forum attachment file type
Uploaded file extension does not match its content
Only the forum post owner can upload attachments
```

### Use Case Media Upload

BrowserOps evidence:

```text
/home/hamza-minipc/Documents/PersonalOpsAgent/data/browser_artifacts/20260601-125707-p2p-forum-usecase-upload-hardening-test
```

Endpoint:

```text
POST /api/v1/media/usecase-media
```

Results:

```text
Upload to someone else’s use case -> 403 blocked
Valid PNG to someone else’s use case -> 403 blocked
```

Response snippet:

```text
Only the use case owner can upload media
```

Use case note: ownership checks run before content validation, so unauthorized use case upload attempts correctly fail with `403` before byte validation.

---

## Remaining Optional Hardening

The KACST issue is addressed for the discovered upload routes. Optional future improvements:

1. Add malware/antivirus scanning if required by KACST.
2. Remove GIF support if forum animated GIFs are not needed.
3. Review object storage serving headers such as `X-Content-Type-Options: nosniff` and `Content-Disposition`.
4. Add automated upload validation tests in CI.
