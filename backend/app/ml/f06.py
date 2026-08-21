"""F-06 research pipeline: OpenCV face detection. CNN weights are not loaded without licensed datasets."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from app.shared.explanation_engine import generate_explanation


def analyze_media(image_bytes: bytes) -> Dict[str, Any]:
    import cv2

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("unreadable_image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    face_count = int(len(faces))
    verdict = generate_explanation(
        feature_id="F-06",
        risk_level="low_risk" if face_count else "safe",
        signals=["face_detected"] if face_count else ["no_face_detected"],
        is_experimental=True,
    )
    return {
        "media_analysis": {
            "faces_detected": face_count,
            "media_type": "image",
            "cnn_weights_loaded": False,
        },
        "verdict": verdict,
        "model_note": (
            "OpenCV Haar face detection ran. EfficientNet/Xception weights are not loaded: "
            "FaceForensics++ / Celeb-DF / DFDC were not licensed or downloaded in this environment."
        ),
    }
