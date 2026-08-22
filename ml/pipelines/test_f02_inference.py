import sys
sys.path.append('backend')
from app.ml.f02 import infer_text

tests = [
    ("FRAUD", "Your SBI account is blocked. Update KYC immediately."),
    ("FRAUD", "Your bank account is blocked. Update KYC immediately at bit.ly/kyc-fix or call 9876543210."),
    ("FRAUD", "Congratulations! You won Rs 25,00,000 in KBC Lottery. Claim by depositing processing fee of Rs 5000."),
    ("FRAUD", "URGENT: Click http://sbi-kyc-update.xyz to verify your Aadhaar linked to SBI account."),
    ("LEGIT", "Your OTP for HDFC login is 482910. Do not share this."),
    ("LEGIT", "Hi Team, see attached agenda for tomorrow meeting."),
    ("LEGIT", "Dear customer, your electricity bill of Rs 1420 is due on 28th Aug. Pay via official app."),
    ("FRAUD", "URGENT job offer: Earn Rs 5000 per day liking YouTube videos. Work from home. Join Telegram group."),
    ("FRAUD", "Guaranteed 50% returns in 7 days on crypto investment. Limited seats. Contact manager WhatsApp."),
]

print("\n=== F-02 Inference Verification ===\n")
for expected, msg in tests:
    r = infer_text(msg)
    cls = r["classification"]
    prob = r["probability"]
    predicted = "FRAUD" if cls in ("FRAUD_SCAM", "SUSPICIOUS") else "LEGIT"
    status = "OK" if predicted == expected else "FAIL"
    signals = r["scam_signals"]
    print(f"[{status}] [{cls:12s}] prob={prob:.3f} signals={signals}")
    print(f"   {msg[:70]}")
    print()
