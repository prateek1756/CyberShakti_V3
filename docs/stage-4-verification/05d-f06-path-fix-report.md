# CyberShakti V3 — F-06 Model Path Fix Report

**Date:** 2026-08-21  
**Scope:** Fix only — correct `MODEL_DIR` path in `backend/app/worker.py`  
**Status:** COMPLETE

---

## File Changed

`backend/app/worker.py` — line 33

---

## Exact Issue

`worker.py` constructed `MODEL_DIR` using two `os.path.dirname()` calls:

```python
# BEFORE (broken)
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models")
```

Path resolution trace:

```
__file__                              = backend/app/worker.py
os.path.dirname(__file__)             = backend/app
os.path.dirname(os.path.dirname(...)) = backend          ← one too many
MODEL_DIR resolved to                 = backend/ml/models/
```

`backend/ml/models/` does not exist. As a result `os.path.exists(F06_EFFICIENTNET_PATH)` always returned `False`, so the `detect_deepfake` Celery task silently skipped loading the trained weights and ran inference with a randomly-initialised model on every call. The same wrong path affected F-02, F-05, and F-07 model loading at worker startup.

---

## Correction Made

Removed one `os.path.dirname()` call:

```python
# AFTER (correct)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
```

Path resolution trace:

```
__file__                  = backend/app/worker.py
os.path.dirname(__file__) = backend/app
MODEL_DIR resolved to     = backend/app/ml/models/   ← correct
```

`backend/app/ml/models/` exists and contains all model artifacts.

This is the only line changed. No other code, architecture, routes, database, or frontend files were modified.

---

## Verification Result

Path resolution verified by simulating `worker.py`'s import-time evaluation with `__file__` set to its actual on-disk location:

| Path constant | Resolved path | Exists |
|---|---|---|
| `MODEL_DIR` | `backend/app/ml/models/` | **YES** |
| `F02_MODEL_PATH` | `backend/app/ml/models/f02_scam_text_pipeline.joblib` | **YES** |
| `F02_DISTILBERT_DIR` | `backend/app/ml/models/distilbert_scam/` | **YES** |
| `F05_MODEL_PATH` | `backend/app/ml/models/f05_fake_profile_model.joblib` | **YES** |
| `F06_EFFICIENTNET_PATH` | `backend/app/ml/models/f06_efficientnet_b4.pth` | **YES** (70.98 MB) |
| `F07_MODEL_PATH` | `backend/app/ml/models/f07_mule_account_model.joblib` | **YES** |

Worker line 33 as written in the file after the fix:

```
MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
```

---

## Tests Executed

7 tests run against `backend/app/worker.py` and `ml/pipelines/train_f06_efficientnet.py`.

| # | Test | Result | Notes |
|---|---|---|---|
| T1 | `MODEL_DIR` resolves to `backend/app/ml/models/` | **PASS** | Exact string match + `os.path.isdir()` |
| T2 | `f06_efficientnet_b4.pth` exists and is >1 MB | **PASS** | 70.98 MB confirmed |
| T3 | State dict loads into `DeepfakeEfficientNetDetector` | **PASS** | 706 keys, no mismatches, 2 output classes |
| T4 | Real image inference produces valid [0,1] probability | **FAIL** | Pre-existing test-script issue (see below) |
| T5 | Different inputs produce different outputs | **FAIL** | Pre-existing test-script issue (see below) |
| T6 | Worker `_preprocess_image_for_efficientnet` produces (1,3,224,224) tensor | **PASS** | dtype=float32 confirmed |
| T7 | Worker `detect_deepfake` end-to-end returns valid verdict | **PASS** | `anomaly_score` in [0,1], `risk_level` valid |

**5 passed, 2 failed.**

### T4 and T5 failure explanation

Both failures produce:

```
RuntimeError: expected scalar type Double but found Float
```

Root cause: the test scripts construct image tensors using `np.array(img) / 255.0` without `dtype=np.float32`. Under NumPy 2.x (installed: 2.3.5) this produces a `float64` array, which becomes a `torch.float64` (Double) tensor, mismatching the model's `float32` parameters.

This is a **pre-existing bug in the test scripts themselves**, not in the worker code. `worker.py::_preprocess_image_for_efficientnet` explicitly uses `np.array(img, dtype=np.float32)` throughout and is unaffected. T6 and T7 — which exercise the actual worker code path — both pass.

T4 and T5 require a separate fix: add `dtype=np.float32` to the `np.array()` calls in `test_f06_deepfake_real.py`. That fix is out of scope for this task.

### Tests that directly validate the path fix

T6 and T7 are the tests most directly relevant to the path fix:

- **T6** confirms `_preprocess_image_for_efficientnet` reads a real file from disk and returns a correctly-shaped float32 tensor — proving the worker-side file I/O path is functional.
- **T7** runs the full `detect_deepfake` worker task end-to-end with a real PNG file, confirming the trained `.pth` is now found and loaded (`os.path.exists(F06_EFFICIENTNET_PATH)` returns `True`), and that inference produces a valid `anomaly_score` in [0.0, 1.0] with a valid `risk_level` in the response.

Both pass.

---

## Summary

The one-line change to `worker.py` corrects the model directory path for all Celery workers. After the fix, `F06_EFFICIENTNET_PATH` resolves to the existing `f06_efficientnet_b4.pth` artifact (70.98 MB). The `detect_deepfake` task will now load the trained weights rather than silently running with a randomly-initialised model.

F-06 is not claimed as production-ready. Training on a GPU-capable environment remains required before the model produces meaningful predictions.
