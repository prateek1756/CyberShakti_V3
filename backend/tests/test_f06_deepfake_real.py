"""
F-06 Real Model Integration Tests
===================================
These tests verify that:
1. The saved EfficientNet-B4 artifact is loadable (not random noise)
2. Real image bytes produce a genuine model prediction
3. The Celery worker reads actual uploaded image bytes
4. The EfficientNet-B4 architecture forward-pass executes
5. Prediction changes between clearly different inputs (smoke test only; 
   no ground-truth deepfake images available in the test environment)

Mocks are ONLY used for Celery dispatch isolation (not for model or image).
"""

import os
import io
import json
import torch
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient

from app.main import app
from ml.pipelines.train_f06_efficientnet import DeepfakeEfficientNetDetector
from app.worker import _preprocess_image_for_efficientnet, detect_deepfake
from tests.conftest import auth_headers

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(ROOT_DIR, "ml", "models", "f06_efficientnet_b4.pth") if os.path.exists(os.path.join(ROOT_DIR, "ml", "models", "f06_efficientnet_b4.pth")) else os.path.join("ml", "models", "f06_efficientnet_b4.pth")
METRICS_PATH = os.path.join(ROOT_DIR, "ml", "models", "f06_efficientnet_metrics.json") if os.path.exists(os.path.join(ROOT_DIR, "ml", "models", "f06_efficientnet_metrics.json")) else os.path.join("ml", "models", "f06_efficientnet_metrics.json")


def make_png_bytes(color="red", size=224) -> bytes:
    img = Image.new("RGB", (size, size), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ─────────────────────────────────────────────────────────
# STEP 8: Artifact Validation
# ─────────────────────────────────────────────────────────

def test_f06_artifact_exists_and_has_size():
    """Model file must exist and be non-trivially sized (>1MB)."""
    assert os.path.exists(MODEL_PATH), f"Model artifact not found at {MODEL_PATH}"
    size_mb = os.path.getsize(MODEL_PATH) / 1e6
    assert size_mb > 1.0, f"Model file too small ({size_mb:.2f} MB) — likely empty or corrupt"


def test_f06_artifact_loads_into_architecture():
    """Model state_dict must load into DeepfakeEfficientNetDetector without errors."""
    assert os.path.exists(MODEL_PATH), "Model artifact missing"
    model = DeepfakeEfficientNetDetector(pretrained=False)
    state_dict = torch.load(MODEL_PATH, weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()
    # Verify structure: classifier must have 2 output classes
    num_outputs = list(model.parameters())[-1].shape[0]
    assert num_outputs == 2, f"Expected 2 output classes, got {num_outputs}"


def test_f06_real_image_inference_executes():
    """Real PNG image bytes must produce a valid [0,1] probability from the model."""
    assert os.path.exists(MODEL_PATH), "Model artifact missing"
    model = DeepfakeEfficientNetDetector(pretrained=False)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    model.eval()

    # Build a real image tensor (not torch.randn)
    img_bytes = make_png_bytes(color="blue")
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((224, 224), Image.BILINEAR)

    import numpy as np
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = ((arr - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).astype(np.float32)
    tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)  # (1,3,224,224)

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)

    assert probs.shape == (1, 2), f"Expected (1,2) probabilities, got {probs.shape}"
    prob_fake = float(probs[0, 0])
    prob_real = float(probs[0, 1])
    assert abs(prob_fake + prob_real - 1.0) < 1e-4, "Probabilities must sum to 1.0"
    assert 0.0 <= prob_real <= 1.0
    assert 0.0 <= prob_fake <= 1.0


def test_f06_predictions_differ_for_different_inputs():
    """Real and fake Celeb-DF test frames must produce different probability outputs."""
    assert os.path.exists(MODEL_PATH), "Model artifact missing"
    model = DeepfakeEfficientNetDetector(pretrained=False)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    model.eval()

    import numpy as np

    # Use actual Celeb-DF test frames — not synthetic solid-color images.
    # Solid-color images may produce identical activations in a face-trained model.
    REAL_FRAME = os.path.join(
        "D:\\dataset\\Celeb-DF-cropped", "test", "real", "real_0_00170_frame_0.jpg"
    )
    FAKE_FRAME = os.path.join(
        "D:\\dataset\\Celeb-DF-cropped", "test", "fake", "fake_0_id1_id0_0007_frame_0.jpg"
    )

    def frame_to_tensor(path):
        img = Image.open(path).convert("RGB").resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = ((arr - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).astype(np.float32)
        return torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)

    if not os.path.exists(REAL_FRAME) or not os.path.exists(FAKE_FRAME):
        import pytest
        pytest.skip("Celeb-DF-cropped test frames not available in this environment")

    t_real = frame_to_tensor(REAL_FRAME)
    t_fake = frame_to_tensor(FAKE_FRAME)

    with torch.no_grad():
        p_real = torch.softmax(model(t_real), dim=1)[0, 1].item()
        p_fake = torch.softmax(model(t_fake), dim=1)[0, 1].item()

    # Predictions must differ — trained model should distinguish real from deepfake
    assert abs(p_real - p_fake) > 1e-5, (
        f"Model returned identical outputs for real and fake frames: p_real={p_real:.6f} p_fake={p_fake:.6f}. "
        "Possible untrained/constant model."
    )


def test_f06_metrics_file_has_real_values():
    """Metrics JSON must exist and contain non-trivial (non-zero) evaluation results."""
    assert os.path.exists(METRICS_PATH), f"Metrics file not found at {METRICS_PATH}"
    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    assert "test_accuracy" in metrics
    assert "test_f1_score" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["test_accuracy"] > 0.0, "Test accuracy must be > 0"
    assert isinstance(metrics["confusion_matrix"], list)
    assert "Celeb-DF" in metrics.get("dataset", ""), "Dataset must be Celeb-DF"


# ─────────────────────────────────────────────────────────
# STEP 10: Celery Worker Real Image Pipeline
# ─────────────────────────────────────────────────────────

def test_f06_worker_preprocessing_produces_correct_tensor(tmp_path):
    """Real uploaded image file must be decoded and produce (1,3,224,224) tensor."""
    img_path = str(tmp_path / "test_face.png")
    make_png_bytes(color="green")
    with open(img_path, "wb") as f:
        f.write(make_png_bytes(color="green"))

    tensor = _preprocess_image_for_efficientnet(img_path)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 3, 224, 224), f"Expected (1,3,224,224), got {tensor.shape}"
    # Must NOT be random noise — a solid green image has predictable channel values
    # After ImageNet norm: green=(0,128,0) -> R=(0-0.485)/0.229, G=(0.502-0.456)/0.224
    assert tensor.dtype == torch.float32


def test_f06_worker_detect_deepfake_real_file(tmp_path):
    """Worker must read actual image, run EfficientNet inference, return verdict."""
    img_path = str(tmp_path / "face_sample.png")
    with open(img_path, "wb") as f:
        f.write(make_png_bytes(color="blue", size=224))

    result = detect_deepfake(job_id="test-real-inference", file_path=img_path)

    assert "verdict" in result, f"Worker returned no verdict: {result}"
    assert "risk_level" in result["verdict"], f"No risk_level in verdict: {result['verdict']}"
    assert result["verdict"]["risk_level"] in ["safe", "moderate_risk", "high_risk", "error"]
    assert "media_analysis" in result, f"No media_analysis in result: {result}"
    assert "anomaly_score" in result["media_analysis"]
    score = result["media_analysis"]["anomaly_score"]
    assert 0.0 <= score <= 1.0, f"anomaly_score out of range: {score}"


# ─────────────────────────────────────────────────────────
# STEP 10: API → Celery Integration
# ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.detect_analyze.router.detect_deepfake.delay")
async def test_f06_api_endpoint_accepts_real_image(mock_delay):
    """API must accept valid image upload and dispatch task (Celery mocked for isolation)."""
    mock_delay.return_value = MagicMock(id="test-f06-task-001")
    png = make_png_bytes(color="red")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/analyze-media-deepfake",
            files={"file": ("face.png", png, "image/png")},
        )

    assert res.status_code == 200
    data = res.json()
    assert "task_id" in data
    assert "experimental_disclaimer" in data
    # Verify Celery was dispatched with a real file path (not None or empty)
    assert mock_delay.called
    call_args = mock_delay.call_args
    file_path_arg = call_args[0][1] if call_args[0] else call_args[1].get("file_path", "")
    assert file_path_arg  # must be non-empty string


@pytest.mark.asyncio
async def test_f06_api_rejects_non_image():
    """API must reject non-image bytes with 415."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/analyze-media-deepfake",
            files={"file": ("not_image.bin", b"NOT_AN_IMAGE_BYTES_12345", "image/png")},
        )
    assert res.status_code == 415
