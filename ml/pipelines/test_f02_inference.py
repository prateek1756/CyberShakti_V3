import sys
sys.path.append('backend')
from app.ml.f02 import infer_text

tests = [
    ("FRAUD", "Your bank account is blocked. Update KYC immediately at bit.ly/kyc-fix or call 9876543210."),
    ("FRAUD", "Congratulations! You won Rs 25,00,000 in KBC Lottery. Deposit Rs 5000 processing fee via UPI."),
    ("FRAUD", "URGENT: Your SBI account will be suspended. Click http://sbi-kyc-update.xyz to verify Aadhaar."),
    ("LEGIT", "Your OTP for HDFC Bank login is 482910. Do not share this OTP with anyone."),
    ("LEGIT", "Hi Team, please review the attached agenda for tomorrow meeting. Thanks."),
    ("LEGIT", "Your order from Flipkart has been dispatched. Expected delivery: 25 Aug."),
    ("LEGIT", "Dear customer, your electricity bill of Rs 1,420 is due on 28th Aug. Pay via official app."),
    ("FRAUD", "Earn Rs 5000 per day liking YouTube videos from home. Join our Telegram group now."),
    ("FRAUD", "Your PAN card has been deactivated. Update within 24 hours to avoid penalty at income-tax-india-gov.com"),
]

print("\n=== F-02 Scam Text Model Inference Test ===\n")
correct = 0
for expected, msg in tests:
    r = infer_text(msg)
    prob = r["probability"]
    predicted = "FRAUD" if prob > 0.5 else "LEGIT"
    status = "OK" if predicted == expected else "FAIL"
    correct += 1 if predicted == expected else 0
    print(f"[{status}] [{predicted}] prob={prob:.3f} expected={expected}")
    print(f"   {msg[:80]}")
    print()

print(f"Accuracy: {correct}/{len(tests)} = {correct/len(tests)*100:.1f}%")
