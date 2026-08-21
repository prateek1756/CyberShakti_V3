# CyberShakti — Product Requirements Document

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-PRD-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-15 |
| **Traces To** | CSHAKTI-PVS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — all content must be consistent with the constitution. Conflicts recorded in `docs/00-decisions.md`. |

---

## Table of Contents

1. [User Personas](#1-user-personas)
2. [User Journeys](#2-user-journeys)
3. [Feature Specifications](#3-feature-specifications)
4. [AI/ML User Interaction Model](#4-aiml-user-interaction-model)
5. [Authentication and Account Flows](#5-authentication-and-account-flows)
6. [Notification and Alert Model](#6-notification-and-alert-model)
7. [Privacy and Consent UX](#7-privacy-and-consent-ux)
8. [Non-Functional Product Requirements](#8-non-functional-product-requirements)

---

## 1. User Personas

These personas are **illustrative**. They represent plausible user archetypes grounded in the target user definition in CSHAKTI-PVS-001 §5. They must be validated and refined during the UI/UX design phase. They do not substitute for real user research.


### Persona 1 — Priya, 34, School Teacher, Pune

| Dimension | Detail |
|---|---|
| **Background** | Secondary school teacher. Uses smartphone daily for UPI payments, WhatsApp, and online banking. |
| **Technical literacy** | Moderate. Comfortable with apps but does not understand terms like "phishing" or "2FA" without explanation. |
| **Primary device** | Android smartphone (mobile browser). Occasional laptop use. |
| **Threat exposure** | Receives frequent suspicious WhatsApp messages. Recently received a fake KYC update SMS. Knows colleagues who have lost money to UPI scams. |
| **Primary use cases** | Check suspicious links before clicking. Verify QR codes before scanning for payment. Understand her overall security posture. |
| **Key pain points** | Cannot tell which messages are scams. No trusted tool to verify a link or QR code quickly. Worried about her parents falling for scam calls. |

---

### Persona 2 — Arjun, 22, Engineering Student, Bengaluru

| Dimension | Detail |
|---|---|
| **Background** | Final-year engineering student. Active on Instagram, Telegram, and Discord. Uses UPI daily. Recently started investing on a stock trading app. |
| **Technical literacy** | High for technology in general. Low for cybersecurity specifically — confident but overconfident. |
| **Primary device** | Smartphone and laptop interchangeably. |
| **Threat exposure** | Has received fake job offer messages on Telegram. Follows investment tip groups that may be scams. Active social media user exposed to fake profiles and impersonation. |
| **Primary use cases** | Check suspicious investment opportunity links. Verify social media profiles before engaging. Check if a screenshot of a "winning notification" is real. Use the AI assistant to understand a new scam pattern. |
| **Key pain points** | Has difficulty distinguishing legitimate investment platforms from scams. No way to quickly check if a profile is real. |

---

### Persona 3 — Kamala, 67, Retired Bank Officer, Chennai

| Dimension | Detail |
|---|---|
| **Background** | Retired. Uses a smartphone for WhatsApp, video calls, and UPI payments. Children set up her banking apps. |
| **Technical literacy** | Low. Comfortable with WhatsApp and calls. Easily confused by unusual app behaviour or unfamiliar requests. |
| **Primary device** | Android smartphone. Uses only mobile browser if she uses a web browser at all. |
| **Threat exposure** | Highest risk profile. Has received calls from people claiming to be bank officials asking for OTPs. Received WhatsApp messages claiming she won a prize. Vulnerable to social engineering. |
| **Primary use cases** | Check a phone number before calling back. Verify a suspicious message forwarded by a relative. Access the Cyber Safety Hub for awareness. |
| **Key pain points** | No way to quickly check if a caller or message is trustworthy. Explanations need to be extremely plain — no jargon. |

---

## 2. User Journeys

Journeys are organised by pillar. They show how a user moves through CyberShakti in response to a real-world trigger. They trace across features to illustrate how the pillars connect.

### Journey 1 — Pillar 1: Receiving a Suspicious Message

**Trigger:** Priya receives a WhatsApp message claiming her bank account will be blocked unless she clicks a link and updates her KYC.

1. Priya opens CyberShakti in her mobile browser.
2. She navigates to **Message & Email Scam Detection (F-02)** and pastes the message text.
3. CyberShakti returns a **High Risk** verdict with a plain-language explanation: "This message uses urgency tactics common in KYC scams. The link domain does not match your bank's official domain."
4. Priya feels confirmed in her suspicion. She copies the link from the message and checks it in **Phishing Link Scanning (F-01)**.
5. F-01 returns a **Critical** verdict: "This URL is on a known phishing list and mimics a major Indian bank's website."
6. Priya deletes the message. She is prompted by CyberShakti to check her **Cyber Risk Score (F-12)**.
7. Her Risk Score reflects that she has used scanning features — her score improves slightly and the explanation notes her proactive behaviour.
8. She shares what she learned with her mother, Kamala, using content from the **Cyber Safety Hub (F-14)**.

---

### Journey 2 — Pillar 2: Protecting a File Before Sharing

**Trigger:** Arjun needs to send sensitive documents (Aadhaar copy, bank statement) to a prospective employer and wants to ensure they are protected.

1. Arjun opens CyberShakti and navigates to **Secure File Encryption (F-10)**.
2. He uploads his documents and sets a strong password.
3. CyberShakti encrypts the files using AES-256-GCM and provides the encrypted files for download.
4. He shares the encrypted files and the password separately with the employer via a different channel.
5. Before setting his encryption password, Arjun uses **Password Security Checker (F-09)** to verify it is strong.
6. The checker returns a **Moderate Risk** verdict on his first attempt with improvement guidance. He strengthens the password and the checker confirms it is now strong.

---

### Journey 3 — Pillar 3: Understanding a Threat and Assessing Posture

**Trigger:** Kamala receives a missed call from an unknown number and is unsure whether to call back.

1. Her daughter helps her open CyberShakti and navigate to **Scam Call Blocking (F-08)**.
2. She enters the phone number. CyberShakti checks it against threat/reputation data.
3. The number returns a **High Risk** verdict: "This number has been reported as associated with fake bank official calls in multiple user reports."
4. Kamala is advised not to call back and to report the number to her bank if contacted again.
5. Her daughter encourages her to check her **Cyber Risk Score (F-12)**. Kamala's score is low — she has not set up 2FA, reuses passwords, and has not completed any security awareness content.
6. The score explanation recommends she explore the **Cyber Safety Hub (F-14)** — specifically the module on scam calls and OTP protection.
7. Kamala reads the daily tip about never sharing OTPs. She shares it with her WhatsApp family group.

---

### Journey 4 — Pillar 4: Building Awareness

**Trigger:** Arjun is curious about a new investment scam pattern he saw on Reddit.

1. He opens the **Cyber Safety Hub (F-14)** and reads a Daily Cyber Safety Tip about cryptocurrency investment scams.
2. He takes the **Cybersecurity Quiz** and scores well on phishing recognition but poorly on investment scam identification.
3. The quiz directs him to an awareness article on "How crypto investment scams work in India."
4. Arjun asks the **AI Cybersecurity Assistant (F-11)** a follow-up question: "How do I verify if a crypto investment platform is legitimate in India?"
5. The assistant provides a grounded response referencing SEBI registration requirements and CERT-In advisories, with a disclaimer that this is AI-generated guidance and he should verify with official sources.

---

## 3. Feature Specifications

All 14 features are specified below. Each specification is complete — no field is left unpopulated.

**Locked classification tiers are used exactly as defined in CSHAKTI-CONST-001 §5.1 and ADR-029. Tiers are not reassigned.**

---

### F-01 — Phishing Link Scanning

| Field | Value |
|---|---|
| **Feature ID** | F-01 |
| **Feature Name** | Phishing Link Scanning |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to submit a suspicious URL so that I can find out whether it is a phishing or malicious link before I click on it.

**Functional Description:**
The user submits a URL. The system performs: URL feature engineering (lexical features, domain characteristics, path analysis), rule-based pre-filtering, threat intelligence lookup against configured sources (ADR-032), and ML classification using the trained XGBoost baseline model (ADR-008). The system returns a risk verdict and a plain-language explanation.

**Phase 1 Implementation Scope:**
URL submission via text input. Feature engineering pipeline. XGBoost classifier (Provisional — ADR-008). Threat intelligence enrichment (sources TBD — ADR-032). Risk verdict output with explanation. 5-level risk severity output.

**Advanced/Future Scope:**
Real-time URL scanning via browser extension (deferred). Automatic link scanning in uploaded messages (enhanced pipeline). Expanded threat intelligence integration. Model retraining pipeline.

**Inputs:** URL string (HTTP/HTTPS). Maximum URL length: TBD during engineering design.

**Outputs:**
- Risk level: Safe / Low Risk / Moderate Risk / High Risk / Critical
- Plain-language explanation (minimum 1 sentence; must state what indicators were found)
- Threat intelligence match indicator (yes/no, source not necessarily disclosed to user)
- Confidence indicator (displayed in user-accessible terms — e.g., "based on known threat data" vs. "based on URL analysis only")

**Edge Cases:**
1. URL with no HTTP/HTTPS scheme — system must normalise or reject with guidance
2. URL that resolves to a redirect chain — system analyses the submitted URL; redirect following is a future enhancement
3. URL not in any threat intelligence database and no phishing features detected — returns Safe with note that absence of detection does not guarantee safety
4. Malformed URL that cannot be parsed — returns an error with user-friendly guidance
5. Very long URL (potential obfuscation) — system must handle without crashing; flag length as a suspicious signal

**Explicit Per-Feature Out-of-Scope:**
- Real-time browser extension integration
- Automatic scanning of links in uploaded messages
- Following redirect chains
- Scanning URLs behind authentication

**Acceptance Criteria:**
- AC-F01-1: Given a URL on a known phishing list (from configured threat intelligence source), the system returns High Risk or Critical verdict within the defined response time target (TBD).
- AC-F01-2: Given a well-known legitimate URL (e.g., sbi.co.in, google.com), the system returns Safe or Low Risk verdict.
- AC-F01-3: Every verdict response includes a non-empty plain-language explanation field.
- AC-F01-4: A malformed URL (e.g., "not a url at all") returns an error response with a user-friendly message — it does not return a risk verdict.
- AC-F01-5: The system returns a response for any valid URL input; it does not crash or time out on edge-case URLs.


---

### F-02 — Message & Email Scam Detection

| Field | Value |
|---|---|
| **Feature ID** | F-02 |
| **Feature Name** | Message & Email Scam Detection |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to paste a suspicious message or email text so that I can find out whether it is a scam before I respond or act on it.

**Functional Description:**
The user pastes or types message/email text. The system preprocesses the text, runs it through the trained NLP classifier (DistilBERT fine-tuned — ADR-009, Provisional), and returns a scam risk verdict with a plain-language explanation identifying what scam indicators were found.

**Phase 1 Implementation Scope:**
Text input (paste or type). Preprocessing pipeline (cleaning, tokenisation). DistilBERT classifier with mandatory TF-IDF + Logistic Regression baseline established first (ADR-009). Risk verdict with explanation. Scam category hint (e.g., "KYC scam", "prize scam", "job scam") where confidence is sufficient.

**Advanced/Future Scope:**
Multilingual detection (Hindi, Tamil, etc.). Automatic extraction from forwarded messages. Real-time email client integration. Continuous model retraining on new scam patterns.

**Inputs:** Free-form text string. Minimum length: TBD. Maximum length: TBD during engineering design.

**Outputs:**
- Risk level: Safe / Low Risk / Moderate Risk / High Risk / Critical
- Plain-language explanation (what indicators triggered the classification)
- Scam category hint (where confidence is sufficient)
- AI disclaimer: "This assessment is based on pattern analysis and may not catch all scams."

**Edge Cases:**
1. Very short message (e.g., "Call me back") — insufficient text for meaningful classification; system returns Low Risk with note that short messages cannot be reliably assessed
2. Message in Hindi or regional language — system notes that Phase 1 analysis is optimised for English; results may be less reliable for non-English text
3. Empty input — system returns validation error before analysis
4. Message that is clearly legitimate (e.g., a known bank's genuine transaction SMS) — system returns Safe with explanation
5. Message containing a URL — system can optionally surface the URL for F-01 analysis; does not automatically scan it

**Explicit Per-Feature Out-of-Scope:**
- Multilingual classification (Phase 1 is English-primary)
- Email client integration
- Automatic scanning of forwarded messages

**Acceptance Criteria:**
- AC-F02-1: Given a text sample matching a known scam pattern (KYC, OTP, prize, job scam), the system returns Moderate Risk, High Risk, or Critical verdict.
- AC-F02-2: Given a plainly benign message (e.g., a genuine transaction confirmation), the system returns Safe or Low Risk.
- AC-F02-3: Every verdict includes a non-empty explanation field identifying specific indicators.
- AC-F02-4: A Hindi-only message triggers a note that Phase 1 analysis is optimised for English, rather than returning a misleadingly confident verdict.
- AC-F02-5: An empty text input returns a validation error — not a risk verdict.
- AC-F02-6: The AI disclaimer is present in every response.

---

### F-03 — Screenshot Scam Scanner

| Field | Value |
|---|---|
| **Feature ID** | F-03 |
| **Feature Name** | Screenshot Scam Scanner |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to upload a screenshot of a suspicious message or notification so that I can find out whether it contains scam content without having to manually retype the text.

**Functional Description:**
User uploads a screenshot image. The system runs PaddleOCR to extract text from the image (ADR-022, Provisional). Extracted text is passed through the F-02 scam NLP classifier pipeline. The system returns a risk verdict with explanation. If OCR confidence is low, the system flags this in the response.

**Phase 1 Implementation Scope:**
Image upload (JPEG, PNG — file size limit TBD). PaddleOCR text extraction. OCR confidence assessment. F-02 NLP classification on extracted text. Risk verdict with explanation and OCR quality indicator.

**Advanced/Future Scope:**
Visual scam indicator detection beyond text (logos, layout patterns). Support for additional image formats. Improved multilingual OCR. Video screenshot support.

**Inputs:** Image file (JPEG or PNG). File size limit: TBD during engineering design.

**Outputs:**
- Extracted text (shown to user for transparency)
- Risk level: Safe / Low Risk / Moderate Risk / High Risk / Critical
- Plain-language explanation
- OCR quality indicator: "Text extracted clearly" / "Text extraction may be incomplete — results may be less reliable"
- AI disclaimer

**Edge Cases:**
1. Screenshot with no readable text (e.g., a photo of a landscape) — OCR returns empty/near-empty text; system returns "No scam-related text detected in this image" — not a Safe verdict implying safety
2. Very low resolution screenshot — OCR quality warning displayed; verdict reliability flagged
3. Screenshot containing both English and Hindi text — English portion is analysed; Hindi portion may be missed; language limitation note displayed
4. Oversized image file — system rejects with a clear file size error before attempting OCR
5. Screenshot of a legitimate document (e.g., a real bank statement) — classified as Safe with explanation; OCR text shown so user can verify extraction accuracy

**Explicit Per-Feature Out-of-Scope:**
- Visual/layout-based scam detection (beyond OCR + NLP)
- Video analysis
- PDF scanning

**Acceptance Criteria:**
- AC-F03-1: Given a screenshot of a known scam message (WhatsApp format), the system extracts readable text and returns a Moderate Risk or higher verdict.
- AC-F03-2: The extracted text is displayed to the user in the response so they can verify OCR accuracy.
- AC-F03-3: A screenshot with no extractable text returns "No scam-related text detected" — not a Safe risk verdict.
- AC-F03-4: A file exceeding the size limit returns a clear validation error before processing.
- AC-F03-5: Every response includes the OCR quality indicator and AI disclaimer.


---

### F-04 — QR Code Scam Scanner

| Field | Value |
|---|---|
| **Feature ID** | F-04 |
| **Feature Name** | QR Code Scam Scanner |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to scan or upload a QR code image so that I can find out whether it leads to a malicious or scam destination before I scan it with my camera.

**Functional Description:**
User uploads a QR code image. The system decodes the QR code using a standard library (ADR-023). If the decoded content is a URL, it is routed to the F-01 phishing URL analysis pipeline. If the decoded content is not a URL, the system identifies the content type and returns an appropriate response. Risk verdict returned with explanation.

**Phase 1 Implementation Scope:**
QR image upload. QR decode. URL routing to F-01. Non-URL content type identification. Risk verdict and explanation. No separate ML model for QR images.

**Advanced/Future Scope:**
Camera-based real-time QR scanning (requires mobile app). QR code generation verification.

**Inputs:** QR code image (JPEG, PNG). File size limit: TBD.

**Outputs:**
- Decoded content (shown to user — URL, contact card, WiFi credentials, plain text, etc.)
- For URL content: full F-01 risk verdict and explanation
- For non-URL content: content type identification and a note that CyberShakti's URL analysis does not apply
- Error response for unreadable QR codes

**Edge Cases:**
1. QR code containing a contact card (vCard) — system identifies as contact data, notes that URL phishing analysis does not apply, advises caution with unknown contacts
2. QR code containing WiFi credentials — system identifies content type, notes that CyberShakti cannot assess WiFi network safety, advises caution
3. Blurry or damaged QR code that cannot be decoded — system returns a clear error: "Unable to read QR code. Please try a clearer image."
4. QR code containing a URL with no HTTP scheme — normalised before F-01 analysis
5. Multiple QR codes in a single image — Phase 1 decodes the most prominent/first QR code detected; multi-code support is a future enhancement

**Explicit Per-Feature Out-of-Scope:**
- Camera-based real-time QR scanning
- WiFi network safety assessment
- Contact/vCard safety verification

**Acceptance Criteria:**
- AC-F04-1: Given a QR code image encoding a known phishing URL, the system decodes the URL, routes it through F-01, and returns a High Risk or Critical verdict.
- AC-F04-2: Given a QR code encoding a legitimate URL (e.g., a major brand's official site), the system returns Safe or Low Risk.
- AC-F04-3: Given a QR code encoding non-URL content (contact card, WiFi), the system identifies the content type and returns an appropriate non-risk response without applying URL analysis.
- AC-F04-4: An unreadable QR code returns a clear error message — not a risk verdict.
- AC-F04-5: The decoded content is shown to the user in all cases.

---

### F-05 — Fake Profile Verification

| Field | Value |
|---|---|
| **Feature ID** | F-05 |
| **Feature Name** | Fake Profile Verification |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | Advanced MVP |

**User Story:**
As an Indian internet user, I want to submit details about a social media profile so that I can assess whether it shows indicators of being a fake or suspicious account before I engage with it.

**Functional Description:**
User submits observable profile signals (profile URL and/or observable characteristics such as account age indicators, follower/following ratio hints, profile completeness signals, content consistency). The system applies a risk assessment model (XGBoost / LightGBM — ADR-011, Provisional) to return a fake-profile risk assessment. This feature assesses risk — it does not verify identity and must never claim to do so.

**Phase 1 Implementation Scope:**
Profile signal input form. Feature engineering on submitted signals. XGBoost/LightGBM risk assessment. Risk verdict with explanation. Explicit "risk assessment only — not identity verification" disclaimer in every response.

**Advanced/Future Scope:**
API-based profile data retrieval (subject to platform API terms). Automated signal extraction from profile URL. More granular signal set.

**Inputs:** Profile URL (optional) and/or manually entered observable signals (account age estimate, follower/following count, profile photo type, content pattern, etc.) — exact signal set defined during engineering design.

**Outputs:**
- Risk level: Safe / Low Risk / Moderate Risk / High Risk / Critical
- Plain-language explanation of which signals contributed to the verdict
- Mandatory disclaimer: "This is a risk assessment only. CyberShakti cannot verify identity and this result should not be treated as definitive proof that a profile is fake or genuine."

**Edge Cases:**
1. User submits only a profile URL with no additional signals — system attempts feature extraction from URL alone; notes that limited signals reduce assessment confidence
2. Profile URL is inaccessible (private account, deleted) — system cannot assess; returns "Unable to access profile data" response
3. User submits signals for a well-established verified account — should return Low Risk or Safe
4. User submits signals for an account that is new, has few followers, and limited content — may return Moderate Risk; explanation clarifies these are statistical risk indicators, not proof of fraud
5. User submits a signal set that is insufficient for any meaningful assessment — system returns "Insufficient signals for assessment" rather than a misleading verdict

**Explicit Per-Feature Out-of-Scope:**
- Identity verification of any kind
- Platform API integration for automated signal retrieval
- Legal or law enforcement reporting

**Acceptance Criteria:**
- AC-F05-1: Every response includes the identity-verification disclaimer in a visible position.
- AC-F05-2: A profile submission with clearly high-risk signals (e.g., new account, zero posts, very high following, suspicious name pattern) returns Moderate Risk or higher.
- AC-F05-3: A well-established public figure's official profile submitted with full signals returns Low Risk or Safe.
- AC-F05-4: An insufficient signal submission returns an "insufficient signals" response rather than a risk verdict.
- AC-F05-5: The explanation field identifies which specific submitted signals contributed to the risk level — it is never empty.


---

### F-06 — Deepfake Detection

| Field | Value |
|---|---|
| **Feature ID** | F-06 |
| **Feature Name** | Deepfake Detection |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | **Research/Experimental** |

> **Research/Experimental Notice:** F-06 is part of the Phase 1 product definition and research/training scope. It must NOT be represented as production-grade or guaranteed functionality. All outputs must communicate experimental status and uncertainty to the user. See CSHAKTI-CONST-001 §4 and ADR-010.

**User Story:**
As an Indian internet user, I want to upload an image or short video so that I can get an assessment of whether it may be AI-generated or manipulated, helping me evaluate its authenticity.

**Functional Description:**
User uploads an image or short video. The system preprocesses the media and runs a CNN-based classifier (EfficientNet or Xception — model architecture selected by empirical evaluation, ADR-010). The system returns a risk assessment with a confidence indicator. All output must include the Research/Experimental disclaimer and communicate uncertainty. This feature must not be represented as definitive deepfake detection.

**Phase 1 Implementation Scope:**
Image upload. Short video upload (duration limit TBD). Preprocessing (face detection, frame extraction for video). CNN inference. Risk assessment output with Research/Experimental disclaimer and confidence uncertainty communication. This feature is in research/training scope — it may be presented in the UI with an "Experimental" label.

**Advanced/Future Scope:**
Production-grade model after empirical validation. Video length support expansion. Audio deepfake detection. Adversarial robustness improvements.

**Inputs:** Image file (JPEG, PNG) or short video file (MP4 — duration limit TBD). File size limit: TBD.

**Outputs:**
- Risk assessment: indicators of synthetic generation present / not detected / uncertain
- Confidence level communicated in plain language (e.g., "Low confidence — limited analysis possible on this media")
- Mandatory Research/Experimental disclaimer: "This feature is experimental. Results are not reliable enough to be treated as definitive evidence of deepfake manipulation. False positives and false negatives are expected."
- Explanation of what signals were analysed

**Edge Cases:**
1. Image with no detectable face — system cannot apply face-based deepfake analysis; returns "No face detected — deepfake analysis requires a clear face in the image"
2. Image is a cartoon or illustration — clearly not a photographic deepfake; system should not misclassify; returns appropriate response
3. Highly compressed or very low resolution image — analysis quality is degraded; confidence indicator reflects this
4. Very short video (under 1 second) — insufficient frames for reliable analysis; system notes this
5. Media file that is genuine but unusual (professional photo editing, heavy filter) — may produce false positives; disclaimer is critical

**Explicit Per-Feature Out-of-Scope:**
- Definitive deepfake determination
- Audio deepfake detection
- Legal evidence quality output
- Real-time video stream analysis

**Acceptance Criteria:**
- AC-F06-1: Every response includes the Research/Experimental disclaimer in a prominent, user-visible position.
- AC-F06-2: An image with no detectable face returns "No face detected" — not a deepfake risk verdict.
- AC-F06-3: The response always includes a confidence level communicated in plain language.
- AC-F06-4: A file exceeding the size limit returns a validation error before processing.
- AC-F06-5: The explanation field describes what signals were analysed — it is never empty.
- AC-F06-6: The feature is labelled "Experimental" in the UI in a way that is visible to users before they submit media.

---

### F-07 — Mule Account Detection

| Field | Value |
|---|---|
| **Feature ID** | F-07 |
| **Feature Name** | Mule Account Detection |
| **Pillar** | Pillar 1 — Detect & Analyze |
| **Phase 1 Tier** | **Research/Experimental** |

> **Research/Experimental Notice:** F-07 is part of the Phase 1 product definition and research/training scope. Training datasets represent cryptocurrency transaction networks, not bank accounts (ADR-024). Outputs must NOT be presented as production-grade mule account detection. All outputs must communicate experimental status, dataset limitations, and uncertainty. See CSHAKTI-CONST-001 §4, ADR-011, ADR-024.

**User Story:**
As an Indian internet user or financial institution representative (informational use only), I want to submit account-related signals so that I can get a research-based assessment of whether an account shows patterns associated with money mule activity.

**Functional Description:**
User submits account signals (transaction pattern indicators, account age, activity patterns — exact signal set defined during engineering design). The system applies XGBoost with NetworkX-derived graph features (ADR-011) to return a risk assessment. All output includes dataset limitation disclaimer and Research/Experimental notice. This feature does not make accusations — it produces a risk assessment based on statistical patterns.

**Phase 1 Implementation Scope:**
Signal input form (exact signals defined in engineering design). Feature engineering including graph features where applicable. XGBoost + NetworkX classifier. Risk assessment with full disclaimer set. This feature is in research/training scope.

**Advanced/Future Scope:**
Graph Neural Network model (PyTorch Geometric) after Phase 1 research baseline established. Bank-account-specific dataset when available. Integration with financial intelligence feeds.

**Inputs:** Account signal set (to be defined during engineering design — may include: account age, transaction frequency indicators, counterparty diversity, etc.).

**Outputs:**
- Risk assessment: low / moderate / high indicators of mule account patterns
- Mandatory disclaimer set:
  1. Research/Experimental: "This feature is experimental and should not be used as the basis for any legal, financial, or regulatory action."
  2. Dataset limitation: "This model was trained on research datasets representing cryptocurrency transaction networks, not real-world bank accounts. Its applicability to bank account mule detection has not been validated."
  3. General: "This is a statistical risk indicator only."

**Edge Cases:**
1. Incomplete signal set — system returns "Insufficient signals for assessment" rather than a misleading verdict
2. Account signals that match a new/inactive account — may produce false positives; disclaimer covers this
3. User attempts to use this feature for actual fraud investigation or legal evidence — disclaimer explicitly states this is not appropriate
4. All signals are within normal range — returns Low Risk with explanation of why
5. Extreme signal values (outliers) — system handles gracefully without crashing

**Explicit Per-Feature Out-of-Scope:**
- Legal evidence output
- Integration with banking systems or financial intelligence
- Real-time transaction monitoring
- Definitive mule account determination

**Acceptance Criteria:**
- AC-F07-1: Every response includes all three mandatory disclaimers in visible positions.
- AC-F07-2: An incomplete signal set returns "Insufficient signals" — not a risk verdict.
- AC-F07-3: The feature is labelled "Experimental" in the UI before users submit signals.
- AC-F07-4: The response explanation describes which input signals contributed to the risk level.
- AC-F07-5: The system does not crash on extreme or outlier input values.


---

### F-08 — Scam Call Blocking

| Field | Value |
|---|---|
| **Feature ID** | F-08 |
| **Feature Name** | Scam Call Blocking |
| **Pillar** | Pillar 2 — Protect |
| **Phase 1 Tier** | Advanced MVP |

> **Phase 1 Scope Note:** F-08 Phase 1 is in-app phone-number lookup and risk assessment only. Android OS-level automatic call blocking is deferred (ADR-018, ADR-025).

**User Story:**
As an Indian internet user, I want to enter a phone number I received a suspicious call from so that I can find out whether it is associated with known scam activity before I call back or engage with the caller.

**Functional Description:**
User manually enters or pastes a phone number. The system looks up the number against configured threat/reputation data sources (ADR-032) and returns a risk assessment. No OS-level call interception occurs in Phase 1.

**Phase 1 Implementation Scope:**
Phone number input (manual entry or paste). Input validation and normalisation (Indian number formats: +91, 0xx, 10-digit). Threat/reputation data lookup. Risk verdict with explanation. User-reported scam number integration (basic — if implemented in Phase 1).

**Advanced/Future Scope:**
Android OS-level automatic call screening. Real-time call ID integration. Automated scam number crowdsourcing. SMS spam detection integration.

**Inputs:** Phone number string. Indian number formats supported: 10-digit, +91 prefix, 0xx format.

**Outputs:**
- Risk level: Safe / Low Risk / Moderate Risk / High Risk / Critical
- Plain-language explanation (e.g., "This number has been reported as associated with fake bank official impersonation calls")
- Data source indicator (e.g., "Based on user reports" / "Based on threat intelligence database")
- Disclaimer: "Risk assessments are based on available data and may not reflect the current status of this number."

**Edge Cases:**
1. Number not in any threat database and no user reports — returns Safe/Low Risk with note that absence of data does not confirm safety
2. Invalid phone number format — returns validation error with guidance on correct format
3. International number (non-Indian) — system notes that threat data coverage is primarily India-focused; assessment may be limited
4. Emergency service numbers (100, 112, etc.) — system should never return a risk verdict for emergency numbers; hard-coded exclusion
5. Number that was previously flagged but has been cleared — reflects most recent available data with timestamp where possible

**Explicit Per-Feature Out-of-Scope:**
- Android OS-level call blocking
- Real-time call interception
- SMS content analysis

**Acceptance Criteria:**
- AC-F08-1: Given a phone number on a known scam list (from configured threat source), the system returns Moderate Risk or higher.
- AC-F08-2: An emergency service number (100, 112, 108, etc.) never returns a risk verdict — it returns a "this is an emergency service number" response.
- AC-F08-3: An invalid number format returns a validation error with formatting guidance.
- AC-F08-4: Every verdict includes the data source indicator and disclaimer.
- AC-F08-5: A number with no threat data returns Safe or Low Risk with an explicit note that absence of data does not confirm safety.

---

### F-09 — Password Security Checker

| Field | Value |
|---|---|
| **Feature ID** | F-09 |
| **Feature Name** | Password Security Checker |
| **Pillar** | Pillar 2 — Protect |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to check a password I am considering using so that I can understand how strong it is and how to improve it, without my password being stored or transmitted.

**Functional Description:**
User enters a password into the checker (this is for assessment purposes — users should not enter their actual live account passwords). The system evaluates the password client-side or via a secure server-side assessment: entropy calculation, length check, character diversity analysis, common password detection (against a curated list), and known-breach indicator (via k-anonymity technique against a breach database if integrated). Returns a security verdict with specific improvement guidance. Password is never stored.

**Phase 1 Implementation Scope:**
Password input field (masked). Entropy calculation. Length check. Character diversity check. Common password pattern detection. Security verdict (5-level) with specific plain-language improvement recommendations. No password transmitted in plaintext to server — if server-side assessment is used, k-anonymity technique must be applied. No password stored under any circumstances.

**Advanced/Future Scope:**
Integration with password manager recommendations. Passphrase strength assessment. Breach database integration (HaveIBeenPwned API via k-anonymity if not included in Phase 1).

**Inputs:** Password string (entered by user for assessment — not their live password).

**Outputs:**
- Security level: Very Weak / Weak / Moderate / Strong / Very Strong (aligned to Safe–Critical model)
- Specific improvement recommendations (e.g., "Add uppercase letters", "Increase length to at least 12 characters", "Avoid common words")
- Entropy score (shown as a plain-language descriptor, not a raw number)
- Clear notice: "Do not enter your actual account password here. This tool is for assessing password strength before you set a password."

**Edge Cases:**
1. Empty password — validation error before assessment
2. Password that is purely numeric (PIN-style) — flagged as Very Weak with explanation
3. Password that is a known common password (e.g., "password123") — flagged immediately as Very Weak
4. Very long password (passphrase) — should score well if entropy is high; system handles gracefully
5. Password containing only spaces — validation error or Very Weak rating with explanation

**Explicit Per-Feature Out-of-Scope:**
- Storing passwords
- Transmitting passwords in plaintext
- Checking passwords against live account systems

**Acceptance Criteria:**
- AC-F09-1: "password123" returns a Very Weak verdict.
- AC-F09-2: A random 16-character mixed-case alphanumeric+symbol password returns Strong or Very Strong.
- AC-F09-3: Every verdict includes at least one specific, actionable improvement recommendation.
- AC-F09-4: The "do not enter your actual account password" notice is displayed before and after assessment.
- AC-F09-5: An empty password input returns a validation error — not a security verdict.
- AC-F09-6: No password value is stored in any database or log at any point.


---

### F-10 — Secure File Encryption

| Field | Value |
|---|---|
| **Feature ID** | F-10 |
| **Feature Name** | Secure File Encryption |
| **Pillar** | Pillar 2 — Protect |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to encrypt a sensitive file with a password so that I can share or store it safely, knowing only someone with the password can access it.

**Functional Description:**
User uploads a file and sets an encryption password. The system derives an encryption key from the password using Argon2id (ADR-021), encrypts the file using AES-256-GCM (ADR-021), and provides the encrypted file for download. Decryption flow: user uploads the encrypted file and provides the password; system decrypts and provides the original file for download. Original plaintext file is not permanently stored server-side. Encryption/decryption parameters (nonce, salt) are embedded in the encrypted file output.

**Phase 1 Implementation Scope:**
File upload (supported types and size limit TBD during engineering design). Password input for encryption. Argon2id key derivation (parameters TBD — ADR-026). AES-256-GCM encryption. Encrypted file download. Decryption flow (encrypted file upload + password → decrypted file download). No permanent server-side storage of plaintext files.

**Advanced/Future Scope:**
Folder/batch encryption. Key-based encryption (public key infrastructure). Secure file sharing links. Cloud storage integration.

**Inputs:**
- Encryption: file + encryption password
- Decryption: encrypted file + decryption password

**Outputs:**
- Encryption: encrypted file download + confirmation message
- Decryption: original file download OR clear error if password is wrong
- Warning: "Keep your encryption password safe. If you lose it, your encrypted file cannot be recovered."

**Edge Cases:**
1. Wrong password on decryption — AES-256-GCM authentication tag failure; system returns "Incorrect password or corrupted file" — it does not return partial or garbled content
2. File type that may contain malware — system must validate file type and may apply basic content checks before encryption; file content is encrypted as-is
3. File size exceeds limit — validation error before upload
4. User attempts to decrypt a file that was not encrypted by CyberShakti — AES-256-GCM tag verification will fail; returns appropriate error
5. Network interruption during upload — system handles gracefully; upload must be restarted

**Explicit Per-Feature Out-of-Scope:**
- Permanent cloud storage of encrypted files
- Secure sharing links
- Key management infrastructure
- Encrypting entire folders in Phase 1

**Acceptance Criteria:**
- AC-F10-1: A file encrypted with a password can be successfully decrypted with the same password and produces the original file with no data corruption.
- AC-F10-2: Attempting to decrypt with the wrong password returns an error — it does not return any file content.
- AC-F10-3: No plaintext version of the uploaded file persists on the server after the encrypted download is provided.
- AC-F10-4: The password-loss warning is displayed prominently before and after encryption.
- AC-F10-5: A file exceeding the size limit returns a validation error before any processing occurs.

---

### F-11 — AI Cybersecurity Assistant

| Field | Value |
|---|---|
| **Feature ID** | F-11 |
| **Feature Name** | AI Cybersecurity Assistant |
| **Pillar** | Pillar 3 — Assist & Respond |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to ask cybersecurity questions in plain language so that I can get grounded, understandable guidance about threats, how to stay safe, and what my CyberShakti results mean.

**Functional Description:**
Conversational AI assistant. User submits a question or message. The system embeds the query, retrieves relevant content from the CyberShakti knowledge base via pgvector similarity search (RAG pipeline), constructs a grounded prompt, and calls the configured LLM API (provider TBD — ADR-013 Open) to generate a response. Response is grounded in retrieved content. All responses include AI disclaimer. The assistant must not fabricate threat intelligence, regulatory obligations, or security facts not in the knowledge base.

**Phase 1 Implementation Scope:**
Text-based conversational interface. Query embedding and retrieval (pgvector). LLM API call with retrieved context (provider TBD). Response display with AI disclaimer. Basic conversation history within a session (not persisted across sessions in Phase 1). Knowledge base: curated CyberShakti cybersecurity content, Indian threat taxonomy, feature explanations.

**Advanced/Future Scope:**
Persistent conversation history. Voice input/output. Context-aware follow-up (awareness of user's recent scan results). Expanded knowledge base. Proactive threat alerts via assistant.

**Inputs:** Natural language text query. Maximum input length: TBD.

**Outputs:**
- Natural language response grounded in knowledge base
- Mandatory AI disclaimer: "This response is generated by an AI assistant and may not be fully accurate. Do not make important security decisions based solely on this guidance. Verify critical information with official sources."
- Source references where the knowledge base content supports it

**Edge Cases:**
1. Question outside the cybersecurity domain (e.g., "What is the weather today?") — assistant politely declines and redirects to cybersecurity topics
2. Question asking for specific legal advice (e.g., "Am I legally liable for...") — assistant notes it cannot provide legal advice and recommends consulting a qualified lawyer
3. Question in Hindi — if the LLM supports Hindi (provider-dependent), response in Hindi is acceptable; if not, the assistant responds in English and notes the language limitation
4. Query that cannot be answered from the knowledge base — assistant acknowledges the limitation rather than fabricating an answer
5. Very long or complex multi-part question — assistant addresses the most relevant parts and notes if some aspects are outside its knowledge

**Explicit Per-Feature Out-of-Scope:**
- Legal, financial, or medical advice
- Real-time threat intelligence lookup (Phase 1 — knowledge base is curated, not live-updating)
- Persistent conversation history across sessions (Phase 1)

**Acceptance Criteria:**
- AC-F11-1: Every response includes the AI disclaimer in a visible position.
- AC-F11-2: A question about a common Indian scam type (e.g., "What is a KYC scam?") produces a relevant, grounded response that references content from the knowledge base.
- AC-F11-3: A question requesting legal advice triggers the "cannot provide legal advice" response rather than a fabricated legal answer.
- AC-F11-4: A question completely outside cybersecurity domain triggers a polite out-of-scope response.
- AC-F11-5: The assistant does not fabricate threat intelligence statistics, regulatory obligations, or security facts not supported by the knowledge base.
- AC-F11-6: F-11 implementation is blocked until ADR-013 (LLM provider) is resolved.


---

### F-12 — Cyber Risk Score

| Field | Value |
|---|---|
| **Feature ID** | F-12 |
| **Feature Name** | Cyber Risk Score |
| **Pillar** | Pillar 3 — Assist & Respond |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to see a personalised score that reflects my cybersecurity posture so that I can understand how well protected I am and know what to do to improve.

**Functional Description:**
The system computes a Cyber Risk Score for the authenticated user using an explainable weighted risk engine (ADR-012). The score draws from a controlled Phase 1 signal set (ADR-020). Every score is accompanied by a breakdown identifying which signals contributed to it and what the user can do to improve their score. The score is not an ML prediction — it is a deterministic weighted calculation over defined signals.

**Phase 1 Signal Set (Controlled — not open-ended):**

*In-app signals (automatically collected):*
- Number of scans performed (link, message, screenshot, QR, call)
- Threat detections encountered (high/critical verdicts received)
- Password Security Checker usage and result (strong/weak)
- File Encryption usage
- 2FA enabled on CyberShakti account (yes/no)
- Account password strength (assessed at registration/change)

*User-reported security posture signals (self-declared — not verified):*
- "Do you reuse passwords across accounts?" (yes/no/sometimes)
- "Have you enabled 2FA on your primary banking app?" (yes/no/unsure)
- "Do you regularly update your device OS?" (yes/no/sometimes)
- "Have you been affected by a digital fraud in the past 12 months?" (yes/no/prefer not to say)

**Note:** The exact signal weights are defined during engineering design and are configurable. No additional signals may be added to Phase 1 without a recorded change decision.

**Phase 1 Implementation Scope:**
Signal collection from in-app activity. User-reported signal questionnaire. Weighted engine calculation. Score display (numerical + label). Score breakdown (which signals contributed, positively or negatively). Score change history (basic — shows if score improved or worsened over time). Improvement recommendations linked to specific low-scoring signals.

**Advanced/Future Scope:**
ML-based risk prediction (future phase). External signal integration (with user consent). More granular signal set. Score benchmarking against anonymised peer groups.

**Inputs:** User's in-app activity data + user-reported signal responses.

**Outputs:**
- Numerical score (range TBD — e.g., 0–100) + label (e.g., Low / Moderate / Good / Strong — exact labels TBD during engineering design)
- Breakdown: list of contributing signals with their individual contribution (positive or negative)
- Improvement actions: specific, actionable steps for the lowest-scoring signals
- Disclaimer: "Your Cyber Risk Score is based on the information available within CyberShakti and your self-reported responses. It is an indicator of security posture, not a guarantee of protection."

**Edge Cases:**
1. New user with no in-app activity and no signal responses — returns a baseline score with a message prompting them to complete the onboarding questionnaire and start using features
2. User who declines to answer all user-reported signals — score is calculated from in-app signals only; note displayed that score accuracy improves with self-reported data
3. User who reports being affected by fraud — this signal should not dramatically penalise the score (being a victim is not equivalent to poor security behaviour); it informs the score moderately
4. Score is at maximum — system acknowledges strong posture and recommends maintaining behaviour rather than implying invulnerability
5. User with high threat detections (many scans, many high-risk results) — high detection activity can reflect active use rather than poor posture; weighting must be designed carefully

**Explicit Per-Feature Out-of-Scope:**
- ML-based risk prediction
- External data integration (e.g., credit bureau, bank data)
- Score comparison against other users (public leaderboard)
- Guaranteed security assessment

**Acceptance Criteria:**
- AC-F12-1: A user who has enabled 2FA, used the password checker with a strong result, and performed multiple scans receives a higher score than a user with no activity.
- AC-F12-2: Every score display includes the full signal breakdown — no score is displayed without an explanation.
- AC-F12-3: A new user with no activity and no responses receives a baseline score with an onboarding prompt — not an error.
- AC-F12-4: The score disclaimer is displayed with every score presentation.
- AC-F12-5: Completing the user-reported questionnaire changes the score in a direction consistent with the responses given (e.g., reporting 2FA enabled on banking app improves the score).
- AC-F12-6: The signal set used is exactly the Phase 1 controlled set defined above — no additional signals are introduced without a recorded change decision.

---

### F-13 — Location-Based Scam Alerts

| Field | Value |
|---|---|
| **Feature ID** | F-13 |
| **Feature Name** | Location-Based Scam Alerts |
| **Pillar** | Pillar 3 — Assist & Respond |
| **Phase 1 Tier** | Advanced MVP |

**User Story:**
As an Indian internet user, I want to see scam and fraud alerts relevant to my location so that I can be aware of threats that are active in my area.

**Functional Description:**
The system surfaces scam and fraud alerts tagged to geographic locations (city/district/region level). User provides their location (self-reported city selection or with explicit consent for browser location access at city/region precision). The system queries the threat database using PostGIS geospatial queries (ADR-007) to return alerts relevant to the user's location. No real-time precise location tracking.

**Phase 1 Implementation Scope:**
Location input (user-selected city/region from a dropdown, or browser geolocation API with explicit consent — city/region precision only). PostGIS geospatial query against location-tagged threat database. Alert display (alert type, description, date, severity). No persistent precise location storage. Location used for query only — not stored beyond the session unless user consents.

**Advanced/Future Scope:**
Automatic location-based push notifications. Hyperlocal (neighbourhood-level) alerts. User-submitted scam reports with location tagging. Integration with CERT-In and police cyber cell alert feeds.

**Inputs:** User's city/region (self-selected or browser geolocation at city precision with explicit consent).

**Outputs:**
- List of active scam alerts for the user's location (alert title, description, scam type, date reported, severity)
- "No recent alerts for your location" message if none found
- Data freshness indicator (when alerts were last updated)
- Disclaimer: "Alerts are based on available reported data and may not represent all active scams in your area."

**Edge Cases:**
1. User in a location with no alerts in the database — returns "No recent alerts for your area" — not an error
2. User denies browser location permission — system falls back to self-selected city dropdown
3. User is in a location not covered by the threat database — same as above; no alerts returned
4. Alert database has not been updated recently — data freshness indicator shows last update date; stale alerts are flagged
5. User selects a very broad region — returns alerts for that region with a note that alerts are at region level

**Explicit Per-Feature Out-of-Scope:**
- Precise (street-level) location tracking
- Persistent location storage without consent
- Real-time push notifications (Phase 1 — displayed on-demand in the app)
- User-submitted scam reports (Phase 1)

**Acceptance Criteria:**
- AC-F13-1: Selecting a major Indian metropolitan area (Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata, Pune) returns at least one alert if alerts exist for that area in the database.
- AC-F13-2: A location with no alerts returns "No recent alerts" — not an error or empty screen.
- AC-F13-3: Browser geolocation is requested only with an explicit user consent prompt explaining why location is needed.
- AC-F13-4: Location data is not stored persistently without explicit user consent.
- AC-F13-5: Every alert display includes the data freshness indicator and disclaimer.


---

### F-14 — Cyber Safety Hub

| Field | Value |
|---|---|
| **Feature ID** | F-14 |
| **Feature Name** | Cyber Safety Hub |
| **Pillar** | Pillar 4 — Learn & Prevent |
| **Phase 1 Tier** | Core MVP |

**User Story:**
As an Indian internet user, I want to access cybersecurity awareness content, daily tips, and quizzes so that I can learn how to recognise scams and protect myself from common digital threats.

**Functional Description:**
A curated content hub containing India-relevant cybersecurity awareness content. Content is manually curated and reviewed for accuracy. Sub-features include: Daily Cyber Safety Tips, Cybersecurity Quiz, awareness articles, and preventive guidance. All content must be factually accurate — no fabricated threat claims. The Cybersecurity Quiz is a sub-feature of F-14, not a separate top-level feature.

**Phase 1 Implementation Scope:**
Daily Cyber Safety Tips (one tip per day, cycling through a curated set). Cybersecurity Quiz (multiple-choice questions on Indian cyberthreat patterns). Awareness articles (curated set covering major Indian threat categories). Preventive guidance pages (what to do if you receive a suspicious call, message, etc.).

**Advanced/Future Scope:**
User progress tracking. Certificate of completion. Community threat reporting integration. Regional language content. Video content.

**Inputs:** No user-submitted input for content consumption. Quiz answers for scoring.

**Outputs:**
- Daily tip (text + brief explanation)
- Quiz results (score + correct answers with explanations)
- Awareness articles (text content)
- Preventive guidance content

**Edge Cases:**
1. User has seen all available daily tips (cycle completed) — tips cycle back to the beginning or a new set is loaded; user is not shown an empty state
2. User scores 100% on quiz — congratulatory message with a recommendation to explore advanced content
3. User scores very low on quiz — encouraging message with links to relevant awareness articles (no shaming)
4. Content contains outdated threat information — content must have a review date and a process for updating; stale content is flagged for review
5. User accesses Hub without an account — awareness content and tips are accessible; quiz may require login to track scores

**Explicit Per-Feature Out-of-Scope:**
- User-generated content
- Community forums
- Video content (Phase 1)
- Regional language content (Phase 1)

**Acceptance Criteria:**
- AC-F14-1: A Daily Cyber Safety Tip is displayed on the hub home page every day; the same tip is not displayed on consecutive days if the tip set contains more than one tip.
- AC-F14-2: The Cybersecurity Quiz presents at minimum 10 questions covering at least 3 different Indian threat categories.
- AC-F14-3: Every quiz question displays the correct answer and a brief explanation after the user answers.
- AC-F14-4: Awareness articles cover at minimum: UPI fraud, WhatsApp scams, OTP theft, phishing links, and scam calls — the primary Indian threat categories from the problem statement.
- AC-F14-5: All content (tips, quiz questions, articles) is reviewed for factual accuracy before publication. No content makes unsupported threat statistics claims.

---

## 4. AI/ML User Interaction Model

This section governs how users experience AI/ML outputs across all features. It applies to all features that produce risk assessments, classifications, or AI-generated content.

### 4.1 Confidence Display

- Where the system has high confidence in a verdict based on threat intelligence match (e.g., known phishing URL), confidence is communicated as: "Based on known threat data."
- Where the verdict is based primarily on model classification without a direct threat intelligence match, this is communicated as: "Based on pattern analysis."
- Where confidence is degraded (e.g., insufficient input data, OCR quality issues), this is explicitly communicated in user-accessible language: "Limited analysis — result may be less reliable."
- Raw probability scores or model confidence percentages are NOT displayed to users directly. They are translated into plain-language confidence descriptors.

### 4.2 Plain-Language Explanation Requirement

Every risk verdict from every feature must include a plain-language explanation that:
- States what was found (e.g., "This URL matches patterns commonly used in phishing sites targeting Indian banks")
- States what it means for the user (e.g., "You should not click this link or enter any personal information on this site")
- Is understandable without any technical background
- Avoids jargon unless the jargon is immediately explained

An explanation field must never be empty. A verdict without an explanation is a product defect.

### 4.3 Required Disclaimer Language

The following disclaimers apply to all AI/ML features. They must appear in visible positions — not buried in footer text or tooltips that require user action to access.

**Standard risk assessment disclaimer (F-01, F-02, F-03, F-04, F-05, F-08):**
> "This assessment is based on available data and pattern analysis. It may not detect all threats. Use this as one input to your decision — not as the only factor."

**AI assistant disclaimer (F-11):**
> "This response is generated by an AI assistant and may not be fully accurate. Do not make important security decisions based solely on this guidance. Verify critical information with official sources."

**Research/Experimental disclaimer (F-06, F-07):**
> "This feature is experimental. Results are not reliable enough to be treated as definitive. False positives and false negatives are expected. Do not use this as the basis for any legal, financial, or regulatory action."

**Cyber Risk Score disclaimer (F-12):**
> "Your Cyber Risk Score is an indicator of security posture based on available signals. It is not a guarantee of protection."

### 4.4 Research/Experimental Feature Presentation

- F-06 and F-07 must be visually labelled "Experimental" in the UI in a way that is prominent before the user submits any input.
- The experimental label must appear on the feature entry point, not only on the results page.
- Users must not be able to reach the results page without having been exposed to the experimental label.

### 4.5 What the System Must Never Claim

Consistent with CSHAKTI-CONST-001 §3.2, no feature output, tooltip, help text, or UI copy may state or imply:
- 100% detection rate
- Perfect accuracy
- Guaranteed protection
- Zero false positives or zero false negatives
- Definitive identity verification

---

## 5. Authentication and Account Flows

### 5.1 Registration Flow

1. User navigates to registration page.
2. User enters: email address, password, password confirmation.
3. System validates: email format, password strength (minimum requirements TBD during engineering design), password match.
4. System displays data collection disclosure and consent checkbox (required — cannot proceed without consent). See Section 7.
5. System creates account and sends email verification link.
6. User clicks verification link. Account is activated.
7. User is redirected to the application home page / onboarding flow.

**Acceptance Criteria:**
- AC-AUTH-1: A duplicate email address returns a clear error — it does not reveal whether the email is registered (to prevent account enumeration).
- AC-AUTH-2: Registration is not possible without ticking the consent checkbox.
- AC-AUTH-3: Email verification link expires after a defined period (TBD — ADR-026).

### 5.2 Login Flow

1. User enters email and password.
2. If 2FA is not enabled: system validates credentials and issues JWT access token and refresh token. User is redirected to the home page.
3. If 2FA is enabled: system validates credentials, then prompts for TOTP code. User enters code. System validates. JWT tokens issued. User redirected to home page.
4. Failed login: system returns a generic "Invalid email or password" message — it does not specify which field is wrong (prevents enumeration).

**Acceptance Criteria:**
- AC-AUTH-4: Failed login returns a generic error — not "incorrect password" or "email not found."
- AC-AUTH-5: After a defined number of consecutive failed login attempts (TBD — ADR-026), the account is temporarily locked or rate-limited.
- AC-AUTH-6: A valid TOTP code at the correct time step allows login. An expired or incorrect code does not.

### 5.3 Optional TOTP 2FA Enrollment Flow

1. Authenticated user navigates to Security Settings.
2. User selects "Enable Two-Factor Authentication."
3. System generates a TOTP secret and displays a QR code for scanning with an authenticator app (e.g., Google Authenticator, Authy).
4. System also displays the backup codes (one-time use codes for account recovery).
5. User scans the QR code in their authenticator app.
6. User enters the current TOTP code from their authenticator app to confirm enrollment.
7. System validates the code. 2FA is enabled.
8. System prompts user to save backup codes securely.

**Acceptance Criteria:**
- AC-AUTH-7: 2FA enrollment is not confirmed until the user successfully enters a valid TOTP code during setup.
- AC-AUTH-8: Backup codes are generated and displayed exactly once during enrollment. The user is warned that they cannot be retrieved again.

### 5.4 Password Reset Flow

1. User navigates to "Forgot Password" from the login page.
2. User enters their email address.
3. System sends a password reset link to the email (if the email is registered — system sends the email regardless of whether the address is registered, to prevent enumeration).
4. User clicks the reset link (time-limited — expiry TBD, ADR-026).
5. User enters new password and confirmation.
6. System validates password strength and resets the password.
7. All existing sessions are invalidated.

**Acceptance Criteria:**
- AC-AUTH-9: The password reset confirmation message is identical whether or not the email is registered in the system.
- AC-AUTH-10: Password reset link expires and cannot be reused after a single successful use.
- AC-AUTH-11: All active sessions are invalidated after a successful password reset.

### 5.5 Account Deletion Flow

1. Authenticated user navigates to Account Settings.
2. User selects "Delete My Account."
3. System displays a clear explanation of what will be deleted and that the action is irreversible.
4. User confirms by entering their password.
5. System deletes or anonymises all personal data associated with the account per the defined retention and deletion policy.
6. User is logged out and redirected to a confirmation page.

**Acceptance Criteria:**
- AC-AUTH-12: Account deletion requires password re-entry confirmation — a single button click is not sufficient.
- AC-AUTH-13: After deletion, the user's personal data is deleted or anonymised in accordance with the retention policy defined during engineering design.
- AC-AUTH-14: A deleted account cannot be logged into.

---

## 6. Notification and Alert Model

### 6.1 Phase 1 Notification Scope

Phase 1 notifications are limited to:
- **In-app notifications**: displayed within the application when the user is active
- **Email notifications**: for security-critical events only (account verification, password reset, login from new device if implemented)

Push notifications and SMS notifications are not in Phase 1 scope.

### 6.2 Events That Trigger Notifications

| Event | Notification Type | Channel |
|---|---|---|
| New account registration | Email verification | Email |
| Password reset requested | Reset link | Email |
| 2FA enrollment completed | Confirmation | In-app |
| Login from a new device/location (if implemented) | Security alert | Email + In-app |
| Async scan completed (F-06, F-07 — Celery tasks) | Scan result ready | In-app |
| New scam alert for user's location (F-13) | Alert available | In-app (on next visit) |

### 6.3 Notification Preferences

Users can opt out of non-critical email notifications. Security-critical emails (account verification, password reset) cannot be disabled.

---

## 7. Privacy and Consent UX

### 7.1 Data Collection Disclosure at Registration

Before creating an account, users must be shown a clear, plain-language summary of:
- What personal data is collected (email, usage data, scan history)
- Why it is collected (to provide the service, compute Cyber Risk Score)
- How long it is retained (retention periods defined during engineering design)
- Their rights: access, correction, deletion

This disclosure must be written in plain language — not in legal terms. A link to the full privacy policy is provided for users who want more detail.

### 7.2 Consent Requirement

Account creation requires explicit consent via a checkbox:
> "I have read and understood how CyberShakti uses my data and I consent to data processing as described."

Pre-ticked checkboxes are not permitted.

### 7.3 User Rights in the UI

The following user rights must be accessible from Account Settings:
- **Access:** User can view what data is held about them (within the application scope)
- **Correction:** User can update their profile information
- **Deletion:** User can delete their account and all associated personal data (Section 5.5)
- **Grievance:** Contact information for data-related queries

### 7.4 Regulatory Reference

These flows are designed with awareness of the DPDP Act 2023 and IT Act 2000 as compliance consideration areas. Implementing these flows does not constitute legal compliance. Actual obligations must be verified with qualified legal counsel before launch. See CSHAKTI-CONST-001 §10 and ADR-030.

### 7.5 Per-Feature Data Minimisation

| Feature | Data Collected | Retention |
|---|---|---|
| F-01 to F-04 | Submitted URL/text/image for analysis; verdict and timestamp | Verdict stored for Risk Score; raw input retention TBD during engineering design |
| F-05 | Submitted profile signals; verdict | Verdict stored for Risk Score; raw signals retention TBD |
| F-06, F-07 | Uploaded media/signals; verdict | Raw media not permanently stored; verdict stored for user history |
| F-08 | Phone number submitted; verdict | Verdict stored; phone number retention TBD |
| F-09 | Password string — NOT stored or transmitted in plaintext | Not retained |
| F-10 | File uploaded — plaintext not permanently retained after encrypted output provided | Encrypted file not stored server-side (Phase 1 — user downloads and manages their own encrypted files) |
| F-11 | Query text; response | Session history not persisted in Phase 1; query logging policy TBD during engineering design (privacy implications require review) |
| F-12 | In-app activity signals; user-reported responses | Retained for score computation; user can delete via account deletion |
| F-13 | Location (city/region level); alert view history | Location used for query; retention TBD |
| F-14 | Quiz scores; content viewed | Retained for user progress; user can delete via account deletion |

---

## 8. Non-Functional Product Requirements

These are product-level requirements from the user's perspective. Technical specifications are in the TRD.

### 8.1 Response Time Expectations

Users expect:
- **Lightweight synchronous operations** (password check, URL pre-filter check): near-instantaneous — result appears without a perceptible wait. Specific target: TBD after benchmarking.
- **Standard ML inference** (phishing scan, scam text check): result within a few seconds. User sees a loading indicator. Specific target: TBD after benchmarking.
- **Heavy async inference** (screenshot OCR+NLP, deepfake detection, mule detection): result is not instant. User is informed that analysis is in progress and will be notified when complete. Specific target: TBD after benchmarking.

### 8.2 Behaviour on Slow or Intermittent Connections

- The application must display meaningful loading states — not blank screens.
- File uploads must show progress indication.
- If a network error occurs, the user must receive a clear, user-friendly error message with retry guidance.
- Partial uploads or failed operations must not leave the user uncertain about whether their data was processed.

### 8.3 Mobile-Responsive Behaviour

- The application must be fully functional on mobile browsers (Chrome for Android, Safari for iOS) at screen widths from 320px upward.
- Touch targets must meet minimum size requirements (WCAG 2.5.5 guideline — minimum 44×44px).
- Text must be readable without zooming on a standard smartphone screen.
- File upload interactions must work on mobile browsers (camera capture and file picker).

### 8.4 Accessibility Baseline

- Target: WCAG 2.1 Level AA.
- All images must have meaningful alt text.
- All form inputs must have associated labels.
- Colour is not used as the sole means of conveying information (risk levels must have both colour and text labels).
- The application must be keyboard-navigable.
- Full WCAG compliance requires expert accessibility review and testing — automated tools alone are not sufficient.

### 8.5 Offline Behaviour

The following features require active internet connectivity and must communicate this clearly if connectivity is lost:
- F-01, F-02, F-03, F-04, F-05, F-06, F-07 (ML inference is server-side)
- F-08, F-13 (database lookups)
- F-11 (LLM API call)
- F-12 (score computation with latest signals)

F-09 (Password Security Checker) may be implemented client-side and could function offline — this is a design decision for the engineering phase.

F-14 (Cyber Safety Hub) content may be cacheable for offline reading — to be evaluated during engineering design.

---

*End of CyberShakti Product Requirements Document — CSHAKTI-PRD-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
