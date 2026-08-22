# CyberShakti V3 — Core Security Modules Technical Architecture

This document provides an exhaustive, end-to-end technical explanation of CyberShakti's five flagship cybersecurity engines:
1. **Phishing Link Scanner (F-01)**
2. **Password Security & Entropy Engine**
3. **MuleTrace — Forensic Network Investigator (F-07)**
4. **Zero-Knowledge Secure File Vault (Argon2id + AES-256-GCM / Web Crypto)**
5. **QR Code Threat & Payload Decoder (F-04)**

---

## 1. Phishing Link Scanner (F-01)

### 🎯 Overview & Objectives
The Phishing Link Scanner detects malicious, credential-harvesting, bank impersonation, and deceptive domains by extracting 19 structural and lexical URL features, running real-time machine learning inference via an optimized XGBoost classifier, and explaining feature-level contributions.

```
+-----------------------------------------------------------------------------------+
|                            PHISHING SCAN PIPELINE                                 |
|                                                                                   |
|  [ User URL Input ] --> [ Auto-Scheme Normalizer ] --> [ 19-Feature Extractor ]    |
|                                                                   |               |
|                                                                   v               |
|  [ Threat Result Card ] <-- [ Explanation Engine ] <-- [ XGBoost Model Inference ] |
+-----------------------------------------------------------------------------------+
```

### ⚙️ Backend Architecture & Working Mechanism
1. **Input Normalization**:
   - The route `POST /api/v1/detect/scan-url` receives `{ "url": "<target_url>" }`.
   - Validates that the input is a valid URL string (must contain host and domain elements).
   - Automatically prefixes `https://` if the protocol scheme was omitted.

2. **19-Feature Vector Extraction (`extract_url_features` in `backend/app/detect_analyze/router.py`)**:
   | Feature # | Feature Name | Description & Heuristic Significance |
   |---|---|---|
   | 1 | `url_length` | Total character count (phishing links often use long obscured query strings). |
   | 2 | `hostname_length` | Domain/hostname character length. |
   | 3 | `path_length` | Depth and character length of URL path. |
   | 4 | `subdomain_count` | Number of subdomains (e.g., `login.verify.sbi.com.evil.ru` has high count). |
   | 5 | `has_ip` | Binary flag indicating if the domain is a raw IPv4/IPv6 address. |
   | 6 | `digit_count` | Number of numeric digits across the entire URL. |
   | 7 | `letter_count` | Number of alphabetic characters. |
   | 8 | `special_char_count`| Count of special characters (`-`, `_`, `@`, `?`, `=`, `%`). |
   | 9 | `entropy` | Shannon entropy of the URL string ($H(X) = -\sum P(x) \log_2 P(x)$), detecting randomized strings and DGA domains. |
   | 10 | `is_https` | 1 if HTTPS, 0 if plain HTTP. |
   | 11 | `slash_count` | Number of forward slashes (`/`). |
   | 12 | `dot_count` | Number of periods (`.`) in the URL. |
   | 13 | `hyphen_count` | Number of hyphens (`-`) used to spoof brand names (e.g. `sbi-bank-kyc`). |
   | 14 | `at_symbol_count` | Number of `@` symbols (used in URL trickery to obscure the real destination). |
   | 15 | `has_suspicious_keyword` | Detects high-risk keywords: `kyc`, `verify`, `otp`, `bank`, `update`, `reward`, `gift`, `unblock`. |
   | 16 | `has_brand_name` | Matches Indian and global banking/payment brands (`sbi`, `hdfc`, `icici`, `paytm`, `phonepe`, `gpay`). |
   | 17 | `digit_ratio` | Ratio of numeric digits to total letters. |
   | 18 | `path_depth` | Hierarchical folder count in URL path. |
   | 19 | `query_length` | Length of parameters after `?`. |

3. **Machine Learning Model (`f01_phishing_url_model.joblib`)**:
   - Model Type: **XGBoost Classifier** with gradient boosted decision trees.
   - Threshold Logic:
     - $P(\text{Phishing}) \ge 0.70 \implies$ **High Risk**
     - $0.40 \le P(\text{Phishing}) < 0.70 \implies$ **Moderate Risk**
     - $P(\text{Phishing}) < 0.40 \implies$ **Safe**
   - Direct IP address overrides automatically enforce a minimum of **Moderate Risk**.

4. **Verdict Generation (`explanation_engine.py`)**:
   - Compiles human-readable reasoning, identified risk signals, and recommended security actions (e.g. "Do not enter OTPs or passwords on this domain").

---

## 2. Password Security & Shannon Entropy Checker

### 🎯 Overview & Objectives
The Password Security Checker provides zero-knowledge password auditing. It calculates informational entropy bits, evaluates combinatorial character complexity, detects dictionary words, and estimates brute-force crack times at 10 billion guesses/second.

```
+-----------------------------------------------------------------------------------+
|                        PASSWORD SECURITY CHECKER PIPELINE                         |
|                                                                                   |
|  [ User Password ] --> [ Shannon Entropy Engine: -sum(p * log2(p)) ]              |
|                                     |                                             |
|                                     v                                             |
|  [ Crack Time Estimator ] <-- [ Search Space Size: Pool^Length ]                  |
|          |                                                                        |
|          v                                                                        |
|  [ Multi-Signal Checklist: Length, Upper, Lower, Numbers, Special Characters ]   |
|          |                                                                        |
|          v                                                                        |
|  [ 1-Click Cryptographically Secure Passphrase Generator (Web Crypto API) ]       |
+-----------------------------------------------------------------------------------+
```

### ⚙️ Backend & Frontend Algorithms
1. **Shannon Entropy Formula**:
   $$\text{Entropy (bits)} = -\sum_{i=1}^{n} P(c_i) \log_2 P(c_i) \times L$$
   where $P(c_i)$ is the frequency of character $c_i$ in the password and $L$ is password length.

2. **Combinatorial Search Space & Crack Time Estimation**:
   - **Pool Size Calculation ($N$)**:
     - Lowercase letters ($a-z$): $+26$
     - Uppercase letters ($A-Z$): $+26$
     - Numbers ($0-9$): $+10$
     - Special Symbols: $+33$
   - Total Combinations: $\text{Combinations} = N^L$
   - Crack Time assuming a high-end GPU cluster operating at $10^{10}$ hashes/second:
     $$\text{Seconds to Crack} = \frac{N^L}{10^{10}}$$

3. **Backend API (`/api/v1/protect/check-password`)**:
   - Accessible without forced authentication (`get_optional_current_user`).
   - Checks against common weak password lists (`123456`, `password`, `admin`, `qwerty`).
   - Evaluates consecutive character repetitions and keyboard patterns (`asdf`, `1234`).

4. **Client-Side Generator**:
   - Uses `window.crypto.getRandomValues()` to generate 16–24 character cryptographically strong passwords containing uppercase, lowercase, numbers, and symbols.

---

## 3. MuleTrace — Forensic Network Investigator (F-07)

### 🎯 Overview & Objectives
MuleTrace is a money mule network detection and forensic graph analytics engine. It models transactional flows between accounts to uncover mule rings, layering chains, smurfing rings, and burst pass-through hubs using NetworkX graph theory and an XGBoost classification model trained on Indian banking typologies (UPI, IMPS, NEFT).

```
+-----------------------------------------------------------------------------------+
|                             MULETRACE FORENSIC ENGINE                             |
|                                                                                   |
|  [ Transaction Records (CSV/Preset) ] --> [ Directed Graph Construction (NetworkX)|
|                                                        |                          |
|                                                        v                          |
|  [ Graph Centrality Calculation: In/Out Degree, Betweenness, Velocity, Pass-Thru ]|
|                                                        |                          |
|                                                        v                          |
|  [ Interactive Topology Graph (vis-network) ] <-- [ F-07 XGBoost Classification ] |
+-----------------------------------------------------------------------------------+
```

### ⚙️ Backend Graph Analytics & Typology Detection
1. **NetworkX Directed Graph Modeling ($G = (V, E)$)**:
   - Vertices ($V$): Bank accounts / UPI IDs.
   - Directed Edges ($E$): Transactions with weights representing amount ($\text{INR}$) and timestamp.

2. **Forensic Centrality & Transaction Metrics**:
   - **In-Degree ($d_{in}$) & Out-Degree ($d_{out}$)**: Ratio of money inflow vs. outflow accounts.
   - **Betweenness Centrality**: Measures how frequently an account sits on the shortest transfer path between victim nodes and cash-out nodes:
     $$C_B(v) = \sum_{s \ne v \ne t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
   - **Pass-Through Index**: High inflow velocity immediately followed by high outflow velocity (funds retained for $< 15$ minutes).
   - **Structuring / Smurfing Detector**: Detects transaction splitting where amounts are structured just below Indian regulatory reporting thresholds ($< ₹50,000$).

3. **Built-In Scenarios & Custom CSV Datasets**:
   - **UPI Mule Ring (`demo_mule_ring_simple.csv`)**: 8 transactions, 9 nodes demonstrating layer-1 victims funneling into layer-2 intermediate mule hubs.
   - **Complex Multi-Tier Ring (`demo_mule_ring_complex.csv`)**: 17 transactions, 16 nodes demonstrating multi-tier laundering, smurfing, and aggregator accounts.

4. **Frontend Graph Visualizer (`frontend/src/pages/MuleAccount.jsx`)**:
   - Rendered using `vis-network` with physics-based force-directed layout.
   - Node styling: Color-coded by role (Victim: Green/Cyan, Mule Hub: Red/Amber, Aggregator: Purple).
   - Clean Plain-Text Tooltips: Displays exact account ID without raw HTML artifacts.

---

## 4. Zero-Knowledge Secure File Vault

### 🎯 Overview & Objectives
The File Encryption Vault enables zero-knowledge, end-to-end document protection. Files are encrypted with authenticated AES-256-GCM using memory-hard key derivation functions, supporting both server-side processing and client-side browser Web Crypto processing.

```
+-----------------------------------------------------------------------------------+
|                        ZERO-KNOWLEDGE CIPHER PIPELINE                             |
|                                                                                   |
|  [ Upload File + Passphrase ] --> [ 256-bit Random Salt Generated ]               |
|                                                |                                  |
|                                                v                                  |
|                       [ Key Derivation: Argon2id / PBKDF2 (100k rounds) ]         |
|                                                |                                  |
|                                                v                                  |
|                   [ Authenticated AES-GCM-256 (96-bit Nonce + 128-bit Tag) ]      |
|                                                |                                  |
|                                                v                                  |
|            [ Binary Output File: [SALT (32B)] + [NONCE (12B)] + [CIPHERTEXT] ]    |
+-----------------------------------------------------------------------------------+
```

### ⚙️ Cryptographic Specifications & Dual Engine
1. **Server-Side Engine (`backend/app/shared/file_crypto.py`)**:
   - **Key Derivation**: **Argon2id** (memory-hard against ASIC/GPU cracking).
   - **Encryption Algorithm**: **AES-256-GCM** (Galois/Counter Mode) offering confidentiality and cryptographic authenticity (AEAD).
   - **Binary Format Header**:
     - Bytes `0..31` (32 bytes): Cryptographically secure random Salt.
     - Bytes `32..43` (12 bytes): Initialization Vector (96-bit Nonce).
     - Bytes `44..end`: Encrypted payload with 128-bit appended GCM authentication tag.

2. **Client-Side Web Crypto Engine (In-Browser Offline Fallback)**:
   - Uses browser-native `window.crypto.subtle`.
   - Derives 256-bit key using PBKDF2 with SHA-256 and 100,000 iterations.
   - Performs streaming AES-GCM encryption/decryption in memory.

3. **User State Management**:
   - Tab switching between "Encrypt File (.enc)" and "Decrypt File" automatically resets inputs, passwords, and file handles for security and a clean state.

---

## 5. QR Code Threat & Payload Decoder (F-04)

### 🎯 Overview & Objectives
The QR Code Scanner detects malicious payloads embedded in QR codes (quishing attacks, payment redirect fraud, fake KYC update forms) by combining a client-side JavaScript QR engine, a server-side OpenCV multi-pass vision engine, and the F-01 machine learning classifier.

```
+-----------------------------------------------------------------------------------+
|                            QR CODE SCANNER PIPELINE                               |
|                                                                                   |
|  [ Upload / Drop QR Image ]                                                       |
|             |                                                                     |
|             +---> [ 1. In-Browser jsQR + Canvas Matrix Decoder ]                  |
|             |               |                                                     |
|             |               v (If decoded)                                        |
|             |     [ Extract Payload String ]                                      |
|             |               |                                                     |
|             +---> [ 2. Server Multi-Pass OpenCV (Grayscale/Otsu/Upscale) ]        |
|                             |                                                     |
|                             v                                                     |
|                 [ Decoded Payload Banner ]                                        |
|                             |                                                     |
|                             v                                                     |
|                 [ Is Payload a URL? ]                                             |
|                    /              \                                               |
|               (Yes)                (No - Text/WiFi)                               |
|                 v                            v                                    |
|     [ F-01 ML URL Classifier ]      [ Safe Payload Summary ]                      |
|                 |                            |                                    |
|                 +------------+---------------+                                    |
|                              |                                                    |
|                              v                                                    |
|                 [ Threat Analysis Verdict Card ]                                  |
+-----------------------------------------------------------------------------------+
```

### ⚙️ Multi-Tier Decoding Architecture
1. **Tier 1: Client-Side In-Browser Engine (`jsQR` + HTML5 Canvas)**:
   - Reads image dimensions and renders raw pixels to an off-screen `HTMLCanvasElement`.
   - Extracts `ImageData` buffer and runs `jsQR` with:
     - Pass 1: Standard color matrix.
     - Pass 2: Inverted contrast matrix (for dark-mode QR codes).
   - Achieves instant decoding with zero network latency.

2. **Tier 2: Server-Side Multi-Pass OpenCV Decoder (`backend/app/shared/qrdecode.py`)**:
   - **Pass A**: Standard RGB matrix read.
   - **Pass B**: Grayscale intensity conversion.
   - **Pass C**: Otsu adaptive binary thresholding (`cv2.THRESH_BINARY + cv2.THRESH_OTSU`).
   - **Pass D**: 2x bicubic upscaling (`cv2.INTER_CUBIC`) for low-resolution or thumbnail QR images.
   - **Pass E**: `pyzbar` fallback.

3. **Payload Inspection & ML Routing**:
   - When a URL payload is extracted (e.g. `http://sbi-bank-kyc-verify.info/login`), it routes through the F-01 URL classifier.
   - Displays the **`DECODED PAYLOAD:`** badge directly above the detailed **`ThreatResultCard`** containing confidence scores, domain risk metrics, and mitigation steps.

---

## 6. Architecture Summary Table

| Feature | Module ID | Core Technologies | Primary Machine Learning / Cryptographic Algorithm |
|---|---|---|---|
| **Phishing Link Scanner** | F-01 | FastAPI, Scikit-Learn, XGBoost, SHAP | 19-Feature Vector + XGBoost Gradient Boosted Trees |
| **Password Security Checker** | Protect | Python, React, Web Crypto API | Shannon Entropy Calculation + Combinatorial Search Space |
| **MuleTrace Investigator** | F-07 | NetworkX, Vis-Network, Scikit-Learn | Graph Centrality Analytics + Indian Banking Typology XGBoost |
| **Secure File Vault** | Protect | Cryptography (Py), Web Crypto (JS) | Argon2id Key Derivation + AES-256-GCM Authenticated Cipher |
| **QR Code Threat Scanner** | F-04 | jsQR, OpenCV, PIL, F-01 Classifier | Multi-Pass Vision Decoding + XGBoost Phishing Pipeline |
