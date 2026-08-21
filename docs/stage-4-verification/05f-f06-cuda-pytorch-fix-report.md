# CyberShakti V3 — F-06 CUDA PyTorch Fix Report

**Date:** 2026-08-21  
**Scope:** Replace CPU-only PyTorch with CUDA-enabled build and verify GPU inference  
**Status:** COMPLETE

---

## 1. Previous Environment

| Property | Value |
|---|---|
| Python | 3.14.1 (CPython 64-bit) |
| torch (before) | 2.10.0+cpu |
| torchvision (before) | 0.25.0+cpu |
| `torch.version.cuda` | `None` |
| `torch.cuda.is_available()` | `False` |
| Root cause | CPU-only wheel installed — no CUDA compiled in despite GPU hardware being present |

---

## 2. GPU Hardware

| Property | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 3050 6GB Laptop GPU |
| NVIDIA driver | 610.88 |
| CUDA UMD (nvidia-smi) | 13.3 |
| VRAM total | 6,144 MB (6.00 GB) |
| CUDA compute capability | 8.6 (Ampere) |
| SM count | 20 |
| Hardware status | Confirmed present and functional before installation |

---

## 3. Selected PyTorch Build

**Why no standard `+cu121`/`+cu124` wheel?**  
PyTorch does not publish traditional CUDA-suffixed wheels (`+cu121`, `+cu124`) for Python 3.14 on PyPI or the standard download index. This was confirmed by inspecting the `cp314-win_amd64` entries across the `cu118`, `cu121`, `cu124`, and `cu128` indices — none existed for those CUDA versions.

PyTorch 2.10 introduced **wheel variants** (PEP-817) and simultaneously published `cu128` wheels for Python 3.14 via `uv --torch-backend`. These are official PyTorch wheels, not third-party builds.

**Wheel selection process:**

```
# Dry run to confirm availability before installing
uv pip install torch torchvision --system --dry-run --torch-backend=cu128
# Result: torch==2.11.0+cu128, torchvision==0.26.0+cu128 (resolved)

# Python version constraint check on metadata:
# torch==2.10.0+cu128   Requires-Python: >=3.10         ← no 3.14.1 exclusion
# torch==2.11.0+cu128   Requires-Python: >=3.10         ← no 3.14.1 exclusion
# torchvision==0.25.0+cu128  Requires-Python: >=3.10    ← no 3.14.1 exclusion
# torchvision==0.26.0+cu128  Requires-Python: >=3.10,!=3.14.1  ← EXCLUDED Python 3.14.1
#
# torchvision==0.25.0+cu128 requires torch==2.10.0 exactly
# Final compatible pair: torch==2.10.0+cu128 + torchvision==0.25.0+cu128
```

| Property | Value |
|---|---|
| Selected torch | `torch==2.10.0+cu128` |
| Selected torchvision | `torchvision==0.25.0+cu128` |
| CUDA version built against | 12.8 |
| Driver compatibility | Driver 610.88 supports CUDA up to 13.3 — CUDA 12.8 is fully compatible |
| Python compatibility | `Requires-Python: >=3.10` — no exclusion for 3.14.1 |
| Source index | `https://download.pytorch.org/whl/cu128` (official PyTorch) |

---

## 4. Installation

**Step 1 — Remove CPU-only packages:**

```
pip uninstall torch torchvision -y
```

Result: `Successfully uninstalled torch-2.10.0` and `Successfully uninstalled torchvision-0.25.0`

**Step 2 — Install CUDA-enabled build:**

```
pip install torch==2.10.0+cu128 torchvision==0.25.0+cu128 \
  --index-url https://download.pytorch.org/whl/cu128 --no-cache-dir
```

Result: `Successfully installed torch-2.10.0+cu128 torchvision-0.25.0+cu128`

**Dependency conflict (non-blocking):**  
`open-mythos==0.5.0` requires `torch==2.11.0`. This package is unrelated to CyberShakti. The conflict does not affect any CyberShakti component.

**Install location:** `C:\Users\Prateek\AppData\Roaming\Python\Python314\site-packages`

---

## 5. CUDA Verification

Verified with `python -c "import torch; ..."` after installation:

| Check | Command | Result |
|---|---|---|
| torch version | `torch.__version__` | **2.10.0+cu128** |
| torchvision version | `torchvision.__version__` | **0.25.0+cu128** |
| CUDA version | `torch.version.cuda` | **12.8** |
| CUDA available | `torch.cuda.is_available()` | **True** |
| Device count | `torch.cuda.device_count()` | **1** |
| Current device | `torch.cuda.current_device()` | **0** |
| Device name | `torch.cuda.get_device_name(0)` | **NVIDIA GeForce RTX 3050 6GB Laptop GPU** |
| VRAM total | `get_device_properties(0).total_memory` | **6.00 GB** |
| VRAM free | `torch.cuda.mem_get_info(0)[0]` | **5.04 GB** |
| CUDA compute cap | `properties.major.minor` | **8.6** |
| SM count | `properties.multi_processor_count` | **20** |

**Small CUDA tensor test:**

```python
t = torch.tensor([1.0, 2.0, 3.0], device="cuda:0")
# device: cuda:0  dtype: torch.float32  values: [1.0, 2.0, 3.0]
# t * 2 → [2.0, 4.0, 6.0]  ← PASS
```

---

## 6. EfficientNet-B4 CUDA Verification

| Check | Result |
|---|---|
| Model class | `DeepfakeEfficientNetDetector` (`ml/pipelines/train_f06_efficientnet.py`) |
| Artifact path | `backend/app/ml/models/f06_efficientnet_b4.pth` |
| Artifact exists | **YES** (70.98 MB, 706 state dict keys) |
| Weights loaded | **YES** — `model.load_state_dict(sd)` — no key mismatches |
| Model moved to CUDA | `model.cuda()` — **YES** |
| Model device confirmed | `next(model.parameters()).device` → **cuda:0** |

---

## 7. Real Celeb-DF Image CUDA Inference

**Input source:** `D:\dataset\Celeb-DF-cropped\train\real\real_0_id9_0006_frame_0.jpg`  
This is a face-cropped frame from the real Celeb-DF dataset. No `torch.randn()`, no synthetic data.

| Step | Result |
|---|---|
| Frame file size | 12,090 bytes (11.8 KB) |
| PIL load | YES — RGB, 224×224 |
| Preprocessing | `Resize(224,224) → ToTensor → Normalize(ImageNet)` |
| CPU tensor shape | `[1, 3, 224, 224]` — `torch.float32` |
| Move to CUDA | `tensor.to("cuda:0")` — **YES** |
| Input tensor device | **cuda:0** |
| Model device | **cuda:0** |
| Forward pass | **COMPLETED** — no exception |
| Output device | **cuda:0** |
| Output shape | `[1, 2]` |
| Raw logits | `[[0.00175099, 0.00441546]]` |
| Softmax probabilities | `[[0.4993, 0.5007]]` (class 0 = real, class 1 = fake) |
| VRAM used after inference | **1,114.5 MB** (~18.6% of 6 GB) |
| VRAM remaining | ~4.93 GB free — ample headroom for training batch sizes |

Note: near-50/50 probabilities are expected from the current model state. The existing `.pth` artifact reflects an incompletely trained checkpoint (per the diagnostic report). These probabilities confirm real forward pass execution, not a hardcoded result.

---

## 8. Final Environment

| Property | Value |
|---|---|
| OS | Windows 11 Home (Build 26200) |
| Python | 3.14.1 |
| torch | **2.10.0+cu128** |
| torchvision | **0.25.0+cu128** |
| `torch.version.cuda` | **12.8** |
| `torch.cuda.is_available()` | **True** |
| GPU | NVIDIA GeForce RTX 3050 6GB Laptop GPU |
| VRAM total | 6.00 GB |
| VRAM free at idle | ~5.04 GB |
| VRAM used by inference | ~1.1 GB |
| timm | 1.0.27 (unchanged, compatible) |
| numpy | 2.3.5 (unchanged) |
| Pillow | 12.0.0 (unchanged) |
| OpenCV | 4.13.0 (unchanged) |

No CyberShakti source files were modified. No model architecture was changed. No database was touched.

---

## 9. Training Readiness

```
GPU_READY
```

All prerequisites are now satisfied:

| Requirement | Status |
|---|---|
| GPU hardware | NVIDIA RTX 3050 6GB — confirmed |
| CUDA-enabled PyTorch | `torch==2.10.0+cu128` — installed and verified |
| `torch.cuda.is_available()` | **True** |
| EfficientNet-B4 on cuda:0 | **Confirmed** |
| Real Celeb-DF CUDA inference | **Completed successfully** |
| VRAM headroom | ~4.93 GB free — supports batch size 16 at 224×224 |
| Dataset (Celeb-DF-cropped) | 6,015 frames across train/val/test — ready |
| Training script | `ml/pipelines/train_f06_efficientnet.py` — present |
| Model artifact path | `backend/app/ml/models/f06_efficientnet_b4.pth` — resolves correctly (path fix applied) |

---

## 10. Remaining Issues

**Minor:**

1. **`open-mythos` dependency conflict** — `open-mythos==0.5.0` requires `torch==2.11.0` exactly. This package is not part of CyberShakti. If it needs to be used alongside this environment, upgrading to `torch==2.11.0+cu128` + `torchvision==0.25.0+cu128` (checking the `!=3.14.1` exclusion is resolved in a later torchvision patch) would resolve it. Not a blocker for F-06.

2. **Existing `.pth` metrics are not from real training** — The `f06_efficientnet_metrics.json` shows `accuracy=0.5` and an all-zero confusion matrix for real samples. The model weights in `f06_efficientnet_b4.pth` appear to be from an incomplete training run. GPU training on Celeb-DF is now unblocked and should produce a genuinely trained model with real metrics.

3. **`torchscripts.exe` / `torchrun.exe` not on PATH** — pip warned these scripts are in a user Scripts folder not on PATH. Not required for training via `python ml/pipelines/train_f06_efficientnet.py`.
