import os
import json
import joblib
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def generate_synthetic_mule_dataset(num_samples: int = 1000) -> pd.DataFrame:
    """Generates synthetic account transaction network & graph feature dataset for F-07."""
    np.random.seed(42)
    
    # Construct a synthetic transaction graph using NetworkX
    G = nx.erdos_renyi_graph(n=200, p=0.05, seed=42, directed=True)
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    betweenness = nx.betweenness_centrality(G)
    clustering = nx.clustering(G)
    
    data = []
    labels = []
    
    node_ids = list(G.nodes())
    
    for i in range(num_samples):
        node = node_ids[i % len(node_ids)]
        is_mule = np.random.choice([0, 1], p=[0.5, 0.5])
        
        if is_mule:
            account_age_cat = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])  # 0: <3mo, 1: 3-12mo, 2: >12mo
            txn_velocity_high = np.random.choice([0, 1], p=[0.1, 0.9])
            multiple_recipients = np.random.choice([0, 1], p=[0.2, 0.8])
            round_amount_transfers = np.random.choice([0, 1], p=[0.3, 0.7])
            pass_through = np.random.choice([0, 1], p=[0.1, 0.9])
            deg_centrality = betweenness[node] * 2.5 + np.random.normal(0.5, 0.1)
        else:
            account_age_cat = np.random.choice([0, 1, 2], p=[0.05, 0.15, 0.8])
            txn_velocity_high = np.random.choice([0, 1], p=[0.9, 0.1])
            multiple_recipients = np.random.choice([0, 1], p=[0.8, 0.2])
            round_amount_transfers = np.random.choice([0, 1], p=[0.85, 0.15])
            pass_through = np.random.choice([0, 1], p=[0.95, 0.05])
            deg_centrality = betweenness[node] + np.random.normal(0.1, 0.05)
            
        data.append({
            'account_age_category': account_age_cat,
            'transaction_velocity_high': txn_velocity_high,
            'multiple_recipients': multiple_recipients,
            'round_amount_transfers': round_amount_transfers,
            'account_used_for_receiving_then_forwarding': pass_through,
            'graph_in_degree': in_degrees[node],
            'graph_out_degree': out_degrees[node],
            'graph_betweenness_centrality': max(0.0, float(deg_centrality)),
            'graph_clustering_coefficient': float(clustering[node])
        })
        labels.append(is_mule)
        
    df = pd.DataFrame(data)
    df['label'] = labels
    return df


def train_f07_model():
    """Trains Gradient Boosting + NetworkX graph features model for F-07 Mule Account Detection."""
    print("=== Training F-07 Mule Account Model ===")
    df = generate_synthetic_mule_dataset(1000)
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
    
    joblib.dump(model, "ml/models/f07_mule_account_model.joblib")
    joblib.dump(model, "backend/app/ml/models/f07_mule_account_model.joblib")
    
    with open("ml/models/f07_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("F-07 Training Complete. Metrics:", metrics)
    return metrics


if __name__ == "__main__":
    train_f07_model()
