import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def generate_synthetic_scam_text_dataset() -> pd.DataFrame:
    """Generates a dataset of scam text messages and legitimate transactional SMS/emails for F-02."""
    scam_messages = [
        "Dear customer, your bank account is suspended. Update KYC immediately at bit.ly/kyc-fix or call 9876543210.",
        "URGENT: Your electricity connection will be disconnected tonight at 9:30 PM due to overdue bill. Call officer at 9876543210.",
        "Congratulations! You won Rs 25,00,000 in KBC Lottery. Claim your prize by depositing processing fee of Rs 5000 via UPI.",
        "URGENT job offer: Earn Rs 5000 per day by liking YouTube videos. Work from home. Click link to join Telegram group.",
        "Your bank account blocked due to unverified Aadhaar card. Click link http://sbi-kyc-verify.info to update immediately.",
        "You have received an unexpected refund of Rs 15,000 from Income Tax Dept. Click link to enter account details.",
        "Dear user, your SIM card will be deactivated within 2 hours. Send 24-digit SIM number to 9876543210 to stop.",
        "URGENT: Someone tried to login to your HDFC bank account. Click http://hdfc-security-fix.top to secure account.",
        "Guaranteed 50% returns in 7 days on crypto investment. Limited seats remaining. Contact manager on WhatsApp.",
        "Your credit card reward points worth Rs 9,450 are expiring today. Redeem immediately by clicking http://reward-redeem.xyz"
    ] * 25

    legit_messages = [
        "Your OTP for login to HDFC Bank internet banking is 482910. Do not share this OTP with anyone.",
        "Dear Customer, Rs 500.00 debited from account xx4892 via UPI to SWIGGY. Ref No 408291048291.",
        "Your electricity bill of Rs 1,420 for month of July is generated. Due date: 28th Aug. Pay via official utility app.",
        "Hi Team, attached is the presentation for tomorrow's engineering sync meeting. Please review beforehand.",
        "Your order #48201 has been dispatched via BlueDart. Track delivery at https://www.bluedart.com/track",
        "Dear Customer, Rs 12,000.00 credited to your account xx9102 towards monthly salary. Total balance: Rs 45,210.00.",
        "Your appointment with Dr. Sharma is confirmed for tomorrow at 4:30 PM at Apollo Clinic, Indiranagar.",
        "Train ticket booked successfully. PNR: 4829104820, Train: 12628 Karnataka Exp, Date: 25 Aug 2026.",
        "Dear Student, your semester exam timetable has been published on the university portal. Check official site.",
        "Your broadband bill of Rs 825 is due on 25th Aug. Pay on Airtel Thanks app to avoid late charges."
    ] * 25

    texts = scam_messages + legit_messages
    labels = [1] * len(scam_messages) + [0] * len(legit_messages)

    return pd.DataFrame({"text": texts, "label": labels})


def train_f02_model():
    """Trains TF-IDF + Logistic Regression NLP model for F-02 Scam Text Detection."""
    print("=== Training F-02 Scam Text NLP Model ===")
    df = generate_synthetic_scam_text_dataset()
    
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, lowercase=True)),
        ('clf', LogisticRegression(random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
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
    
    joblib.dump(pipeline, "ml/models/f02_scam_text_pipeline.joblib")
    joblib.dump(pipeline, "backend/app/ml/models/f02_scam_text_pipeline.joblib")
    
    with open("ml/models/f02_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("F-02 Training Complete. Metrics:", metrics)
    return metrics


if __name__ == "__main__":
    train_f02_model()
