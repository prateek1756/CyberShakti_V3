# F-06 GPU Readiness Report

**Date:** 2026-08-21  
**Scope:** Environment verification only. No training performed. No source code modified.

---

## Environment

| Property | Value |
|---|---|
| Operating System | Windows 11 Home (Build 26200) |
| Python version | 3.14.1 (CPython 64-bit, MSC v.1944) |
| Python executable | `C:\Python314\python.exe` |
| PyTorch version | **2.10.0+cpu** |
| torchvision version | **0.25.0+cpu** |
| PyTorch build type | CPU-only (`+cpu` suffix — no CUDA compiled in) |
| `torch.version.cuda` | `None` |
| `torch.cuda.is_available()` | **False** |

---

## GPU

| Property | Value |
|---|---|
| GPU detected by OS | **YES** |
| GPU name | NVIDIA GeForce RTX 3050 6GB Laptop GPU |
| VRAM total | 6,144 MB (6.0 GB) |
| VRAM in use at check | 159 MB (by Kiro IDE / desktop) |
| VRAM free | ~5,985 MB (~5.84 GB) |
| NVIDIA driver version | 610.88 |
| Detection method | `nvidia-smi` — confirmed hardware present |
| WMI confirmed | YES — `Win32_VideoController` returns RTX 3050 with driver 32.0.16.1088 |

---

## CUDA

| Property | Value |
|---|---|
| CUDA UMD version (nvidia-smi) | 13.3 |
| CUDA Toolkit installed | **NO** — `nvcc` not found, `CUDA_PATH` not set |
| `torch.cuda.is_available()` | **False** |
| Reason CUDA unavailable to PyTorch | PyTorch was installed as the CPU-only wheel (`torch==2.10.0+cpu`). The CUDA runtime is not compiled into this build. The GPU exists at the hardware level but PyTorch cannot dispatch to it. |

---

## Dataset

Location: `D:\dataset\Celeb-DF-cropped\`

| Split | Real frames | Fake frames | Total |
|---|---|---|---|
| train | 1,480 | 2,935 | 4,415 |
| val | 370 | 730 | 1,100 |
| test | 190 | 310 | 500 |
| **Grand total** | **2,040** | **3,975** | **6,015** |

Class imbalance ratio (fake : real): approximately 2:1 across all splits.  
All splits are present and populated. Dataset is ready for training.

Original ZIP: `D:\dataset\Celeb-DF.zip` (1.976 GB, integrity verified in prior diagnostic).

---

## EfficientNet-B4 CUDA Test

| Check | Result | Detail |
|---|---|---|
| Architecture instantiated | YES | `DeepfakeEfficientNetDetector` from `ml/pipelines/train_f06_efficientnet.py` |
| Trained weights loaded | YES | `backend/app/ml/models/f06_efficientnet_b4.pth` — 70.98 MB, 706 keys (path fix confirmed working) |
| Model on CPU | YES | `next(model.parameters()).device` → `cpu` |
| `model.cuda()` attempted | **SKIPPED** | `torch.cuda.is_available()` returns `False` — call would raise `AssertionError: Torch not compiled with CUDA enabled` |
| Model on CUDA | **NO** | Blocked by CPU-only PyTorch wheel |

---

## Real Image Inference Test

Source video: `Celeb-real/id0_0000.mp4` (from `D:\dataset\Celeb-DF.zip`)  
This is an actual Celeb-DF video. No synthetic data, no `torch.randn()`.

| Step | Result | Detail |
|---|---|---|
| Frame extracted from ZIP | YES | OpenCV decoded frame 0 — shape (500, 942, 3) |
| Frame saved | YES | `D:\dataset\_diag_tmp\gpu_test_frame.png` |
| PIL load | YES | RGB, 942×500 |
| Preprocessing | YES | `Resize(224,224) → ToTensor → Normalize(ImageNet)` |
| Input tensor shape | `[1, 3, 224, 224]` | `torch.float32` |
| Input tensor device | `cpu` | CUDA move skipped — no CUDA in PyTorch |
| Model device | `cpu` | |
| Forward pass | **YES — completed on CPU** | |
| Output shape | `[1, 2]` | Binary classifier output |
| Softmax probabilities | `[0.4993, 0.5007]` | Expected near-50/50 from the current model state |
| Inference on CUDA | **NO** | Cannot test — PyTorch has no CUDA support |

The forward pass completed successfully on CPU. CUDA inference could not be tested because the installed PyTorch wheel has no CUDA compiled in.

---

## Resource Assessment

| Resource | Available | Required for training | Status |
|---|---|---|---|
| GPU | RTX 3050 6GB — **hardware present** | ≥4 GB VRAM recommended | Hardware OK |
| PyTorch CUDA support | **None** (CPU-only wheel) | CUDA-enabled wheel required | **BLOCKED** |
| CUDA Toolkit | **Not installed** | Not strictly required (pre-built wheels bundle runtime) | Informational |
| System RAM | 15.64 GB total, 2.34 GB free | ~8 GB free recommended for batch=16 | Marginal |
| Disk (D:) | 91.37 GB free | ~5–10 GB for checkpoints and logs | OK |
| Dataset | 6,015 face-cropped frames, train/val/test split ready | Present | OK |
| Model artifact | `f06_efficientnet_b4.pth` (70.98 MB) | Present | OK |
| Training script | `ml/pipelines/train_f06_efficientnet.py` | Present | OK |

The only blocker is the PyTorch installation. Everything else — GPU hardware, dataset, model architecture, training script, artifact path — is in place.

**Required action before training can begin:**

Uninstall the CPU-only wheel and install a CUDA-enabled build. The GPU's CUDA UMD reports version 13.3 (driver 610.88 supports CUDA up to 12.x via the stable toolkit). Install the PyTorch CUDA 12.1 or CUDA 12.4 wheel:

```
pip uninstall torch torchvision -y
pip install torch==2.10.0+cu121 torchvision==0.25.0+cu121 --index-url https://download.pytorch.org/whl/cu121
```

After reinstalling, verify with:

```python
import torch
print(torch.cuda.is_available())        # must be True
print(torch.cuda.get_device_name(0))    # must show RTX 3050
```

---

## Training Readiness

```
GPU_BLOCKED
```

**Reason:** The NVIDIA RTX 3050 6GB Laptop GPU is physically present and fully functional (confirmed by `nvidia-smi`, ~5.98 GB VRAM free). However, the installed PyTorch is the `+cpu` wheel (`2.10.0+cpu`). `torch.cuda.is_available()` returns `False`. EfficientNet-B4 cannot be moved to CUDA and training cannot use the GPU until the CUDA-enabled PyTorch wheel is installed.

All other prerequisites are satisfied. The single required fix is replacing `torch==2.10.0+cpu` with `torch==2.10.0+cu121` (or equivalent CUDA 12.x build).
