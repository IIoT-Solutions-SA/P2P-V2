"""Server-side upload validation helpers.

The browser/request-provided Content-Type and filename are not trusted for
security decisions. These helpers validate the actual file bytes, enforce size
limits, and return a canonical MIME type + safe extension to use for storage.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile


@dataclass(frozen=True)
class ValidatedUpload:
    """Validated upload payload and canonical storage metadata."""

    content: bytes
    mime_type: str
    extension: str
    safe_filename: str
    original_filename: str


MIME_EXTENSIONS: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "video/mp4": "mp4",
    "video/webm": "webm",
}

EXTENSION_MIME_TYPES: dict[str, set[str]] = {
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "png": {"image/png"},
    "webp": {"image/webp"},
    "gif": {"image/gif"},
    "mp4": {"video/mp4"},
    "webm": {"video/webm"},
}


def _detect_mime_type(content: bytes) -> str | None:
    """Detect supported MIME types from file signatures/magic bytes."""
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if _looks_like_mp4(content):
        return "video/mp4"
    if content.startswith(b"\x1a\x45\xdf\xa3"):
        return "video/webm"
    return None


def _looks_like_mp4(content: bytes) -> bool:
    """Return True for common MP4/ISO-BMFF signatures."""
    if len(content) < 12:
        return False
    # Bytes 4..8 normally contain the ftyp box marker.
    if content[4:8] != b"ftyp":
        return False
    major_brand = content[8:12]
    compatible = content[8:64]
    mp4_markers = (
        b"isom",
        b"iso2",
        b"mp41",
        b"mp42",
        b"avc1",
        b"M4V ",
        b"M4A ",
        b"MSNV",
    )
    return major_brand in mp4_markers or any(marker in compatible for marker in mp4_markers)


def _safe_stem(filename: str) -> str:
    """Return a conservative filename stem for metadata/storage inputs."""
    stem = Path(filename or "upload").name.rsplit(".", 1)[0].strip().lower()
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in stem)
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:80] or "upload"


async def validate_upload_file(
    file: UploadFile,
    *,
    allowed_mime_types: Iterable[str],
    max_size: int,
    purpose: str,
) -> ValidatedUpload:
    """Read and validate an uploaded file.

    Validates actual file bytes instead of trusting user-controlled headers.
    Raises HTTPException with a safe client-facing error on validation failure.
    """
    allowed = set(allowed_mime_types)
    original_filename = Path(file.filename or "upload").name

    if file.size and file.size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise HTTPException(400, f"File too large. Maximum size is {max_mb}MB.")

    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(content) > max_size:
        max_mb = max_size // (1024 * 1024)
        raise HTTPException(400, f"File too large. Maximum size is {max_mb}MB.")

    detected_mime = _detect_mime_type(content)
    if not detected_mime or detected_mime not in allowed:
        allowed_display = ", ".join(sorted(allowed))
        raise HTTPException(400, f"Invalid {purpose} file type. Allowed: {allowed_display}.")

    # If a client sent Content-Type, it must agree with actual bytes. Empty or
    # generic types are treated as untrusted but not fatal once bytes validate.
    claimed_mime = (file.content_type or "").lower().strip()
    generic_mimes = {"", "application/octet-stream", "binary/octet-stream"}
    if claimed_mime not in generic_mimes and claimed_mime != detected_mime:
        raise HTTPException(400, "Uploaded file content does not match its declared file type.")

    # If the filename has an extension, it must match the detected content.
    suffix = Path(original_filename).suffix.lower().lstrip(".")
    if suffix and detected_mime not in EXTENSION_MIME_TYPES.get(suffix, set()):
        raise HTTPException(400, "Uploaded file extension does not match its content.")

    from app.core.input_validation import check_safe_text
    try:
        # Validate original filename metadata using the standard text validator
        original_filename = check_safe_text(original_filename)
    except ValueError as e:
        raise HTTPException(400, f"Invalid filename: {str(e)}")

    extension = MIME_EXTENSIONS[detected_mime]
    safe_filename = f"{_safe_stem(original_filename)}.{extension}"
    return ValidatedUpload(
        content=content,
        mime_type=detected_mime,
        extension=extension,
        safe_filename=safe_filename,
        original_filename=original_filename,
    )
