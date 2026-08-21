"""Upload validation helpers (magic-byte checks; path-safe names)."""

from __future__ import annotations

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
GIF_MAGIC = b"GIF8"
WEBP_RIFF = b"RIFF"
WEBP_WEBP = b"WEBP"


class UploadError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 415):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_image_bytes(content: bytes) -> str:
    if not content or len(content) < 12:
        raise UploadError("UNSUPPORTED_FILE_TYPE", "File must be a JPEG or PNG image.")
    if content.startswith(JPEG_MAGIC):
        return "jpeg"
    if content.startswith(PNG_MAGIC):
        return "png"
    if content.startswith(GIF_MAGIC):
        return "gif"
    if content.startswith(WEBP_RIFF) and content[8:12] == WEBP_WEBP:
        return "webp"
    raise UploadError("UNSUPPORTED_FILE_TYPE", "File must be a JPEG or PNG image.")
