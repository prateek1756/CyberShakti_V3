"""QR payload extraction from image bytes. Returns None if unreadable."""

from __future__ import annotations

import io
from typing import Optional
import numpy as np
from PIL import Image


def decode_qr_payload(image_bytes: bytes) -> Optional[str]:
    # 1. Try OpenCV QRCodeDetector with multi-stage preprocessing
    try:
        import cv2

        pil_img = Image.open(io.BytesIO(image_bytes))
        # Handle RGBA / Palette images with white background
        if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
            bg = Image.new("RGB", pil_img.size, (255, 255, 255))
            if pil_img.mode == "P":
                pil_img = pil_img.convert("RGBA")
            bg.paste(pil_img, mask=pil_img.split()[-1])
            img_rgb = bg
        else:
            img_rgb = pil_img.convert("RGB")

        cv_img = np.array(img_rgb)[:, :, ::-1].copy()
        detector = cv2.QRCodeDetector()

        # Pass A: Standard RGB image
        val, _, _ = detector.detectAndDecode(cv_img)
        if val and len(val.strip()) > 0:
            return val.strip()

        # Pass B: Grayscale
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        val, _, _ = detector.detectAndDecode(gray)
        if val and len(val.strip()) > 0:
            return val.strip()

        # Pass C: Otsu Binary Thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        val, _, _ = detector.detectAndDecode(thresh)
        if val and len(val.strip()) > 0:
            return val.strip()

        # Pass D: Upscale low-res QR images (2x)
        h, w = gray.shape[:2]
        if min(h, w) < 400:
            resized = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
            val, _, _ = detector.detectAndDecode(resized)
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


