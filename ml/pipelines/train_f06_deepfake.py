import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def generate_synthetic_deepfake_dataset(num_samples: int = 1000) -> pd.DataFrame:
    """Generates synthetic media feature dataset (frequency domain artifacts, facial boundary noise) for F-06."""
    np.random.seed(42)
    
    data = []
    labels = []
    
    for i in range(num_samples):
        is_deepfake = np.random.choice([0, 1], p=[0.5, 0.5])
        
        if is_deepfake:
            fft_high_freq_noise = np.random.normal(loc=0.75, scale=0.15)
            color_mismatch_score = np.random.normal(loc=0.65, scale=0.2)
            boundary_blurriness = np.random.normal(loc=0.80, scale=0.1)
            eye_blinking_rate_anomaly = np.random.choice([0, 1], p=[0.2, 0.8])
        else:
            fft_high_freq_noise = np.random.normal(loc=0.25, scale=0.1)
            color_mismatch_score = np.random.normal(loc=0.15, scale=0.1)
            boundary_blurriness = np.random.normal(loc=0.20, scale=0.1)
            eye_blinking_rate_anomaly = np.random.choice([0, 1], p=[0.9, 0.1])
            
        data.append({
            'fft_high_freq_noise': max(0.0, float(fft_high_freq_noise)),
            'color_mismatch_score': max(0.0, float(color_mismatch_score)),
            'boundary_blurriness': max(0.0, float(boundary_blurriness)),
            'eye_blinking_rate_anomaly': int(eye_blinking_rate_anomaly)
        })
        labels.append(is_deepfake)
        
    df = pd.DataFrame(data)
    df['label'] = labels
    return df


def train_f06_model():
    """Trains Random Forest model for F-06 Deepfake Detection (Research/Experimental)."""
    print("=== Training F-06 Deepfake Detection Model ===")
    df = generate_synthetic_deepfake_dataset(1000)
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
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
    
    joblib.dump(model, "ml/models/f06_deepfake_model.joblib")
    joblib.dump(model, "backend/app/ml/models/f06_deepfake_model.joblib")
    
    with open("ml/models/f06_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("F-06 Training Complete. Metrics:", metrics)
    return metrics


if __name__ == "__main__":
    train_f06_model()
