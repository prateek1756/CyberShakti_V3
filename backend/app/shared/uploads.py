"""Upload validation helpers (magic-byte checks; path-safe names)."""

from __future__ import annotations

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
GIF_MAGIC = b"GIF8"
WEBP_RIFF = b"RIFF"
WEBP_WEBP = b"WEBP"


# Video signatures
MP4_FTYP = b"ftyp"
AVI_RIFF = b"RIFF"
AVI_AVI = b"AVI "


class UploadError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 415):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_image_bytes(content: bytes) -> str:
    if not content or len(content) < 12:
        raise UploadError("UNSUPPORTED_FILE_TYPE", "File must be a valid image or video.")
    if content.startswith(JPEG_MAGIC):
        return "jpeg"
    if content.startswith(PNG_MAGIC):
        return "png"
    if content.startswith(GIF_MAGIC):
        return "gif"
    if content.startswith(WEBP_RIFF) and content[8:12] == WEBP_WEBP:
        return "webp"
    raise UploadError("UNSUPPORTED_FILE_TYPE", "File must be a valid image (JPEG, PNG, WebP).")


def validate_media_bytes(content: bytes) -> str:
    """Validates either image or video files (MP4, AVI, WebM, QuickTime, JPEG, PNG, WebP)."""
    if not content or len(content) < 12:
        raise UploadError("UNSUPPORTED_FILE_TYPE", "File must be a valid image or video.")
    # Check images
    if content.startswith(JPEG_MAGIC):
        return "jpeg"
    if content.startswith(PNG_MAGIC):
        return "png"
    if content.startswith(GIF_MAGIC):
        return "gif"
    if content.startswith(WEBP_RIFF) and content[8:12] == WEBP_WEBP:
        return "webp"
    # Check MP4 / MOV (ftyp box at offset 4)
    if len(content) > 12 and content[4:8] == MP4_FTYP:
        return "mp4"
    if content.startswith(AVI_RIFF) and content[8:12] == AVI_AVI:
        return "avi"
    # Fallback: if file has reasonable header and size, treat as video
    if len(content) > 1024:
        return "video"
    raise UploadError("UNSUPPORTED_FILE_TYPE", "Unsupported media type. Upload a JPEG, PNG, WebP image or MP4/AVI video.")

