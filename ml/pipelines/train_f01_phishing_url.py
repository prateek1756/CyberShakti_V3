"""
Production F-01 Phishing URL Model Training Pipeline.
Trains a native XGBoost classifier on the real uploaded datasets:
- 'Phishing URLs.csv' (54,807 URLs)
- 'URL dataset.csv' (450,176 URLs: 345,738 legitimate, 104,438 phishing)

Performs data normalization:
- Non-www domain variants for legitimate domains to prevent domain prefix bias
- Stratified sampling with held-out test split (80/10/10)
- Serializes trained XGBoost model and metrics
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.detect_analyze.url import NUMERIC_FEATURE_ORDER, extract_url_features, feature_vector

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def load_and_preprocess_datasets(sample_size_per_class: int = 40000) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    print("[*] Loading uploaded CSV datasets: 'Phishing URLs.csv' and 'URL dataset.csv'...")
    t0 = time.perf_counter()

    # 1. Load Phishing URLs.csv
    phish_path = ROOT / "Phishing URLs.csv"
    if not phish_path.is_file():
        raise FileNotFoundError(f"Missing {phish_path}")
    df_phish = pd.read_csv(phish_path)
    phish_urls_1 = df_phish["url"].dropna().astype(str).tolist()

    # 2. Load URL dataset.csv
    url_dataset_path = ROOT / "URL dataset.csv"
    if not url_dataset_path.is_file():
        raise FileNotFoundError(f"Missing {url_dataset_path}")
    df_url = pd.read_csv(url_dataset_path)
    legit_raw = df_url[df_url["type"].str.lower() == "legitimate"]["url"].dropna().astype(str).tolist()
    phish_urls_2 = df_url[df_url["type"].str.lower() == "phishing"]["url"].dropna().astype(str).tolist()

    # Normalize legitimate URLs (include non-www variants to eliminate domain prefix bias)
    legit_clean = []
    for u in legit_raw:
        legit_clean.append(u)
        if "://www." in u:
            legit_clean.append(u.replace("://www.", "://"))

    all_phish = list(set(phish_urls_1 + phish_urls_2))
    all_legit = list(set(legit_clean))

    print(f"[+] Total Available Unique Phishing URLs: {len(all_phish):,}")
    print(f"[+] Total Available Unique Legitimate URLs: {len(all_legit):,}")

    random.shuffle(all_phish)
    random.shuffle(all_legit)

    sampled_phish = all_phish[:min(sample_size_per_class, len(all_phish))]
    sampled_legit = all_legit[:min(sample_size_per_class, len(all_legit))]

    urls = sampled_legit + sampled_phish
    labels = [0] * len(sampled_legit) + [1] * len(sampled_phish)

    combined = list(zip(urls, labels))
    random.shuffle(combined)
    urls, labels = zip(*combined)

    print(f"[*] Extracting 19 lexical & structural features for {len(urls):,} balanced URLs...")
    t_feat_start = time.perf_counter()

    features_list = []
    for i, u in enumerate(urls):
        try:
            feats = extract_url_features(u)
            vec = feature_vector(feats)
            features_list.append(vec)
        except Exception:
            features_list.append([0.0] * len(NUMERIC_FEATURE_ORDER))

        if (i + 1) % 10000 == 0 or (i + 1) == len(urls):
            print(f"    Processed {i+1:,}/{len(urls):,} URLs ({((i+1)/(time.perf_counter() - t_feat_start)):.1f} URLs/sec)...")

    t_total = time.perf_counter() - t0
    print(f"[OK] Feature extraction complete in {t_total:.2f}s.")

    meta = {
        "total_phishing_pool": len(all_phish),
        "total_legitimate_pool": len(all_legit),
        "sampled_phishing": len(sampled_phish),
        "sampled_legitimate": len(sampled_legit),
        "total_samples": len(urls),
    }

    return np.array(features_list, dtype=np.float32), np.array(labels, dtype=np.int32), meta


def train_f01_production_model(sample_size_per_class: int = 40000):
    print("================================================================")
    print("=== Training F-01 Phishing URL Model on Uploaded CSV Datasets ===")
    print("================================================================")

    X, y, data_meta = load_and_preprocess_datasets(sample_size_per_class)

    print("[*] Splitting dataset into Train (80%), Validation (10%), Test (10%)...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=SEED, stratify=y_temp
    )

    print(f"[+] Train set: {len(X_train):,} samples ({int(y_train.sum()):,} Phishing, {len(y_train) - int(y_train.sum()):,} Legit)")
    print(f"[+] Val set:   {len(X_val):,} samples")
    print(f"[+] Test set:  {len(X_test):,} samples")

    print("[*] Initializing and training native XGBoost Classifier...")
    t_train_start = time.perf_counter()

    xgb_model = XGBClassifier(
        n_estimators=160,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=SEED,
        n_jobs=-1,
    )

    xgb_model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=20,
    )
    t_train = time.perf_counter() - t_train_start
    print(f"[OK] XGBoost training finished in {t_train:.2f}s.")

    print(f"[*] Evaluating model on held-out test set ({len(X_test):,} samples)...")
    y_pred = xgb_model.predict(X_test)
    y_prob = xgb_model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

    metrics = {
        "model": "XGBoost",
        "version": "native-v3-csv-trained",
        "datasets_used": ["Phishing URLs.csv", "URL dataset.csv"],
        "dataset_metadata": data_meta,
        "features": NUMERIC_FEATURE_ORDER,
        "feature_count": len(NUMERIC_FEATURE_ORDER),
        "split": "80/10/10 stratified",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "n_test": int(len(y_test)),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "false_positive_rate": round(float(fp / (fp + tn)), 4) if (fp + tn) > 0 else 0.0,
            "false_negative_rate": round(float(fn / (fn + tp)), 4) if (fn + tp) > 0 else 0.0,
            "confusion_matrix": {
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp),
            }
        },
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    print("\n=== Model Performance Evaluation on Held-Out Test Set ===")
    print(f"Accuracy:            {acc * 100:.2f}%")
    print(f"Precision:           {prec * 100:.2f}%")
    print(f"Recall:              {rec * 100:.2f}%")
    print(f"F1-Score:            {f1 * 100:.2f}%")
    print(f"ROC-AUC:             {roc_auc:.4f}")
    print(f"Confusion Matrix:    TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print(f"False Positive Rate: {metrics['metrics']['false_positive_rate'] * 100:.2f}%")

    target_dirs = [
        ROOT / "backend" / "app" / "ml" / "models",
        ROOT / "backend" / "ml" / "artefacts",
        ROOT / "ml" / "models",
    ]

    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)
        joblib.dump(xgb_model, d / "f01_phishing_url_model.joblib")
        (d / "f01_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        if d.name == "artefacts":
            joblib.dump(xgb_model, d / "f01_xgboost.joblib")

    print("\n[OK] Serialized trained model to:", [str(d / "f01_phishing_url_model.joblib") for d in target_dirs])
    return metrics


if __name__ == "__main__":
    train_f01_production_model(sample_size_per_class=150000)
