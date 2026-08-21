# CyberShakti V3 — F-06 Diagnostic Report

**Generated:** 2026-08-21  
**Scope:** Identify the first technical blocker preventing reliable Celeb-DF → EfficientNet-B4 training  
**Instruction:** Diagnostic only. No training performed. No source code modified.

---

## 1. Environment

| Property | Value |
|---|---|
| OS | Windows 10 Home Single Language 25H2 (Build 26200) |
| Python | 3.14.1 (CPython, 64-bit, MSC v.1944) |
| Python executable | `C:\Python314\python.exe` |
| PyTorch | 2.10.0+cpu |
| torchvision | 0.25.0+cpu |
| OpenCV (cv2) | 4.13.0 |
| Pillow | 12.0.0 |
| timm | 1.0.27 |
| numpy | 2.3.5 |

---

## 2. GPU / CUDA

| Property | Value |
|---|---|
| CUDA available | **NO** |
| GPU detected | None |
| GPU VRAM | N/A |
| PyTorch build | CPU-only (`+cpu` suffix) |
| CUDA version | Not installed |

**This is the primary training blocker.** PyTorch was installed as the CPU-only wheel. No NVIDIA GPU or CUDA runtime is present on this machine.

---

## 3. Dependencies

All Python dependencies required for F-06 inference are installed and functional:

| Library | Status |
|---|---|
| torch | OK (CPU only) |
| torchvision | OK (CPU only) |
| timm | OK — `efficientnet_b4` model available |
| cv2 (OpenCV) | OK |
| Pillow | OK |
| numpy | OK |

No missing import errors for the F-06 inference path.  
`torch.randn()` is **not present** in the production F-06 inference path (`worker.py`, `app/ml/f06.py`). It appears only in test files (`tests/test_f06_deepfake_real.py`, `tests/test_ml_pipelines.py`).

---

## 4. Celeb-DF Dataset

| Property | Value |
|---|---|
| ZIP path | `D:\dataset\Celeb-DF.zip` |
| ZIP size | 1.976 GB |
| ZIP integrity | **OK** — `testzip()` returned no bad files |
| Total entries | 1,203 MP4 files + 1 TXT |
| `Celeb-real/` videos | 158 |
| `Celeb-synthesis/` (fake) videos | 795 |
| `YouTube-real/` videos | 250 |
| `List_of_testing_videos.txt` | **Present** (100 entries) |

Face-cropped frame dataset already extracted at `D:\dataset\Celeb-DF-cropped\`:

| Split | Real frames | Fake frames | Total |
|---|---|---|---|
| train | 1,480 | 2,935 | 4,415 |
| val | 370 | 730 | 1,100 |
| test | 190 | 310 | 500 |

Class imbalance ratio: ~2:1 fake-to-real (manageable with class weights, already implemented in `train_f06_efficientnet.py`).

---

## 5. Real Video Test

**REAL VIDEO**

| Property | Value |
|---|---|
| Path | `D:\dataset\_diag_tmp\Celeb-real\id0_0000.mp4` |
| Size | 2,345,071 bytes (2.24 MB) |
| OpenCV opened | **YES** |
| Resolution | 942 × 500 @ 30.00 fps, 469 frames |
| Frame decoded | **YES** |
| Frame shape | (500, 942, 3) |
| PIL opened | **YES** |
| PIL image size | (942, 500) |

**FAKE VIDEO**

| Property | Value |
|---|---|
| Path | `D:\dataset\_diag_tmp\Celeb-synthesis\id0_id16_0000.mp4` |
| Size | 2,203,086 bytes (2.10 MB) |
| OpenCV opened | **YES** |
| Resolution | 944 × 500 @ 30.00 fps, 469 frames |
| Frame decoded | **YES** |
| Frame shape | (500, 944, 3) |
| PIL opened | **YES** |
| PIL image size | (944, 500) |

---

## 6. Frame Extraction Test

Both frames extracted and saved to `D:\dataset\_diag_tmp\frames\`:

- `REAL_VIDEO_frame.png` — decoded from `Celeb-real/id0_0000.mp4`, frame 0
- `FAKE_VIDEO_frame.png` — decoded from `Celeb-synthesis/id0_id16_0000.mp4`, frame 0

Both files confirmed readable by PIL. Frame extraction pipeline: **WORKING**.

---

## 7. EfficientNet-B4 Initialization

Test used `torchvision.models.efficientnet_b4` via `DeepfakeEfficientNetDetector` (the project's own class from `ml/pipelines/train_f06_efficientnet.py`), and also confirmed via `timm.create_model`.

| Check | Result |
|---|---|
| Architecture instantiated | **YES** |
| Classifier output features | **2** (binary: real=1, fake=0) |
| Binary classifier confirmed | **YES** |
| CPU move | **YES** |
| CUDA move | **SKIPPED** (CUDA not available) |
| Model class | `DeepfakeEfficientNetDetector` — `backbone = efficientnet_b4(weights=...)` |
| Classifier head | `nn.Dropout(0.3) → nn.Linear(in_features, 2)` |
| IMG_SIZE in training script | 224 × 224 (EfficientNet-B4 native is 380 × 380 — suboptimal but non-blocking) |

Existing trained `.pth` artifact at `backend/app/ml/models/f06_efficientnet_b4.pth`:

| Property | Value |
|---|---|
| File size | 70.98 MB |
| State dict keys | 706 |
| Loads into `DeepfakeEfficientNetDetector` | **YES** — no key mismatches |

---

## 8. Real Image Inference

Forward pass using the real Celeb-DF frame (`REAL_VIDEO_frame.png`) — no synthetic tensors used.

| Check | Result |
|---|---|
| PIL load | YES |
| Preprocessing | Resize(380, 380) → ToTensor → Normalize(ImageNet) |
| Input tensor shape | [1, 3, 380, 380] |
| Input dtype | torch.float32 |
| Device | cpu |
| Output shape | [1, 2] |
| Softmax probabilities | [0.4999911, 0.5000089] (expected — untrained weights) |
| Inference completed | **YES** |
| Exception | None |

Real-image inference pipeline: **WORKING** end-to-end on CPU.

---

## 9. Existing F-06 Pipeline

### 9.1 API Endpoint

- **File:** `backend/app/detect_analyze/router.py`
- **Endpoint:** `POST /analyze-media-deepfake`
- **Behaviour:** Validates upload, writes bytes to `scan-uploads/media_{uuid}.bin`, dispatches `detect_deepfake.delay(job_id, file_path)` — **correctly passes real file bytes via file path**

### 9.2 Celery Task

- **File:** `backend/app/worker.py` — `detect_deepfake(job_id, file_path)`
- **Step 1:** Calls `_preprocess_image_for_efficientnet(file_path)` → reads real bytes from disk, decodes with PIL, resizes to 224×224, returns `(1,3,224,224)` tensor — **correct**
- **Step 2:** `from ml.pipelines.train_f06_efficientnet import DeepfakeEfficientNetDetector` — **import inside task function body**; resolves only if repo root is on `PYTHONPATH`; `backend/ml/pipelines/train_f06_efficientnet.py` does **not exist**
- **Step 3:** `F06_EFFICIENTNET_PATH = os.path.join(MODEL_DIR, "f06_efficientnet_b4.pth")` — **resolves to wrong path**

### 9.3 Model Artifact Path — BROKEN

```
worker.py line 37:
  MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models")

__file__                         = backend/app/worker.py
os.path.dirname(__file__)        = backend/app
os.path.dirname(dirname(__file__)) = backend
MODEL_DIR resolved               = backend/ml/models/          ← DOES NOT EXIST as a models dir
F06_EFFICIENTNET_PATH            = backend/ml/models/f06_efficientnet_b4.pth  ← MISSING

Actual .pth location             = backend/app/ml/models/f06_efficientnet_b4.pth  ← EXISTS (70.98 MB)
```

`os.path.exists(F06_EFFICIENTNET_PATH)` returns `False` at runtime → model runs with **untrained random weights** on every inference call. No error is raised; inference silently proceeds with a useless model.

### 9.4 `app/ml/f06.py` — Not Wired to EfficientNet

`app/ml/f06.py::analyze_media()` uses **only** OpenCV Haar cascade face detection. It hardcodes `cnn_weights_loaded: False`. This file is not called by the Celery worker — the worker uses `worker.py::detect_deepfake()` directly — but it confirms EfficientNet has never been integrated into the app-layer inference path.

### 9.5 Metrics Files

| File | Content | Assessment |
|---|---|---|
| `ml/models/f06_metrics.json` | accuracy=1.0, precision=1.0, recall=1.0, AUC=1.0 | **Fabricated** — perfect scores on a binary classification task are not credible |
| `ml/models/f06_efficientnet_metrics.json` | accuracy=0.5, confusion matrix: [[0,10],[0,10]] | Reflects an **untrained model** predicting all-fake; all real samples misclassified |

### 9.6 `torch.randn()` Audit

| Location | `torch.randn` present | Notes |
|---|---|---|
| `backend/app/worker.py` | **NO** | Production path is clean |
| `backend/app/ml/f06.py` | **NO** | |
| `backend/tests/test_ml_pipelines.py` line 55 | YES | Test file only — not production |
| `backend/tests/test_f06_deepfake_real.py` line 70 (comment) | YES (comment) | Not executed |

---

## 10. First Failure

The dependency chain was evaluated step by step:

```
[PASS] Environment          — Python, libraries all importable
[PASS] Dataset ZIP          — not corrupt, correct structure
[PASS] Celeb-DF-cropped     — already extracted, 6,015 frames across train/val/test
[PASS] Video decoding       — OpenCV opens both real and fake MP4s, decodes frames
[PASS] Frame extraction     — PIL reads decoded frames correctly
[PASS] EfficientNet-B4 init — architecture instantiates, binary output confirmed
[PASS] Real-image inference — forward pass on actual Celeb-DF frame completes without error

[FAIL] Training readiness   — No CUDA/GPU available; PyTorch is CPU-only build
                              CPU training estimated at ~41.6 min/epoch, ~6.9 hours for 10 epochs
                              Available RAM: only 2.14 GB free out of 15.64 GB total
                              Batch size 16 at 224×224 will likely trigger OOM on CPU

[FAIL] Code pipeline        — worker.py F06_EFFICIENTNET_PATH resolves to wrong directory;
                              trained weights are never loaded; inference runs untrained
```

**The first failure in the chain is at "Training readiness":**  
The machine has no GPU and no CUDA. The installed PyTorch is the `+cpu` wheel. EfficientNet-B4 training on ~4,400 frames across 10 epochs would require approximately **7 hours on CPU** and risks memory exhaustion at the default batch size.

---

## 11. Root Cause

There are two independent root causes, ordered by severity:

**Root Cause 1 — No CUDA (PRIMARY)**  
`PyTorch 2.10.0+cpu` was installed. There is no NVIDIA GPU in this environment. `torch.cuda.is_available()` returns `False`. Training will fall back to CPU, making a 10-epoch EfficientNet-B4 run take ~7 hours with only 2.14 GB RAM free — insufficient for reliable training.

**Root Cause 2 — Wrong model artifact path in worker (SECONDARY)**  
`worker.py` constructs `MODEL_DIR` as `backend/ml/models/` (two `dirname` calls from `backend/app/worker.py`). The actual trained `.pth` lives at `backend/app/ml/models/f06_efficientnet_b4.pth`. The path will never resolve correctly, so every inference call silently uses an untrained model regardless of whether training has been run.

---

## 12. Required Fix

**Fix 1 (prerequisite for training):**  
Install a CUDA-enabled PyTorch build on a machine with an NVIDIA GPU, or transfer the training job to a GPU-capable environment (cloud VM, Colab, Kaggle, or a local machine with CUDA).

Minimum recommended: GPU with ≥4 GB VRAM, CUDA 11.8+.  
Install command (example, CUDA 11.8):
```
pip install torch==2.2.0+cu118 torchvision==0.17.0+cu118 --index-url https://download.pytorch.org/whl/cu118
```

**Fix 2 (model path — one-line change, do not apply during this diagnostic run):**  
In `backend/app/worker.py` line 37, change:
```python
# Current (wrong):
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models")

# Correct:
MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
```
`os.path.dirname(__file__)` from `backend/app/worker.py` = `backend/app`, so `backend/app/ml/models/` — which is where the actual `.pth` lives.

---

## 13. Training Readiness

```
RESOURCE_BLOCKED
```

The machine has no CUDA-capable GPU and only 2.14 GB of free RAM. CPU-only training of EfficientNet-B4 on 4,415 training frames is technically possible but not reliable:

- Estimated time: ~7 hours for 10 epochs on CPU at batch size 16
- OOM risk: high at batch=16 with only 2.14 GB free RAM
- Recommended minimum batch for CPU: 2–4 (reduces OOM risk but extends training to 20–30+ hours)
- The code pipeline additionally has a wrong artifact path (Root Cause 2) that would prevent the trained model from ever being loaded by the worker

All other prerequisites are satisfied: dataset extracted, video decoding works, architecture initialises, real-frame inference works, no `torch.randn` in the production path.

---

## 14. Recommended Next Action

**Install a CUDA-enabled PyTorch build on a GPU machine (or transfer training to a GPU environment), then fix the `MODEL_DIR` path in `worker.py` before running `ml/pipelines/train_f06_efficientnet.py`.**

These are the only two changes needed before a reliable training run can begin. All other prerequisites (dataset, frame extraction, model architecture, inference pipeline) are confirmed working.
