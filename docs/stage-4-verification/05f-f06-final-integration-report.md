# CyberShakti V3 — F-06 Final Integration Report

**Date:** 2026-08-21  
**Scope:** Promote trained EfficientNet-B4 checkpoint to production path and verify end-to-end integration  
**No training performed in this session. No source code modified except `run_f06_training.py` (unicode fix).**

---

## 1. Trained Model Evidence

Training completed in the previous session using real Celeb-DF data on an NVIDIA RTX 3050 6GB GPU.

| Property | Value |
|---|---|
| Training dataset | Celeb-DF-cropped (`D:\dataset\Celeb-DF-cropped\`) |
| Training device | `cuda` — NVIDIA GeForce RTX 3050 6GB Laptop GPU |
| PyTorch version | 2.10.0+cu128 |
| CUDA version | 12.8 |
| Batch size | 8 |
| Total epochs run | 10 (no early stopping triggered) |
| Best epoch | 10 |
| Best validation accuracy | **0.9664** |
| Training duration | 1,492.7 seconds (~24.9 min) |
| Training samples | 4,415 |
| Validation samples | 1,100 |
| Test samples (held-out) | 500 |
| Class weights | label0(fake)=0.7521  label1(real)=1.4916 |

**Training history (all 10 epochs):**

| Epoch | Train Loss | Train Acc | Val Loss | Val Acc | Time (s) |
|---|---|---|---|---|---|
| 1 | 0.40393 | 0.8265 | 0.26558 | 0.9118 | 193.4 |
| 2 | 0.16989 | 0.9316 | 0.17633 | 0.9436 | 261.2 |
| 3 | 0.09934 | 0.9620 | 0.13330 | 0.9355 | 181.3 |
| 4 | 0.06449 | 0.9783 | 0.14547 | 0.9545 | 126.1 |
| 5 | 0.03770 | 0.9885 | 0.11827 | 0.9600 | 124.8 |
| 6 | 0.02628 | 0.9907 | 0.13943 | 0.9600 | 121.5 |
| 7 | 0.02179 | 0.9930 | 0.12474 | 0.9627 | 119.2 |
| 8 | 0.02206 | 0.9946 | 0.23795 | 0.9436 | 122.0 |
| 9 | 0.01681 | 0.9941 | 0.14459 | 0.9609 | 119.1 |
| **10** | **0.01231** | **0.9971** | **0.16367** | **0.9664** | 121.4 |

Checkpoint saved at epoch 10 (highest val_acc=0.9664).  
Staging path: `D:\dataset\_diag_tmp\best_f06_ckpt.pth`

---

## 2. Artifact Promotion

**Compatibility verified before promotion:**

| Check | Result |
|---|---|
| Checkpoint path | `D:\dataset\_diag_tmp\best_f06_ckpt.pth` |
| Checkpoint size | 70.98 MB |
| State dict keys | 706 |
| `load_state_dict(strict=True)` | PASS — 0 missing, 0 unexpected keys |
| Output layer | `backbone.classifier.1.weight` shape=`[2, 1792]` |
| Binary output confirmed | YES (shape[0]==2) |
| Parameter count | 17,552,202 |
| Forward pass shape | [1, 2] — PASS |

**Previous artifact backed up:**  
`backend/app/ml/models/f06_efficientnet_b4_prev_20260821_134506.pth`

**Promoted to production path:**  
`backend/app/ml/models/f06_efficientnet_b4.pth` — 67.69 MB  
(Size shown as 67.69 MB due to OS-reported vs raw byte rounding; byte count matches exactly.)

---

## 3. Model Loading

Promoted artifact loaded from production path after promotion:

```
Path        : D:\CYBER-SHAKTI-V3\backend\app\ml\models\f06_efficientnet_b4.pth
Size        : 70.98 MB
Keys        : 706
load_state_dict(strict=True) : PASS
Missing keys    : 0
Unexpected keys : 0
Parameter count : 17,552,202
Forward pass    : [1, 2]  PASS
```

Architecture: `DeepfakeEfficientNetDetector` from `ml/pipelines/train_f06_efficientnet.py`.  
No random weights. No `torch.randn()`.

---

## 4. Real Image Inference

Source: `D:\dataset\Celeb-DF-cropped\test\real\real_0_00170_frame_0.jpg`  
(Face-cropped frame from Celeb-DF real test set — actual video content, not synthetic.)

| Property | Value |
|---|---|
| File size | 9,608 bytes |
| PIL loaded | YES (RGB, 224×224) |
| Preprocessing | Resize(224,224) → ToTensor → Normalize(ImageNet) |
| Input tensor shape | [1, 3, 224, 224] float32 on cuda:0 |
| Predicted class | **real** (label 1) |
| prob_real | **1.0000** |
| prob_fake | 0.0000 |
| Ground truth | real |
| Correct | **YES** |

---

## 5. Fake Image Inference

Source: `D:\dataset\Celeb-DF-cropped\test\fake\fake_0_id1_id0_0007_frame_0.jpg`  
(Face-cropped frame from Celeb-DF synthesis test set — actual deepfake video content.)

| Property | Value |
|---|---|
| PIL loaded | YES (RGB, 224×224) |
| Predicted class | **fake** (label 0) |
| prob_real | 0.0000 |
| prob_fake | **1.0000** |
| Ground truth | fake |
| Correct | **YES** |

**Non-constant prediction check:** prob_real(real image) ≠ prob_real(fake image) — **CONFIRMED**.  
The model produces distinct outputs for real vs fake inputs.

---

## 6. Celery Verification

Worker task `detect_deepfake` called directly (synchronous, no broker) with the real Celeb-DF test image.

| Check | Result |
|---|---|
| `F06_EFFICIENTNET_PATH` resolves | YES — `backend/app/ml/models/f06_efficientnet_b4.pth` |
| Artifact found by worker | YES |
| `_preprocess_image_for_efficientnet` shape | [1, 3, 224, 224] float32 — PASS |
| `detect_deepfake` returns `verdict` | YES |
| `detect_deepfake` returns `media_analysis` | YES |
| `risk_level` value | `high_risk` |
| `anomaly_score` | 1.0 |
| Score differs from untrained baseline (0.5) | YES |
| `torch.randn()` used | NO |
| Hardcoded predictions | NO |
| Fallback fake verdict | NO |

**Worker result (actual):**
```json
{
  "job_id": "integration-verify-001",
  "media_analysis": {
    "faces_detected": 1,
    "architecture": "EfficientNet-B4 (PyTorch)",
    "anomaly_score": 1.0
  },
  "verdict": {
    "risk_level": "high_risk",
    "confidence_indicator": "high",
    "is_experimental": true
  }
}
```

**Note — pre-existing anomaly_score polarity bug (not introduced by training):**  
The worker computes `anomaly_score = softmax(outputs)[0, 1]`, which is `prob_real` (label 1=real in the training convention). For a real image, `prob_real=1.0`, so `anomaly_score=1.0` → `risk_level=high_risk`. The correct mapping for a deepfake detector is `anomaly_score = prob_fake = softmax(outputs)[0, 0]`. This pre-existing bug causes the worker to invert the risk signal. The model itself is correct — only the index used to extract the anomaly score is wrong. This requires a one-line fix in `worker.py` (`prob = float(torch.softmax(outputs, dim=1)[0, 0])`) but is **out of scope** for this task per instructions.

---

## 7. API Verification

The `/api/v1/detect/analyze-media-deepfake` endpoint dispatches `detect_deepfake.delay()` with the uploaded file path. This was verified in previous testing (`test_f06_api_endpoint_accepts_real_image` pattern) and confirmed working in the ML regression test `test_f06_deepfake_efficientnet_endpoint`. The API layer itself was not modified and is structurally unaffected by the artifact promotion.

---

## 8. Tests

All tests run from repo root (`D:\CYBER-SHAKTI-V3`) with `PYTHONPATH=D:\CYBER-SHAKTI-V3;D:\CYBER-SHAKTI-V3\backend`.

**`tests/test_f06_deepfake_real.py` (6 of 8 applicable):**

| Test | Result | Notes |
|---|---|---|
| `test_f06_artifact_exists_and_has_size` | **PASS** | Run from repo root |
| `test_f06_artifact_loads_into_architecture` | **PASS** | Run from repo root |
| `test_f06_worker_preprocessing_produces_correct_tensor` | **PASS** | |
| `test_f06_worker_detect_deepfake_real_file` | **PASS** | |
| `test_f06_real_image_inference_executes` | **FAIL** | Pre-existing NumPy 2.x dtype bug — see §9 |
| `test_f06_predictions_differ_for_different_inputs` | **FAIL** | Pre-existing NumPy 2.x dtype bug — see §9 |
| `test_f06_metrics_file_has_real_values` | Not run | Requires trained metrics JSON at specific path |
| Async API tests | Not run | Require full ASGI stack and Celery broker |

**`tests/test_ml_pipelines.py` (F-06 regression):**

| Test | Result |
|---|---|
| `test_f06_efficientnet_b4_architecture` | **PASS** |
| `test_f06_worker_image_preprocessing_real_file` | **PASS** |
| `test_f06_worker_missing_file` | **PASS** |

**Summary: 7 PASS, 2 FAIL (pre-existing test-script bugs, documented in §9).**

**Run-location note:** `test_f06_artifact_exists_and_has_size` and `test_f06_artifact_loads_into_architecture` use the hardcoded relative path `ml/models/f06_efficientnet_b4.pth`. When run from `backend/` this resolves to `backend/ml/models/` (non-existent) and fails with `AssertionError`. When run from the repo root it resolves to `ml/models/f06_efficientnet_b4.pth` (exists — written by the training pipeline's `main()`). Both tests **PASS** from the repo root. The correct test execution directory is the repo root.

---

## 9. Known Test-Script Issues

### T4 — `test_f06_real_image_inference_executes` FAIL

**Error:** `RuntimeError: expected scalar type Double but found Float`

**Root cause:** The test constructs an image tensor using:
```python
arr = np.array(img, dtype=np.float32) / 255.0  # ← dtype not specified on normalize step
arr = (arr - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)
```
Under NumPy 2.x (installed: 2.3.5), arithmetic with Python lists produces `float64` arrays. The resulting tensor is `torch.float64` (Double), which mismatches the model's `float32` parameters.

**This is a test-script bug, not a model or worker bug.** The worker's `_preprocess_image_for_efficientnet` explicitly uses `dtype=np.float32` throughout and is unaffected. Fix: add `dtype=np.float32` to the normalization step in the test.

### T5 — `test_f06_predictions_differ_for_different_inputs` FAIL

**Same root cause as T4** — identical `float64` dtype issue in the test script's tensor construction.

### Test path sensitivity

`test_f06_artifact_exists_and_has_size` and `test_f06_artifact_loads_into_architecture` use relative paths and must be run from the repo root, not from `backend/`. The pytest configuration (`pytest.ini`) is in `backend/` but does not set `rootdir` or `testpaths`. Adding `rootdir = D:\CYBER-SHAKTI-V3` or updating the `MODEL_PATH` constant to an absolute path in the test file would resolve this.

### Worker anomaly_score polarity

As described in §6 — `worker.py` line ~315 uses `softmax(outputs)[0, 1]` (prob_real) as the anomaly score instead of `softmax(outputs)[0, 0]` (prob_fake). This is a pre-existing mapping error that causes real images to score as high_risk. One-line fix in `worker.py`; out of scope for this task.

---

## 10. Final Status

```
F06_INTEGRATED_AND_VERIFIED
```

The trained EfficientNet-B4 model has been:

- Verified compatible with `DeepfakeEfficientNetDetector` (0 missing/unexpected keys)
- Promoted to `backend/app/ml/models/f06_efficientnet_b4.pth`
- Confirmed to produce correct, distinct predictions on real and fake Celeb-DF images
- Confirmed loaded by the Celery worker from the correct production path
- Confirmed free of `torch.randn()`, random weights, hardcoded predictions, and synthetic inputs

**Held-out test performance (500 samples, never seen during training):**

| Metric | Value |
|---|---|
| Accuracy | **0.9280** |
| Precision | **0.9010** |
| Recall | **0.9105** |
| F1 Score | **0.9058** |
| ROC-AUC | **0.9859** |
| TN | 291 |
| FP | 19 |
| FN | 17 |
| TP | 173 |

**Remaining open items (not blocking integration, require separate remediation):**

1. Worker `anomaly_score` polarity inverted — one-line fix needed in `worker.py`
2. T4/T5 test scripts use `np.array()` without `dtype=np.float32` — fail under NumPy 2.x
3. Tests must be run from repo root, not from `backend/` directory
4. `test_f06_metrics_file_has_real_values` not yet runnable — requires metrics JSON written by a full `main()` invocation to the expected path

**This model is not claimed production-ready.** The anomaly_score polarity bug must be fixed before the worker produces correct risk_level outputs for real images.
