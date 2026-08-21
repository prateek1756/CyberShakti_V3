"""
OCR service for F-03 Screenshot Scam Scanner.

Engine: EasyOCR (en) — ADR-022 provisionally specifies PaddleOCR; EasyOCR is the
available equivalent. The abstraction allows swapping without changing callers.
"""

from __future__ import annotations

import io
import logging
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)

_reader = None  # lazy-loaded singleton


def _get_reader():
    """Lazy-load EasyOCR reader to avoid startup cost."""
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        except Exception as exc:
            logger.error("EasyOCR reader initialisation failed: %s", exc)
            raise
    return _reader


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """
    Run OCR on raw image bytes and return extracted plain text.

    Raises:
        ValueError: if image_bytes cannot be decoded as a valid image.
        RuntimeError: if OCR engine fails.
    """
    if not image_bytes:
        raise ValueError("Empty image bytes provided to OCR engine.")

    # Validate PIL can decode the image
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # checks file integrity
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc

    # Re-open after verify() (verify consumes the file pointer)
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot open image for processing: {exc}") from exc

    reader = _get_reader()

    try:
        results = reader.readtext(image_bytes, detail=0, paragraph=True)
    except Exception as exc:
        logger.error("EasyOCR readtext failed: %s", exc)
        raise RuntimeError(f"OCR processing failed: {exc}") from exc

    extracted = " ".join(r.strip() for r in results if r.strip())
    logger.info("OCR extracted %d characters from image (%d bytes)", len(extracted), len(image_bytes))
    return extracted
