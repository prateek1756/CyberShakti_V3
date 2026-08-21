import os
import json
import math
import re
from urllib.parse import urlparse
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def extract_url_features(url: str) -> dict:
    """Extracts 17 lexical and domain features from a URL string according to CSHAKTI-ML-001 §2.4."""
    parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'http://{url}')
    domain = parsed.netloc or parsed.path.split('/')[0]
    path = parsed.path
    
    url_len = len(url)
    domain_len = len(domain)
    path_len = len(path)
    num_dots = url.count('.')
    num_hyphens = domain.count('-')
    num_underscores = url.count('_')
    num_at = url.count('@')
    num_question = url.count('?')
    num_slashes = url.count('/')
    num_digits = sum(c.isdigit() for c in domain)
    digit_ratio = num_digits / max(1, domain_len)
    
    has_ip = 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain) else 0
    uses_https = 1 if url.startswith('https://') else 0
    has_port = 1 if ':' in domain and not domain.endswith(':80') and not domain.endswith(':443') else 0
    
    prob = [float(url.count(c)) / len(url) for c in set(url)]
    entropy = -sum([p * math.log(p, 2) for p in prob]) if prob else 0
    
    subdomain_count = max(0, len(domain.split('.')) - 2)
    
    shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly']
    is_shortened = 1 if any(s in domain for s in shorteners) else 0

    return {
        'url_length': url_len,
        'domain_length': domain_len,
        'path_length': path_len,
        'num_dots': num_dots,
        'num_hyphens': num_hyphens,
        'num_underscores': num_underscores,
        'num_at_signs': num_at,
        'num_question_marks': num_question,
        'num_slashes': num_slashes,
        'num_digits': num_digits,
        'digit_to_letter_ratio': digit_ratio,
        'has_ip_address': has_ip,
        'uses_https': uses_https,
        'has_port_in_url': has_port,
        'url_entropy': round(entropy, 4),
        'subdomain_count': subdomain_count,
        'is_shortened_url': is_shortened
    }


def generate_synthetic_url_dataset(num_samples: int = 1000) -> pd.DataFrame:
    """Generates a reproducible dataset of phishing and legitimate URLs for F-01 model training."""
    np.random.seed(42)
    
    legit_domains = ["google.com", "wikipedia.org", "github.com", "gov.in", "amazon.in", "sbi.co.in", "hdfcbank.com", "npci.org.in"]
    phish_tokens = ["verify-kyc", "bank-update", "reward-claim", "account-blocked", "secure-login", "upi-collect"]
    phish_tlds = [".info", ".xyz", ".top", ".club", ".online"]
    
    data = []
    labels = []
    
    for i in range(num_samples // 2):
        domain = np.random.choice(legit_domains)
        path = f"/page/{i}" if i % 2 == 0 else ""
        url = f"https://www.{domain}{path}"
        data.append(extract_url_features(url))
        labels.append(0)
        
        token = np.random.choice(phish_tokens)
        tld = np.random.choice(phish_tlds)
        sub = "login.verify" if i % 3 == 0 else "update"
        url = f"http://{sub}.{token}-{i}{tld}/account/verify?token=abc"
        data.append(extract_url_features(url))
        labels.append(1)
        
    df = pd.DataFrame(data)
    df['label'] = labels
    return df


def train_f01_model():
    """Trains native XGBoost classifier (XGBClassifier) for F-01 Phishing URL Detection per ADR-008."""
    print("=== Training F-01 Phishing URL Model (Native XGBoost) ===")
    df = generate_synthetic_url_dataset(1000)
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Baseline: Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    
    # Mandatory Native XGBoost Model (ADR-008)
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, xgb_preds)),
        "precision": float(precision_score(y_test, xgb_preds)),
        "recall": float(recall_score(y_test, xgb_preds)),
        "f1_score": float(f1_score(y_test, xgb_preds)),
        "roc_auc": float(roc_auc_score(y_test, xgb_probs)),
        "confusion_matrix": confusion_matrix(y_test, xgb_preds).tolist()
    }
    
    os.makedirs("ml/models", exist_ok=True)
    os.makedirs("backend/app/ml/models", exist_ok=True)
    
    joblib.dump(xgb_model, "ml/models/f01_phishing_url_model.joblib")
    joblib.dump(xgb_model, "backend/app/ml/models/f01_phishing_url_model.joblib")
    
    with open("ml/models/f01_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("F-01 XGBoost Training Complete. Metrics:", metrics)
    return metrics


if __name__ == "__main__":
    train_f01_model()
