"""QR payload extraction from image bytes. Returns None if unreadable."""

from __future__ import annotations

import io
from typing import Optional
import numpy as np
from PIL import Image


def decode_qr_payload(image_bytes: bytes) -> Optional[str]:
    # 1. Try OpenCV QRCodeDetector (Fast, native C++, no external DLL issues)
    try:
        import cv2
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        cv_img = np.array(img)[:, :, ::-1].copy()
        detector = cv2.QRCodeDetector()
        val, points, _ = detector.detectAndDecode(cv_img)
        if val and len(val.strip()) > 0:
            return val.strip()
    except Exception:
        pass

    # 2. Try pyzbar fallback
    try:
        from pyzbar.pyzbar import decode as zbar_decode
        image = Image.open(io.BytesIO(image_bytes))
        results = zbar_decode(image)
        if results:
            raw = results[0].data
            try:
                return raw.decode("utf-8").strip()
            except UnicodeDecodeError:
                return raw.decode("latin-1", errors="replace").strip()
    except Exception:
        pass

    return None

