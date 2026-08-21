import os
import json
import torch
import joblib
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class ScamDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=64):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_len,
            padding='max_length',
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(self.labels[idx], dtype=torch.long)
        }

def train_f02_distilbert():
    """Fine-tunes distilbert-base-uncased for F-02 Scam Text Detection on UCI SMS Spam Collection dataset."""
    print("=== REM-03: F-02 DistilBERT Training Pipeline ===")
    
    # 1. Load the legitimate SMS Spam Collection dataset
    dataset_path = "backend/ml/datasets/sms.tsv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"SMS dataset not found at {dataset_path}")
        
    df = pd.read_csv(dataset_path, sep="\t", names=["raw_label", "text"])
    df["label"] = df["raw_label"].map({"ham": 0, "spam": 1})
    
    # Check class counts
    ham_df = df[df["label"] == 0]
    spam_df = df[df["label"] == 1]
    print(f"Original Dataset Size: {len(df)} (Ham: {len(ham_df)}, Spam: {len(spam_df)})")
    
    # Create balanced subset for CPU-friendly training
    n_samples_per_class = 250
    balanced_df = pd.concat([
        ham_df.sample(n=n_samples_per_class, random_state=42),
        spam_df.sample(n=n_samples_per_class, random_state=42)
    ]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    print(f"Balanced Dataset Size: {len(balanced_df)} (Ham: {n_samples_per_class}, Spam: {n_samples_per_class})")
    
    # 2. Train/Test split (80/20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        balanced_df['text'], balanced_df['label'], test_size=0.2, random_state=42, stratify=balanced_df['label']
    )
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # 3. Train Baseline TF-IDF + Logistic Regression model on the same split
    print("Training TF-IDF + Logistic Regression Baseline...")
    baseline_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, lowercase=True)),
        ('clf', LogisticRegression(random_state=42))
    ])
    baseline_pipeline.fit(X_train, y_train)
    baseline_preds = baseline_pipeline.predict(X_test)
    
    baseline_metrics = {
        "accuracy": float(accuracy_score(y_test, baseline_preds)),
        "precision": float(precision_score(y_test, baseline_preds)),
        "recall": float(recall_score(y_test, baseline_preds)),
        "f1_score": float(f1_score(y_test, baseline_preds)),
        "confusion_matrix": confusion_matrix(y_test, baseline_preds).tolist()
    }
    print("Baseline Metrics:", baseline_metrics)
    
    # 4. Fine-tune DistilBERT
    print("Loading distilbert-base-uncased tokenizer and model...")
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
    
    train_dataset = ScamDataset(X_train, y_train, tokenizer)
    test_dataset = ScamDataset(X_test, y_test, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    optimizer = AdamW(model.parameters(), lr=3e-5)
    
    epochs = 2
    print(f"Starting training on {device} for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_idx, batch in enumerate(train_loader):
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            if (batch_idx + 1) % 15 == 0:
                print(f"Epoch {epoch+1}/{epochs} | Batch {batch_idx+1}/{len(train_loader)} | Loss: {loss.item():.4f}")
        print(f"Epoch {epoch+1} Completed. Avg Loss: {total_loss/len(train_loader):.4f}")
        
    # 5. Evaluate DistilBERT
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    distilbert_metrics = {
        "accuracy": float(accuracy_score(all_labels, all_preds)),
        "precision": float(precision_score(all_labels, all_preds, zero_division=0)),
        "recall": float(recall_score(all_labels, all_preds, zero_division=0)),
        "f1_score": float(f1_score(all_labels, all_preds, zero_division=0)),
        "confusion_matrix": confusion_matrix(all_labels, all_preds).tolist()
    }
    print("DistilBERT Metrics:", distilbert_metrics)
    
    # 6. Save models and metrics
    os.makedirs("ml/models/distilbert_scam", exist_ok=True)
    os.makedirs("backend/app/ml/models/distilbert_scam", exist_ok=True)
    
    model.save_pretrained("ml/models/distilbert_scam")
    tokenizer.save_pretrained("ml/models/distilbert_scam")
    model.save_pretrained("backend/app/ml/models/distilbert_scam")
    tokenizer.save_pretrained("backend/app/ml/models/distilbert_scam")
    
    # Save baseline to overwrite the old toy dataset model
    joblib.dump(baseline_pipeline, "ml/models/f02_scam_text_pipeline.joblib")
    joblib.dump(baseline_pipeline, "backend/app/ml/models/f02_scam_text_pipeline.joblib")
    
    # Save metrics metadata
    metadata = {
        "dataset_name": "SMS Spam Collection Dataset",
        "source": dataset_path,
        "dataset_size": len(df),
        "labels": {"ham": 0, "spam": 1},
        "class_distribution": {"ham": len(ham_df), "spam": len(spam_df)},
        "balanced_subset_size": len(balanced_df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "distilbert_metrics": distilbert_metrics,
        "baseline_metrics": baseline_metrics
    }
    
    with open("ml/models/f02_distilbert_metrics.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("F-02 Pipelines Saved successfully.")
    return metadata

if __name__ == "__main__":
    train_f02_distilbert()
