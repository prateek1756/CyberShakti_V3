import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def generate_synthetic_profile_dataset(num_samples: int = 1000) -> pd.DataFrame:
    """Generates synthetic dataset of observable social profile risk signals for F-05 training."""
    np.random.seed(42)
    
    data = []
    labels = []
    
    for i in range(num_samples):
        is_fake = np.random.choice([0, 1], p=[0.5, 0.5])
        
        if is_fake:
            age_cat = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])  # 0: <1mo, 1: 1-6mo, 2: >6mo
            follower_cat = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1]) # 0: 0-50, 1: 50-500, 2: >500
            ratio_high = np.random.choice([0, 1], p=[0.2, 0.8])
            has_photo = np.random.choice([0, 1], p=[0.3, 0.7])
            photo_generic = np.random.choice([0, 1], p=[0.2, 0.8]) if has_photo else 0
            bio_present = np.random.choice([0, 1], p=[0.7, 0.3])
            money_req = np.random.choice([0, 1], p=[0.2, 0.8])
            celeb_claim = np.random.choice([0, 1], p=[0.6, 0.4])
            unsolicited_dm = np.random.choice([0, 1], p=[0.1, 0.9])
            scheme_promo = np.random.choice([0, 1], p=[0.3, 0.7])
        else:
            age_cat = np.random.choice([0, 1, 2], p=[0.05, 0.15, 0.8])
            follower_cat = np.random.choice([0, 1, 2], p=[0.1, 0.3, 0.6])
            ratio_high = np.random.choice([0, 1], p=[0.85, 0.15])
            has_photo = np.random.choice([0, 1], p=[0.05, 0.95])
            photo_generic = np.random.choice([0, 1], p=[0.9, 0.1]) if has_photo else 0
            bio_present = np.random.choice([0, 1], p=[0.1, 0.9])
            money_req = np.random.choice([0, 1], p=[0.99, 0.01])
            celeb_claim = np.random.choice([0, 1], p=[0.98, 0.02])
            unsolicited_dm = np.random.choice([0, 1], p=[0.8, 0.2])
            scheme_promo = np.random.choice([0, 1], p=[0.95, 0.05])
            
        data.append({
            'account_age_category': age_cat,
            'follower_count_range': follower_cat,
            'following_to_follower_ratio_high': ratio_high,
            'has_profile_photo': has_photo,
            'profile_photo_appears_generic': photo_generic,
            'bio_present': bio_present,
            'sent_unsolicited_money_request': money_req,
            'claims_celebrity_or_official': celeb_claim,
            'contacted_via_dm_unsolicited': unsolicited_dm,
            'promotes_investment_or_scheme': scheme_promo
        })
        labels.append(is_fake)
        
    df = pd.DataFrame(data)
    df['label'] = labels
    return df


def train_f05_model():
    """Trains Gradient Boosting model for F-05 Fake Profile Risk Assessment."""
    print("=== Training F-05 Fake Profile Risk Model ===")
    df = generate_synthetic_profile_dataset(1000)
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }
    
    os.makedirs("ml/models", exist_ok=True)
    os.makedirs("backend/app/ml/models", exist_ok=True)
    
    joblib.dump(model, "ml/models/f05_fake_profile_model.joblib")
    joblib.dump(model, "backend/app/ml/models/f05_fake_profile_model.joblib")
    
    with open("ml/models/f05_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("F-05 Training Complete. Metrics:", metrics)
    return metrics


if __name__ == "__main__":
    train_f05_model()
