"""
train_f07_indian_bank.py
------------------------
Retrains F-07 XGBoost mule account model on synthetic Indian bank transaction data.
Resolves ADR-024 (Elliptic domain mismatch).

Dataset design is based on:
- RBI/FIU-IND typologies for domestic mule accounts
- NPCI UPI fraud patterns (burst transfers, smurfing thresholds)
- cybercrime.gov.in case categories (job-scam mules, romance-scam money carriers)

Run from backend/ directory:
    python ml/pipelines/train_f07_indian_bank.py

Outputs:
    ml/artefacts/f07_xgboost.joblib              <- trained model
    ml/artefacts/f07_metrics.json                <- evaluation report
    app/ml/models/f07_mule_account_model.joblib  <- copied for inference
    app/ml/models/f07_metrics.json               <- copied for inference
"""

from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

import joblib
import numpy as np
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

ROOT = Path(__file__).resolve().parents[2]          # backend/
ARTEFACTS = ROOT / "ml" / "artefacts"
MODEL_DEST = ROOT / "app" / "ml" / "models"

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Feature order must match f07.py:tabular_features() exactly ──────────────
# [account_age_days, inbound_txn_count, outbound_txn_count,
#  rapid_fund_pass_through, degree_centrality, clustering_coefficient,
#  betweenness_centrality, node_count, edge_count]

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _uniform(lo: float, hi: float) -> float:
    return random.uniform(lo, hi)


def generate_mule_account() -> list[float]:
    """
    MULE_ACCOUNT (label=1):
    New account recruited via job/investment scam.
    Funds arrive from multiple victims, leave same day to aggregator/ATM.
    Indian UPI mule: age < 90 days, rapid pass-through, high betweenness.
    """
    age = _uniform(5, 90)
    in_count = int(_uniform(3, 25))
    out_count = int(_uniform(2, min(in_count + 3, 22)))
    pass_through = 1.0                         # always — funds in/out same day
    deg = _clamp(_uniform(0.30, 0.90), 0, 1)
    clust = _clamp(_uniform(0.00, 0.20), 0, 1) # pass-through nodes don't cluster
    btw = _clamp(_uniform(0.30, 0.95), 0, 1)   # high — sits on critical paths
    n_nodes = int(_uniform(4, 20))
    n_edges = int(_uniform(max(3, n_nodes - 2), n_nodes + 8))
    return [
        _clamp(age + random.gauss(0, 2), 1, 180),
        float(in_count),
        float(out_count),
        pass_through,
        _clamp(deg + random.gauss(0, 0.03), 0, 1),
        _clamp(clust + random.gauss(0, 0.02), 0, 1),
        _clamp(btw + random.gauss(0, 0.04), 0, 1),
        float(n_nodes),
        float(n_edges),
    ]


def generate_layering_hub() -> list[float]:
    """
    LAYERING_HUB / Aggregator (label=1):
    Slightly older account. Aggregates from multiple mule accounts,
    fans out to crypto exchange / ATM withdrawal chain.
    Very high betweenness (sits at convergence point).
    """
    age = _uniform(30, 180)
    in_count = int(_uniform(5, 40))
    out_count = int(_uniform(2, 15))
    pass_through = 1.0
    deg = _clamp(_uniform(0.50, 0.95), 0, 1)
    clust = _clamp(_uniform(0.00, 0.15), 0, 1)
    btw = _clamp(_uniform(0.50, 0.99), 0, 1)  # highest — central aggregator
    n_nodes = int(_uniform(6, 30))
    n_edges = int(_uniform(n_nodes, n_nodes + 15))
    return [
        _clamp(age + random.gauss(0, 5), 5, 365),
        float(in_count),
        float(out_count),
        pass_through,
        _clamp(deg + random.gauss(0, 0.03), 0, 1),
        _clamp(clust + random.gauss(0, 0.02), 0, 1),
        _clamp(btw + random.gauss(0, 0.03), 0, 1),
        float(n_nodes),
        float(n_edges),
    ]


def generate_smurfing_account() -> list[float]:
    """
    SMURFING / Structuring (label=1):
    Account receives many small deposits (< Rs50k each) to avoid AML thresholds.
    High inbound count, few large withdrawals, moderate betweenness.
    """
    age = _uniform(10, 120)
    in_count = int(_uniform(10, 50))   # many small deposits
    out_count = int(_uniform(1, 8))    # few large withdrawals
    pass_through = random.choice([0.0, 1.0])
    deg = _clamp(_uniform(0.20, 0.70), 0, 1)
    clust = _clamp(_uniform(0.00, 0.25), 0, 1)
    btw = _clamp(_uniform(0.20, 0.70), 0, 1)
    n_nodes = int(_uniform(5, 25))
    n_edges = int(_uniform(n_nodes, n_nodes + 20))
    return [
        _clamp(age + random.gauss(0, 3), 1, 180),
        float(in_count),
        float(out_count),
        pass_through,
        _clamp(deg + random.gauss(0, 0.03), 0, 1),
        _clamp(clust + random.gauss(0, 0.02), 0, 1),
        _clamp(btw + random.gauss(0, 0.04), 0, 1),
        float(n_nodes),
        float(n_edges),
    ]


def generate_legit_salary_account() -> list[float]:
    """
    LEGIT — Salary/Savings Account (label=0):
    Old account (> 6 months), regular salary credit once/month,
    bill payments and UPI spends. Low betweenness (not on critical paths).
    """
    age = _uniform(180, 3650)
    in_count = int(_uniform(1, 8))    # salary + occasional transfers
    out_count = int(_uniform(2, 15))  # bill pay, UPI, shopping
    pass_through = 0.0                 # retains balance between salary cycles
    deg = _clamp(_uniform(0.05, 0.30), 0, 1)
    clust = _clamp(_uniform(0.10, 0.60), 0, 1)  # natural social cluster
    btw = _clamp(_uniform(0.00, 0.15), 0, 1)    # not on critical paths
    n_nodes = int(_uniform(2, 8))
    n_edges = int(_uniform(1, 8))
    return [
        _clamp(age + random.gauss(0, 30), 90, 5000),
        float(in_count),
        float(out_count),
        pass_through,
        _clamp(deg + random.gauss(0, 0.02), 0, 1),
        _clamp(clust + random.gauss(0, 0.03), 0, 1),
        _clamp(btw + random.gauss(0, 0.02), 0, 1),
        float(n_nodes),
        float(n_edges),
    ]


def generate_legit_business_account() -> list[float]:
    """
    LEGIT — Small Business / Shop Account (label=0):
    Moderate-age account with many inbound (customers) and outbound (suppliers).
    High degree but natural cluster, low betweenness (not a financial intermediary).
    """
    age = _uniform(90, 1800)
    in_count = int(_uniform(5, 30))   # customer payments
    out_count = int(_uniform(3, 20))  # supplier payments
    pass_through = random.choice([0.0, 0.0, 1.0])  # mostly retains balance
    deg = _clamp(_uniform(0.15, 0.55), 0, 1)
    clust = _clamp(_uniform(0.20, 0.70), 0, 1)
    btw = _clamp(_uniform(0.00, 0.20), 0, 1)
    n_nodes = int(_uniform(3, 15))
    n_edges = int(_uniform(2, 15))
    return [
        _clamp(age + random.gauss(0, 15), 60, 3000),
        float(in_count),
        float(out_count),
        pass_through,
        _clamp(deg + random.gauss(0, 0.03), 0, 1),
        _clamp(clust + random.gauss(0, 0.03), 0, 1),
        _clamp(btw + random.gauss(0, 0.02), 0, 1),
        float(n_nodes),
        float(n_edges),
    ]


def generate_borderline_legit() -> list[float]:
    """
    BORDERLINE LEGIT (label=0) — e.g. freelancer, gig worker:
    Newer account, frequent small inbound payments, moderate outbound.
    Could look mule-adjacent but retains balance; low betweenness.
    """
    age = _uniform(30, 300)
    in_count = int(_uniform(3, 20))
    out_count = int(_uniform(2, 15))
    pass_through = random.choice([0.0, 0.0, 0.0, 1.0])
    deg = _clamp(_uniform(0.10, 0.45), 0, 1)
    clust = _clamp(_uniform(0.15, 0.50), 0, 1)
    btw = _clamp(_uniform(0.00, 0.25), 0, 1)
    n_nodes = int(_uniform(2, 10))
    n_edges = int(_uniform(2, 10))
    return [
        _clamp(age + random.gauss(0, 5), 10, 500),
        float(in_count),
        float(out_count),
        pass_through,
        _clamp(deg + random.gauss(0, 0.02), 0, 1),
        _clamp(clust + random.gauss(0, 0.03), 0, 1),
        _clamp(btw + random.gauss(0, 0.02), 0, 1),
        float(n_nodes),
        float(n_edges),
    ]


def build_dataset(n_per_class: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """
    Build balanced dataset.
    Positives (mule=1): MULE_ACCOUNT + LAYERING_HUB + SMURFING
    Negatives (mule=0): LEGIT_SALARY + LEGIT_BUSINESS + BORDERLINE_LEGIT
    """
    n = n_per_class
    positive_rows = (
        [generate_mule_account() for _ in range(n)]
        + [generate_layering_hub() for _ in range(n)]
        + [generate_smurfing_account() for _ in range(n)]
    )
    negative_rows = (
        [generate_legit_salary_account() for _ in range(n)]
        + [generate_legit_business_account() for _ in range(n)]
        + [generate_borderline_legit() for _ in range(n)]
    )
    X = np.array(positive_rows + negative_rows, dtype=np.float32)
    y = np.array([1] * len(positive_rows) + [0] * len(negative_rows), dtype=np.int32)
    return X, y


def metrics_dict(y_true, y_pred, y_prob) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    out = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "n_test": int(len(y_true)),
        "positive_rate_test": round(float(sum(y_true) / len(y_true)), 4),
    }
    if y_prob is not None and len(set(y_true)) > 1:
        out["roc_auc"] = round(float(roc_auc_score(y_true, y_prob)), 4)
    return out


def train() -> dict:
    ARTEFACTS.mkdir(parents=True, exist_ok=True)
    MODEL_DEST.mkdir(parents=True, exist_ok=True)

    print("[F-07] Generating synthetic Indian bank transaction dataset...")
    X, y = build_dataset(n_per_class=1000)
    print(f"[F-07] Dataset: {len(X)} samples  |  Mule={y.sum()}  Legit={(1-y).sum()}")

    # 60/20/20 stratified split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.40, stratify=y, random_state=SEED
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=SEED
    )
    print(f"[F-07] Split: train={len(y_train)}  val={len(y_val)}  test={len(y_test)}")

    model = XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="auc",
        random_state=SEED,
        n_jobs=-1,
    )

    print("[F-07] Training XGBoost on Indian bank synthetic data...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    test_metrics = metrics_dict(y_test, pred, proba)

    feature_names = [
        "account_age_days", "inbound_txn_count", "outbound_txn_count",
        "rapid_fund_pass_through", "degree_centrality", "clustering_coefficient",
        "betweenness_centrality", "node_count", "edge_count",
    ]
    importances = {
        name: round(float(imp), 4)
        for name, imp in zip(feature_names, model.feature_importances_)
    }

    report = {
        "feature": "F-07",
        "model": "XGBoost",
        "dataset": (
            "Synthetic Indian bank transaction dataset - models UPI/NEFT/IMPS mule account "
            "typologies based on RBI/FIU-IND advisories and NPCI UPI fraud patterns. "
            "Replaces Elliptic cryptocurrency dataset (ADR-024 resolved)."
        ),
        "domain": "Indian bank accounts (UPI, NEFT, IMPS)",
        "adr_resolved": "ADR-024",
        "classes": {
            "mule_patterns": ["MULE_ACCOUNT", "LAYERING_HUB", "SMURFING"],
            "legit_patterns": ["SALARY_ACCOUNT", "BUSINESS_ACCOUNT", "BORDERLINE_LEGIT"],
        },
        "split": "60/20/20 stratified",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "class_distribution_train": {
            "mule": int(y_train.sum()),
            "legit": int((1 - y_train).sum()),
        },
        "test": test_metrics,
        "feature_importances": importances,
        "limitation": (
            "Synthetic data - not a real labelled Indian bank transaction dataset. "
            "Statistical indicator only; not proof of criminal activity."
        ),
    }

    # Save to artefacts/
    artefact_path = ARTEFACTS / "f07_xgboost.joblib"
    metrics_path = ARTEFACTS / "f07_metrics.json"
    joblib.dump(model, artefact_path)
    metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[F-07] Saved model   -> {artefact_path}")
    print(f"[F-07] Saved metrics -> {metrics_path}")

    # Copy into app/ml/models/ for inference (overwrites old Elliptic model)
    dest_model = MODEL_DEST / "f07_mule_account_model.joblib"
    dest_metrics = MODEL_DEST / "f07_metrics.json"
    shutil.copy2(artefact_path, dest_model)
    shutil.copy2(metrics_path, dest_metrics)
    print(f"[F-07] Copied model  -> {dest_model}")
    print(f"[F-07] Copied metrics-> {dest_metrics}")

    print("\n[F-07] -- EVALUATION RESULTS --------------------------------------")
    print(f"  Accuracy : {test_metrics['accuracy']:.4f}")
    print(f"  Precision: {test_metrics['precision']:.4f}")
    print(f"  Recall   : {test_metrics['recall']:.4f}")
    print(f"  F1-Score : {test_metrics['f1']:.4f}")
    print(f"  ROC-AUC  : {test_metrics.get('roc_auc', 'N/A')}")
    print(f"  Confusion : {test_metrics['confusion_matrix']}")
    print("[F-07] -----------------------------------------------------------")
    print("[F-07] ADR-024 RESOLVED - Model now trained on Indian bank domain.")

    return report


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    report = train()
    print("\nFull report:")
    print(json.dumps(report, indent=2))
