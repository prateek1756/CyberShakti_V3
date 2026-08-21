import os
import io
import torch
import pytest
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.main import app
from ml.pipelines.train_f01_phishing_url import extract_url_features
from ml.pipelines.train_f06_efficientnet import DeepfakeEfficientNetDetector
from app.worker import run_screenshot_ocr, detect_deepfake, _preprocess_image_for_efficientnet
from app.shared.uploads import validate_image_bytes, UploadError

# Helper to generate valid PNG bytes
def make_valid_png_bytes(width=100, height=100, color="red") -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

VALID_PNG = make_valid_png_bytes()


def test_f01_xgb_feature_extraction():
    url = "http://verify-bank.kyc-update.info/login?id=123"
    feats = extract_url_features(url)
    assert feats["url_length"] == len(url)
    assert feats["has_ip_address"] == 0
    assert feats["uses_https"] == 0
    assert feats["subdomain_count"] >= 1


@pytest.mark.asyncio
async def test_f01_phishing_url_xgb_inference():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/scan-url", json={"url": "http://sbi-verify-kyc.info/login"})
    assert res.status_code == 200
    data = res.json()
    assert "verdict" in data
    assert data["verdict"]["risk_level"] in ["high_risk", "moderate_risk", "safe"]


@pytest.mark.asyncio
async def test_f02_scam_text_inference():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/scan-message", json={"text": "URGENT: Your electricity connection will be disconnected tonight at 9:30 PM due to overdue bill. Call officer at 9876543210."})
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"]["risk_level"] in ["high_risk", "moderate_risk", "safe"]


def test_f06_efficientnet_b4_architecture():
    model = DeepfakeEfficientNetDetector(pretrained=False)
    dummy_tensor = torch.randn(2, 3, 224, 224)
    out = model(dummy_tensor)
    assert out.shape == (2, 2)


@pytest.mark.asyncio
@patch("app.detect_analyze.router.assess_fake_profile.delay")
async def test_f05_fake_profile_task(mock_delay):
    mock_delay.return_value = MagicMock(id="task-123")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/assess-profile", json={"signals": {"sent_unsolicited_money_request": True, "following_to_follower_ratio_high": True}})
    assert res.status_code == 200
    assert "task_id" in res.json()


@pytest.mark.asyncio
@patch("app.detect_analyze.router.detect_deepfake.delay")
async def test_f06_deepfake_efficientnet_endpoint(mock_delay):
    mock_delay.return_value = MagicMock(id="task-123")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/analyze-media-deepfake",
            files={"file": ("test.png", VALID_PNG, "image/png")}
        )
    assert res.status_code == 200
    assert "experimental_disclaimer" in res.json()
    assert "task_id" in res.json()


@pytest.mark.asyncio
@patch("app.detect_analyze.router.run_screenshot_ocr.delay")
async def test_f03_screenshot_endpoint_valid_image(mock_delay):
    mock_delay.return_value = MagicMock(id="task-screenshot-123")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-screenshot",
            files={"file": ("screenshot.png", VALID_PNG, "image/png")}
        )
    assert res.status_code == 200
    assert "task_id" in res.json()
    assert res.json()["status"] == "queued"


@pytest.mark.asyncio
async def test_upload_invalid_magic_bytes_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-screenshot",
            files={"file": ("fake.png", b"NOT_A_REAL_IMAGE_BYTES_1234567890", "image/png")}
        )
    assert res.status_code == 415
    assert res.json()["detail"]["error_code"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_empty_file_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-screenshot",
            files={"file": ("empty.png", b"", "image/png")}
        )
    assert res.status_code == 400
    assert res.json()["detail"]["error_code"] == "EMPTY_FILE"


@pytest.mark.asyncio
@patch("app.detect_analyze.router.detect_mule_account.delay")
async def test_f07_mule_account_task(mock_delay):
    mock_delay.return_value = MagicMock(id="task-123")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/assess-mule-account", json={"account_signals": {"transaction_velocity_high": True, "pass_through": True}})
    assert res.status_code == 200
    assert "task_id" in res.json()


def test_f06_worker_image_preprocessing_real_file(tmp_path):
    # Test real file preprocessing produces correct (1,3,224,224) tensor
    test_img = tmp_path / "sample.png"
    test_img.write_bytes(VALID_PNG)
    tensor = _preprocess_image_for_efficientnet(str(test_img))
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 3, 224, 224)


def test_f06_worker_missing_file():
    res = detect_deepfake(job_id="test-job", file_path="nonexistent_file_xyz.png")
    assert res["error"] == "FILE_NOT_FOUND"


def test_f03_worker_missing_file():
    res = run_screenshot_ocr(job_id="test-job", file_path="nonexistent_file_xyz.png")
    assert res["error"] == "OCR_FILE_NOT_FOUND"
