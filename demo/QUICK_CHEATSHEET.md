# CyberShakti — Quick Cheat Sheet (Print This)

## LOGIN
Email: user@cybershakti.in  |  Password: CyberShakti@123

---

## F-01 PHISHING URL — Paste into /detect/phishing-link
DANGER: https://sbi-kyc-update-portal-secure.xyz/login?session=abc123
DANGER: http://hdfc-bank-verify-account.info/netbanking/update
SAFE:   https://www.google.com

---

## F-02 SCAM MESSAGE — Paste into /detect/message-scan
DANGER: Dear Customer, Your SBI bank account has been BLOCKED due to incomplete KYC. Share your OTP immediately to avoid permanent suspension. Act within 24 hours. — SBI Customer Care

DANGER: CONGRATULATIONS! You won Rs 15,00,000 in National Lucky Draw 2026. Pay Rs 500 to claim-prize@hdfc to release funds.

SAFE:   Hi, are you free this weekend? Let me know!

---

## F-07 MULE ACCOUNT — Use /detect/mule-account page
HIGH RISK: Age=New, Velocity=High, Fan-out=Yes, Pass-through=Yes
SAFE:      Age=2yrs+, Velocity=Normal, Fan-out=No, Pass-through=No

---

## F-08 PASSWORD — Use /protect/password-check
WEAK:   password   |  123456
STRONG: Tr0ub4dor&3!Zx#9

---

## F-10 RISK SCORE — Use /assist/risk-score (login needed)
LOW (risky):  2FA=No, Reuse=Yes, Click links=Yes, Verify=No, Lock=No
HIGH (safe):  2FA=Yes, Reuse=No, Click links=No, Verify=Yes, Lock=Yes

---

## API TESTING — Open http://localhost:8000/docs
Use Authorize button > Bearer token from login response
