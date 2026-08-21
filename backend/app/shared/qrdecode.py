"""QR payload extraction from image bytes. Returns None if unreadable."""

from __future__ import annotations

import io
from typing import Optional


def decode_qr_payload(image_bytes: bytes) -> Optional[str]:
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode as zbar_decode
    except ImportError:
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
        results = zbar_decode(image)
    except Exception:
        return None

    if not results:
        return None
    raw = results[0].data
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")
