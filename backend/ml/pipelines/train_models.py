"""Train F-01 / F-02 / F-05 artefacts. Writes metrics computed on a held-out test split only."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
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

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "ml" / "datasets"
ARTEFACTS = ROOT / "ml" / "artefacts"
import sys

sys.path.insert(0, str(ROOT))
from app.detect_analyze.url import feature_vector, extract_url_features  # noqa: E402
from app.ml.f05 import encode_signals  # noqa: E402

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

LEGIT_DOMAINS = [
    "https://www.rbi.org.in/",
    "https://www.uidai.gov.in/",
    "https://www.npci.org.in/",
    "https://www.incometax.gov.in/",
    "https://www.sbi.co.in/",
    "https://onlinesbi.sbi/",
    "https://www.hdfcbank.com/",
    "https://www.icicibank.com/",
    "https://www.paytm.com/",
    "https://www.phonepe.com/",
    "https://www.irctc.co.in/",
    "https://www.google.com/",
    "https://www.wikipedia.org/",
    "https://www.microsoft.com/",
    "https://github.com/",
    "https://www.india.gov.in/",
    "https://cybercrime.gov.in/",
    "https://www.meity.gov.in/",
]


def metrics_dict(y_true, y_pred, y_prob) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "n_test": int(len(y_true)),
        "positive_rate_test": float(sum(y_true) / len(y_true)),
    }
    if y_prob is not None and len(set(y_true)) > 1:
        out["roc_auc"] = float(roc_auc_score(y_true, y_prob))
    return out


def load_urlhaus(limit: int = 4000) -> list[str]:
    path = DATA / "urlhaus_recent.csv"
    if not path.is_file():
        path = ROOT / "urlhaus_recent.csv"
    urls = []
    if not path.is_file():
        return urls
    with path.open(encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(filter(lambda row: row and not row.startswith("#"), fh))
        for row in reader:
            if len(row) < 3:
                continue
            url = row[2].strip()
            if url.startswith("http"):
                urls.append(url[:2048])
            if len(urls) >= limit:
                break
    return urls


def train_f01() -> dict:
    ARTEFACTS.mkdir(parents=True, exist_ok=True)
    pos = load_urlhaus()
    neg = []
    for base in LEGIT_DOMAINS:
        neg.append(base)
        neg.append(base.rstrip("/") + "/login")
        neg.append(base.rstrip("/") + "/about")
    while len(neg) < min(len(pos), 4000):
        neg.extend(list(neg))
    neg = neg[: max(len(pos), 1)]
    if len(pos) < 50:
        raise SystemExit("F-01 BLOCKED: URLhaus CSV missing or too small")
    X_urls = pos + neg
    y = [1] * len(pos) + [0] * len(neg)
    X = np.array([feature_vector(extract_url_features(u)) for u in X_urls])
    y = np.array(y)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=SEED)
    model = XGBClassifier(
        n_estimators=80,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=SEED,
        n_jobs=2,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    report = {
        "feature": "F-01",
        "model": "XGBoost",
        "dataset": "URLhaus recent (malicious URLs) vs curated official-domain negatives",
        "license_note": "URLhaus: open (abuse.ch). Negatives are curated official sites, not Tranco top-1M.",
        "split": "80/10/10 stratified",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "class_distribution_train": {"malicious": int(y_train.sum()), "legit": int((1 - y_train).sum())},
        "test": metrics_dict(y_test, pred, proba),
    }
    joblib.dump(model, ARTEFACTS / "f01_xgboost.joblib")
    (ARTEFACTS / "f01_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def train_f02() -> dict:
    path = DATA / "sms.tsv"
    if not path.is_file():
        path = ROOT / "sms.tsv"
    rows = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) != 2:
                continue
            label, text = parts
            y = 1 if label.strip().lower() == "spam" else 0
            rows.append((text, y))
    if len(rows) < 100:
        raise SystemExit("F-02 BLOCKED: SMS dataset missing")
    texts = [r[0] for r in rows]
    y = np.array([r[1] for r in rows])
    X_train, X_temp, y_train, y_temp = train_test_split(texts, y, test_size=0.2, stratify=y, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=SEED)
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=20000)
    Xt = vectorizer.fit_transform(X_train)
    clf = LogisticRegression(max_iter=200, class_weight="balanced", random_state=SEED)
    clf.fit(Xt, y_train)
    proba = clf.predict_proba(vectorizer.transform(X_test))[:, 1]
    pred = (proba >= 0.5).astype(int)
    report = {
        "feature": "F-02",
        "model": "TF-IDF char n-grams + Logistic Regression",
        "dataset": "SMS Spam Collection (UCI) via public tsv mirror",
        "limitation": "English SMS spam/ham; not an India-specific scam corpus.",
        "distilbert": "not_trained",
        "split": "80/10/10 stratified",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "class_distribution_train": {"spam": int(y_train.sum()), "ham": int((1 - y_train).sum())},
        "test": metrics_dict(y_test, pred, proba),
        "val_f1": float(f1_score(y_val, (clf.predict_proba(vectorizer.transform(X_val))[:, 1] >= 0.5).astype(int))),
    }
    joblib.dump({"vectorizer": vectorizer, "model": clf}, ARTEFACTS / "f02_tfidf_lr.joblib")
    (ARTEFACTS / "f02_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _synthetic_profile(label: int) -> dict:
    if label == 1:
        return {
            "account_age_category": random.choice(["days", "weeks"]),
            "follower_count_range": random.choice(["none", "low"]),
            "following_to_follower_ratio_high": True,
            "has_profile_photo": random.choice([True, False]),
            "profile_photo_appears_generic": True,
            "bio_present": False,
            "posts_count_range": "none",
            "sent_unsolicited_money_request": random.random() < 0.7,
            "claims_celebrity_or_official": random.random() < 0.4,
            "platform": random.choice(["instagram", "facebook", "whatsapp"]),
            "contacted_via_dm_unsolicited": True,
            "promotes_investment_or_scheme": random.random() < 0.5,
        }
    return {
        "account_age_category": random.choice(["months", "years"]),
        "follower_count_range": random.choice(["medium", "high"]),
        "following_to_follower_ratio_high": False,
        "has_profile_photo": True,
        "profile_photo_appears_generic": False,
        "bio_present": True,
        "posts_count_range": random.choice(["some", "many"]),
        "sent_unsolicited_money_request": False,
        "claims_celebrity_or_official": False,
        "platform": random.choice(["instagram", "facebook", "twitter"]),
        "contacted_via_dm_unsolicited": False,
        "promotes_investment_or_scheme": False,
    }


def train_f05() -> dict:
    y = np.array([1] * 400 + [0] * 400)
    X = np.array([encode_signals(_synthetic_profile(int(lbl))) for lbl in y])
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=SEED)
    model = XGBClassifier(n_estimators=60, max_depth=3, learning_rate=0.1, random_state=SEED, eval_metric="logloss")
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    report = {
        "feature": "F-05",
        "model": "XGBoost",
        "dataset": "synthetic labels generated from documented F-05 observable indicators",
        "limitation": "Not an academic fake-social-media dataset. Metrics describe the synthetic distribution only.",
        "split": "80/10/10 stratified",
        "seed": SEED,
        "n_train": int(len(y_train)),
        "test": metrics_dict(y_test, pred, proba),
    }
    joblib.dump(model, ARTEFACTS / "f05_xgboost.joblib")
    (ARTEFACTS / "f05_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    DATA.mkdir(parents=True, exist_ok=True)
    reports = {"f01": train_f01(), "f02": train_f02(), "f05": train_f05()}
    print(json.dumps({k: {**v, "test": v["test"]} for k, v in reports.items()}, indent=2))
