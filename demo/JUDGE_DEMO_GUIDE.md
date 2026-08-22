# CyberShakti V3 — Judge Demo Guide

> **Demo URL:** `http://localhost:5173`
> **API Docs:** `http://localhost:8000/docs`
> **Time needed:** ~8 minutes for full walkthrough

---

## Step 0 — Login Credentials

| Field | Value |
|---|---|
| **Email** | `user@cybershakti.in` |
| **Password** | `CyberShakti@123` |

---

## Feature 1 — Phishing Link Scanner (F-01)
**Route:** `/detect/phishing-link`
**Talking point:** ML model extracts 17 structural URL features — no external API needed.

### HIGH RISK URLs (paste one at a time)
- `https://sbi-kyc-update-portal-secure.xyz/login?session=abc123`
- `http://hdfc-bank-verify-account.info/netbanking/update`
- `https://paypal-secure-login.account-verify.tk/auth`
- `http://bit.ly/reward-claim-amazon`

### SAFE URLs
- `https://www.google.com`
- `https://www.sbi.co.in`

---

## Feature 2 — Scam Message Analyzer (F-02)
**Route:** `/detect/message-scan` > Text tab
**Talking point:** DistilBERT NLP fine-tuned on Indian scam corpus.

### HIGH RISK Message 1 (OTP Scam)
Dear Customer, Your SBI bank account has been temporarily BLOCKED due to incomplete KYC verification. To avoid permanent suspension, please update your details immediately by clicking the link and sharing the OTP sent to your registered mobile. Act within 24 hours or your account will be frozen. — SBI Customer Care

### HIGH RISK Message 2 (Lottery Fraud)
CONGRATULATIONS! You have won Rs 15,00,000 in the National Digital India Lucky Draw 2026. Your mobile number was selected from 5 crore participants. To claim your prize, send your Aadhaar number, bank account details and pay Rs 500 processing fee to UPI: claim-prize@hdfc

### HIGH RISK Message 3 (Impersonation)
Urgent: Your UPI ID has been flagged for suspicious activity. Your account will be blocked in 2 hours unless you verify by clicking http://upi-secure-verify.in/verify and entering your PIN. This is automated from NPCI Security Team.

### SAFE Message
Hi, are you free to catch up this weekend? We could go to the cafe near your place. Let me know!

---

## Feature 3 — Screenshot OCR Scanner (F-03)
**Route:** `/detect/message-scan` > OCR Screenshot tab
**How to demo:** Screenshot one of the scam messages above (e.g. paste in Notepad, take screenshot), upload the PNG.
EasyOCR extracts text then passes through DistilBERT classifier.

---

## Feature 4 — QR Code Scanner (F-04)
**Route:** `/detect/phishing-link` > QR Code Image tab
**How to demo:**
1. Go to https://www.qr-code-generator.com
2. Generate QR for: `https://hdfc-bank-verify-account.info/netbanking/update`
3. Download PNG and upload it
**Expected:** HIGH RISK verdict with phishing URL decoded

---

## Feature 5 — Fake Profile Detector (F-05)
**API via /docs:** `POST /api/v1/detect/assess-profile`

### HIGH RISK payload
{
  "signals": {
    "account_age_category": 0,
    "follower_count_range": 0,
    "following_to_follower_ratio_high": true,
    "has_profile_photo": true,
    "profile_photo_appears_generic": true,
    "bio_present": false,
    "sent_unsolicited_money_request": true,
    "claims_celebrity_or_official": true,
    "contacted_via_dm_unsolicited": true,
    "promotes_investment_or_scheme": true
  }
}

### SAFE payload
{
  "signals": {
    "account_age_category": 2,
    "follower_count_range": 2,
    "following_to_follower_ratio_high": false,
    "has_profile_photo": true,
    "profile_photo_appears_generic": false,
    "bio_present": true,
    "sent_unsolicited_money_request": false,
    "claims_celebrity_or_official": false,
    "contacted_via_dm_unsolicited": false,
    "promotes_investment_or_scheme": false
  }
}

---

## Feature 6 — Deepfake Detector (F-06)
**Route:** `/detect/deepfake`
**Talking point:** EfficientNet-B4 model trained on Celeb-DF v2 dataset.
Upload any clear face photo. Manipulated/GAN images score high risk.
Note: Label as experimental — disclaimer appears automatically.

---

## Feature 7 — Money Mule Account Detector (F-07)
**Route:** `/detect/mule-account`
**Talking point:** XGBoost with graph-theoretic signals (betweenness centrality, velocity).

### HIGH RISK — Select these options
- Account Age: Less than 6 months (New)
- Transaction Velocity: High (Rapid burst transfers)
- Fan-Out Recipients: Yes — Fan-out to many accounts
- Pass-Through Pattern: Yes — Rapid cash-in & cash-out
Expected: HIGH RISK / Money Mule Account Pattern

### SAFE — Select these options
- Account Age: More than 2 years
- Transaction Velocity: Normal velocity
- Fan-Out Recipients: No — Normal recipient list
- Pass-Through Pattern: No — Normal balance retention
Expected: SAFE / Low Risk Account

---

## Feature 8 — Password Security Checker (F-08)
**Route:** `/protect/password-check`
**Talking point:** Entropy bits = log2(charset_size) x length. Checks common password dictionary.

| Password to type | Expected |
|---|---|
| `password` | VERY WEAK — common |
| `123456` | VERY WEAK — common |
| `CyberShakti2026` | MODERATE |
| `Tr0ub4dor&3!Zx#9` | VERY STRONG |
| `x7Kq!@#mNpL`$`vR2y9Wz` | VERY STRONG — ~130 bits |

---

## Feature 9 — Cyber Risk Score (F-10)
**Route:** `/assist/risk-score` (requires login)
**Talking point:** Explainable weighted signal engine — scan history + questionnaire = personalized score.

### LOW SCORE answers (high risk user)
- 2FA on banking apps? NO
- Reuse same password? YES
- Click links from unknown senders? YES
- Verify sender before financial actions? NO
- Device lock enabled? NO
Expected Score: ~20–30 (High Risk)

### HIGH SCORE answers (safe user)
- 2FA on banking apps? YES
- Reuse same password? NO
- Click links from unknown senders? NO
- Verify sender before financial actions? YES
- Device lock enabled? YES
Expected Score: ~80–90 (Well Protected)

---

## Suggested 8-Minute Demo Flow

| Time | Feature | Action |
|---|---|---|
| 0:00 | Login | user@cybershakti.in / CyberShakti@123 |
| 0:30 | F-01 | Paste SBI phishing URL → HIGH RISK |
| 1:00 | F-01 | Paste google.com → SAFE (contrast) |
| 1:30 | F-02 | Paste OTP scam message → HIGH RISK |
| 2:30 | F-02 | Paste safe message → SAFE |
| 3:00 | F-07 | Set all HIGH signals → Mule detected |
| 4:00 | F-07 | Switch to SAFE signals → Clean account |
| 4:30 | F-08 | Type `password` → VERY WEAK |
| 5:00 | F-08 | Type `Tr0ub4dor&3!Zx#9` → VERY STRONG |
| 5:30 | F-10 | Bad habits answers → Score ~25 |
| 6:30 | F-10 | Good habits answers → Score ~85 |
| 7:30 | F-06 | Upload face image → Deepfake verdict |
| 8:00 | Wrap | Show /docs → 30+ production API endpoints |

---

## Key Technical Talking Points

- No cloud APIs — all ML inference runs 100% locally
- 5 trained models: DistilBERT, EfficientNet-B4, XGBoost, LightGBM, TF-IDF
- Production-grade auth: Argon2 + TOTP 2FA + JWT refresh rotation
- Explainable AI: every verdict shows which signals triggered classification
- Indian-context training: UPI, KYC, NPCI, SBI, Aadhaar scam patterns
- Async architecture: Celery task queue for OCR and Deepfake inference
- Dual DB: SQLite (demo) / PostgreSQL+pgvector (production-ready)
