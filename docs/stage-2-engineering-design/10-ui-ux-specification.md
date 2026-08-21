# CyberShakti — UI/UX Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-UX-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-PRD-001, CSHAKTI-SYS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 §11 (UI/UX Principles) |

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Design System](#2-design-system)
3. [Accessibility Requirements](#3-accessibility-requirements)
4. [Responsive Design Breakpoints](#4-responsive-design-breakpoints)
5. [Core Screen Specifications](#5-core-screen-specifications)
6. [Navigation Architecture](#6-navigation-architecture)
7. [Risk Verdict Display Standard](#7-risk-verdict-display-standard)
8. [Disclaimer Display Standard](#8-disclaimer-display-standard)
9. [Async Operation UX Pattern](#9-async-operation-ux-pattern)
10. [Authentication UX](#10-authentication-ux)
11. [Error State UX](#11-error-state-ux)
12. [Internationalisation Considerations](#12-internationalisation-considerations)
13. [Motion and Animation](#13-motion-and-animation)
14. [Open UX Decisions](#14-open-ux-decisions)

---

## 1. Design Principles

These principles are governed by CSHAKTI-CONST-001 §11 and must be upheld across all screens:

### 1.1 Trust Through Clarity

CyberShakti users are often in a moment of anxiety — they suspect a threat and need a clear answer. The UI must:
- Communicate verdicts immediately and unambiguously
- Avoid technical jargon unless accompanied by plain-language explanation
- Never leave a user unsure of what happened or what to do next

### 1.2 Inclusive Design First

The target user includes Kamala (67, low technical literacy — Persona 3). The UI must work for her, not just for Arjun (Persona 2, high technical literacy):
- Large touch targets (minimum 44×44px)
- High-contrast colour choices
- Plain-English labels (no feature codes like "F-01" in the UI)
- Explanations before disclaimers — answer the user first, qualify second

### 1.3 Transparency, Not False Confidence

The UI must never suggest the system is infallible:
- Disclaimers are required on all AI/ML outputs — but they are presented as secondary, not primary
- Confidence indicators communicate uncertainty to users
- Experimental features are clearly labelled before use, not buried in fine print

### 1.4 Mobile-First

Most Indian users access the internet primarily via smartphone. All layouts are designed mobile-first. Desktop is an enhancement, not the primary target.

### 1.5 Speed Over Decoration

The UI prioritises perceived performance:
- Skeleton loaders for content
- Optimistic UI patterns where safe
- Minimal blocking operations

---

## 2. Design System

### 2.1 Colour Palette

#### Brand Colours

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#2563EB` (Blue 600) | Primary actions, brand identity |
| `--color-primary-dark` | `#1D4ED8` (Blue 700) | Primary hover states |
| `--color-secondary` | `#7C3AED` (Violet 600) | Secondary actions, accents |
| `--color-background` | `#0F172A` (Slate 900) | App background (dark theme) |
| `--color-surface` | `#1E293B` (Slate 800) | Card and panel backgrounds |
| `--color-surface-raised` | `#334155` (Slate 700) | Elevated surface backgrounds |
| `--color-border` | `#475569` (Slate 600) | Borders and dividers |

#### Risk Level Colours

These colours are standardised across all verdict displays and must be used consistently:

| Risk Level | Colour Token | Value | Usage |
|---|---|---|---|
| Safe | `--color-risk-safe` | `#22C55E` (Green 500) | Safe verdict indicator |
| Low Risk | `--color-risk-low` | `#84CC16` (Lime 500) | Low risk indicator |
| Moderate Risk | `--color-risk-moderate` | `#EAB308` (Yellow 500) | Moderate risk indicator |
| High Risk | `--color-risk-high` | `#F97316` (Orange 500) | High risk indicator |
| Critical | `--color-risk-critical` | `#EF4444` (Red 500) | Critical risk indicator |

#### Text Colours

| Token | Value | Usage |
|---|---|---|
| `--color-text-primary` | `#F8FAFC` (Slate 50) | Primary body text |
| `--color-text-secondary` | `#CBD5E1` (Slate 300) | Secondary and helper text |
| `--color-text-muted` | `#94A3B8` (Slate 400) | Placeholder and muted content |
| `--color-text-warning` | `#FDE68A` (Amber 200) | Warning text |
| `--color-text-error` | `#FCA5A5` (Red 300) | Error text |

### 2.2 Typography

| Role | Font Family | Weight | Size (Mobile) | Size (Desktop) |
|---|---|---|---|---|
| App name / H1 | Inter, system-ui | 700 (Bold) | 1.875rem (30px) | 2.25rem (36px) |
| Page heading / H2 | Inter, system-ui | 600 (SemiBold) | 1.5rem (24px) | 1.875rem (30px) |
| Section heading / H3 | Inter, system-ui | 600 (SemiBold) | 1.25rem (20px) | 1.5rem (24px) |
| Body text | Inter, system-ui | 400 (Regular) | 1rem (16px) | 1rem (16px) |
| Small / Helper text | Inter, system-ui | 400 (Regular) | 0.875rem (14px) | 0.875rem (14px) |
| Risk verdict label | Inter, system-ui | 700 (Bold) | 1.25rem (20px) | 1.5rem (24px) |
| Disclaimer text | Inter, system-ui | 400 (Regular) | 0.75rem (12px) | 0.8125rem (13px) |

Font loaded via Google Fonts (`Inter` family, weights 400, 500, 600, 700). Font must preload for performance.

### 2.3 Spacing Scale

Based on an 8px base unit:

| Token | Value | Usage |
|---|---|---|
| `--space-1` | 4px | Micro spacing |
| `--space-2` | 8px | Tight spacing |
| `--space-3` | 12px | Component internal padding |
| `--space-4` | 16px | Standard padding |
| `--space-6` | 24px | Section gaps |
| `--space-8` | 32px | Section padding |
| `--space-12` | 48px | Large section gaps |
| `--space-16` | 64px | Page-level spacing |

### 2.4 Component Library

All UI components are custom-built (no third-party component library is mandated). Tailwind CSS utility classes are used for styling. Components include:

| Component | Usage |
|---|---|
| `Button` | Primary, secondary, ghost, destructive variants |
| `Input` | Text, email, password (with show/hide toggle) |
| `FileUpload` | Drag-and-drop + click-to-select; progress indicator |
| `VerdictCard` | Displays risk verdict with colour, label, explanation |
| `DisclaimerBox` | Styled disclaimer display (visually secondary) |
| `ProgressRing` | Cyber Risk Score circular progress display |
| `Skeleton` | Loading placeholder matching content layout |
| `Modal` | Confirmation dialogs, 2FA setup |
| `Toast` | Success, error, and info notifications |
| `Badge` | Feature tier labels (Core, Advanced, Experimental) |
| `Alert` | In-page alerts (not toast — stays visible) |

---

## 3. Accessibility Requirements

**Minimum standard: WCAG 2.1 Level AA** (CSHAKTI-CONST-001 §11.4)

### 3.1 Colour Contrast

- Normal text: minimum 4.5:1 contrast ratio against background
- Large text (18px+ or 14px+ bold): minimum 3:1
- Risk level colours: tested against both dark surface background and white text labels
- Interactive elements: focus indicator clearly visible (minimum 3:1 against adjacent colours)

### 3.2 Keyboard Navigation

- All interactive elements reachable by keyboard (Tab/Shift+Tab)
- Logical tab order matches visual flow
- Custom interactive elements (VerdictCard, FileUpload) implement keyboard event handlers
- Modal traps focus while open; returns focus on close

### 3.3 Screen Reader Support

- Semantic HTML throughout (`<main>`, `<nav>`, `<section>`, `<article>`, `<header>`, `<footer>`)
- ARIA labels for icon-only buttons
- ARIA live regions for dynamic content updates (verdict results, async completion)
- Form field labels associated with inputs via `htmlFor`/`for` — no placeholder-only labelling
- Error messages linked to fields via `aria-describedby`

### 3.4 Motion Accessibility

- Respects `prefers-reduced-motion` media query
- Animations disabled when user has requested reduced motion
- No flashing content (epilepsy risk mitigation)

### 3.5 Touch Targets

- Minimum 44×44px touch target for all interactive elements
- Spacing between adjacent targets: minimum 8px

---

## 4. Responsive Design Breakpoints

Mobile-first design. All layouts begin with mobile and progressively enhance.

| Breakpoint | Value | Target |
|---|---|---|
| `xs` | Default | Mobile (320px+) |
| `sm` | `640px` | Large mobile / small tablet |
| `md` | `768px` | Tablet |
| `lg` | `1024px` | Desktop |
| `xl` | `1280px` | Large desktop |

**Layout behaviour:**
- Navigation: bottom tab bar (mobile) → side drawer or top nav (desktop)
- Feature inputs: full-width single column (mobile) → max-width centred card (desktop)
- Verdict cards: full-width (mobile) → constrained width (desktop)
- Risk Score: full-width panel (mobile) → sidebar or centred panel (desktop)

---

## 5. Core Screen Specifications

### 5.1 Landing / Home Screen

**Purpose:** Entry point for unauthenticated and authenticated users.

**Unauthenticated:**
- Hero section: CyberShakti name, tagline (to be confirmed by product), primary CTA ("Check Something Suspicious" → scan without account, or "Create Account")
- Feature pillar overview: 4 pillars with icon and brief description
- Trust indicators: platform stats, data handling commitment
- CTA: Register / Login

**Authenticated:**
- Welcome message with user name (or "Welcome back")
- Quick access to most-used features (contextual to recent activity)
- Cyber Risk Score summary card with link to full score
- Recent scan history summary (last 3–5 scans)
- Daily Safety Tip from F-14

### 5.2 Feature Hub Screens (per Pillar)

Each pillar has a hub screen:
- Pillar name and description
- List of features within the pillar with feature name, description, and status badge (Core / Advanced / Experimental)
- Quick-access cards linking to each feature

### 5.3 F-01 — Phishing Link Scanner Screen

**Layout:**
1. Feature name: "Check a Suspicious Link"
2. Brief description (one sentence)
3. Input field: URL text input with placeholder "Paste a link here..."
4. "Check Link" button (primary)
5. [After submission] Loading skeleton → Verdict Card

**Verdict Card contains:**
- Risk level badge (colour-coded)
- Risk label (e.g., "High Risk")
- Explanation paragraph (plain language)
- Key signals section (2–3 bullet points)
- Confidence indicator
- Disclaimer (collapsible on mobile if space is constrained)
- Share result button (optional — Phase 1 scope TBD)
- "Check another link" link

### 5.4 F-02 — Message & Email Scam Detection Screen

**Feature label in UI:** "Check a Suspicious Message or Email"

**Layout:**
1. Feature name
2. Brief description
3. Textarea: "Paste the message or email text here..." (multi-line)
4. Character count indicator
5. "Check Message" button
6. [Result] Verdict Card + language note (if applicable)

### 5.5 F-03 — Screenshot Scam Scanner Screen

**Feature label in UI:** "Scan a Screenshot"

**Layout:**
1. Feature name
2. Description: "Upload a screenshot of a suspicious message or notification"
3. File upload zone (drag and drop + "Browse files" button)
4. Accepted formats: JPEG, PNG — displayed near upload zone
5. Upload progress indicator (if file is large)
6. [Processing] "Analysing your screenshot..." with animated indicator
7. [Result] OCR extracted text section + Verdict Card

### 5.6 F-09 — Password Security Checker Screen

**Feature label in UI:** "Check Password Strength"

**CRITICAL UX REQUIREMENT:** The notice "Do not enter your actual account passwords here" must be displayed:
- **Before** the password input field is shown (at screen entry)
- **After** the result is shown (in the verdict card)

**Layout:**
1. Feature name
2. Safety notice (prominent, not dismissible)
3. Password input with show/hide toggle
4. "Check Strength" button
5. [Result] Strength level indicator (visual bar + label) + improvement recommendations

### 5.7 F-12 — Cyber Risk Score Screen

**Feature label in UI:** "My Cyber Risk Score"

**Layout:**
1. Score display: large circular progress ring (ProgressRing component) with score number
2. Score band label (e.g., "Moderate Risk")
3. Signal breakdown: accordion or card list showing each signal, its label, and contribution direction
4. Improvement actions: ordered list
5. Score disclaimer
6. "Answer security questions to improve your score" CTA (if questionnaire not completed)

### 5.8 F-10 — Secure File Encryption Screen

**Feature label in UI:** "Encrypt or Decrypt a File"

**Layout (two modes — tabs or toggle):**

*Encrypt mode:*
1. Feature description
2. File upload zone
3. Password input (show/hide toggle)
4. Password-loss warning (prominent)
5. "Encrypt and Download" button

*Decrypt mode:*
1. Encrypted file upload zone
2. Password input
3. "Decrypt and Download" button

### 5.9 F-14 — Cyber Safety Hub Screen

**Feature label in UI:** "Cyber Safety Hub"

**Layout:**
1. Daily Tip card (highlighted, top of page)
2. Tab navigation: "Articles" | "Quiz" | "Quick Tips"
3. Articles tab: category filter chips + article card list
4. Quiz tab: quiz start prompt + question/answer flow
5. Quick Tips tab: list of actionable tips

---

## 6. Navigation Architecture

### 6.1 Mobile Navigation (Bottom Tab Bar)

| Tab | Icon | Label |
|---|---|---|
| Home | Home icon | Home |
| Detect | Shield-check icon | Detect |
| Protect | Lock icon | Protect |
| Assist | Bot/chat icon | Assist |
| Learn | Book icon | Learn |

Authenticated state: profile avatar or icon replaces or augments navigation. Settings accessible via avatar menu.

### 6.2 Desktop Navigation (Top Nav or Side Drawer)

Top navigation bar with:
- CyberShakti logo/wordmark (left)
- Pillar links: Detect, Protect, Assist, Learn (centre)
- User avatar menu: Profile, Settings, Logout (right)

### 6.3 Route Structure

| Route | Screen |
|---|---|
| `/` | Home / Dashboard |
| `/detect` | Detect & Analyze hub |
| `/detect/phishing-link` | F-01 |
| `/detect/message-scan` | F-02 |
| `/detect/screenshot-scan` | F-03 |
| `/detect/qr-scan` | F-04 |
| `/detect/profile-check` | F-05 |
| `/detect/deepfake-check` | F-06 |
| `/detect/account-check` | F-07 |
| `/protect` | Protect hub |
| `/protect/phone-check` | F-08 |
| `/protect/password-check` | F-09 |
| `/protect/file-encryption` | F-10 |
| `/assist` | Assist & Respond hub |
| `/assist/ai-assistant` | F-11 |
| `/assist/risk-score` | F-12 |
| `/assist/scam-alerts` | F-13 |
| `/learn` | Cyber Safety Hub (F-14) |
| `/learn/articles` | Article list |
| `/learn/articles/:slug` | Article detail |
| `/learn/quiz` | Quiz |
| `/auth/login` | Login |
| `/auth/register` | Registration |
| `/auth/verify-email` | Email verification |
| `/auth/reset-password` | Password reset flow |
| `/settings` | Account settings |
| `/settings/security` | 2FA, password change |

---

## 7. Risk Verdict Display Standard

All five risk levels are presented using the **VerdictCard** component with the following standardised visual treatment:

| Risk Level | Colour | Icon | Label |
|---|---|---|---|
| Safe | Green (`--color-risk-safe`) | Shield-check ✓ | "Safe" |
| Low Risk | Lime (`--color-risk-low`) | Shield with information | "Low Risk" |
| Moderate Risk | Yellow (`--color-risk-moderate`) | Alert triangle | "Moderate Risk" |
| High Risk | Orange (`--color-risk-high`) | Alert triangle (filled) | "High Risk" |
| Critical | Red (`--color-risk-critical`) | Skull or X-circle | "Critical" |

**Verdict card anatomy:**
1. **Header bar** (full width, risk level colour): Icon + Risk Level Label
2. **Explanation section**: Plain-language explanation paragraph
3. **Key signals** (where available): bulleted list of contributing factors
4. **Confidence indicator**: "Based on: Threat Intelligence + AI Analysis" or similar
5. **Experimental badge** (F-06, F-07 only): prominent "Experimental" badge before explanation
6. **Disclaimer** (secondary visual weight — e.g., small text, muted colour)
7. **Next steps** (where applicable): e.g., "Do not click this link" / "Report to cybercrime.gov.in"

---

## 8. Disclaimer Display Standard

Disclaimers are required on all AI/ML outputs. They must be:
- **Present**: Never omitted
- **Secondary**: Presented below the primary verdict/result, not above it
- **Not disruptive**: Displayed in smaller text (12–13px) with muted colour
- **Not modal**: Disclaimers do not block the interface

**Disclaimer text standard by feature type:**

| Feature Type | Disclaimer |
|---|---|
| Detection features (F-01–F-08) | "This assessment is produced by an automated system and may not detect all threats. Do not rely solely on this result." |
| Experimental features (F-06, F-07) | "This is an experimental research feature. Results are indicative only. False positives and false negatives occur." |
| F-05 Fake Profile | "CyberShakti does not verify identities. This assesses observable risk signals only." |
| F-09 Password Checker | "Do not enter your actual account passwords here. This assessment is for educational purposes only." |
| F-11 AI Assistant | "This response is generated by AI and is for informational purposes only. It should not replace professional cybersecurity, legal, or financial advice." |
| F-12 Risk Score | "Your Cyber Risk Score is an estimate based on your CyberShakti activity. It is not a comprehensive security audit." |

---

## 9. Async Operation UX Pattern

For features using the Celery async task pattern (F-03, F-05, F-06, F-07, F-11):

**States and displays:**

| State | UI Display |
|---|---|
| Upload/Submission | File upload progress bar or submit button spinner |
| Queued | "Your request has been received and is queued for analysis" + animated indicator |
| Processing | "Analysing now..." + animated indicator; estimated wait time if measurable |
| Complete | Verdict card animates in |
| Error | Error card with specific guidance (not generic "something went wrong") |

**Polling strategy (Phase 1):**
- Client polls `GET /tasks/{task_id}/status` every 3 seconds
- After 10 consecutive polls without completion: show "This is taking longer than expected" message with a wait option
- After 20 polls: show timeout with "Try again later" option

**User must be able to navigate away** during processing. On return to the screen, the result is displayed if complete (results are persisted in the database).

---

## 10. Authentication UX

### 10.1 Registration Flow

1. Register screen: email, password, consent checkbox, register button
2. Inline: "Check password strength" link (opens F-09 in a sheet/modal — Phase 1 scope TBD)
3. After submit: "Check your email to verify your account" success screen
4. Email link → Verification success screen → Redirect to login

### 10.2 Login Flow (No 2FA)

1. Login screen: email, password, login button
2. Forgot password link
3. After login: redirect to home / last visited page

### 10.3 Login Flow (2FA Enabled)

1. Login screen: email, password, login button
2. On partial auth success: "Enter your authenticator code" screen
3. 6-digit TOTP input (auto-advance on 6 digits entered)
4. "Use a backup code" link
5. After 2FA verified: redirect to home

### 10.4 Password Reset Flow

1. "Forgot password" → email entry screen
2. Submit: always shows "If this email is registered, you'll receive a reset link" (no enumeration)
3. Email link → Reset password screen (new password + confirm)
4. Success: "Password changed. All sessions have been signed out." → Redirect to login

---

## 11. Error State UX

### 11.1 Validation Errors

Inline validation on blur (not on each keystroke):
- Error text displayed below the field in `--color-text-error`
- Field border changes to error colour
- Accessible: linked to field via `aria-describedby`

### 11.2 Network / Server Errors

- Toast notification: short, actionable message
- Persistent error for critical failures: inline error card (not just a toast)
- Retry button where the operation can be safely retried

### 11.3 Feature Unavailable Errors

For features blocked by unresolved dependencies (e.g., F-11 when ADR-013 is unresolved):
- Feature card shows "Coming Soon" badge
- Feature screen shows clear explanation: "This feature is being finalised. Check back soon."
- Not a 404 — the feature is known, just not yet available

### 11.4 Empty States

Every list, history, or content area must have a designed empty state:
- Icon + message
- CTA where appropriate (e.g., "No scan history yet. Check a suspicious link to get started.")

---

## 12. Internationalisation Considerations

### 12.1 Phase 1 Language

English is the primary language for Phase 1 (CSHAKTI-CONST-001 §11.5).

### 12.2 Future Language Support

The UI must be built to support future internationalisation:
- All user-facing strings in string constants (not hardcoded inline)
- No hardcoded date/number formats (use Intl API)
- RTL layout not required for Phase 1 but should not be architecturally excluded

### 12.3 Indian English Conventions

UI copy should use Indian English conventions:
- "Mobile number" (not "cell phone" or "mobile phone")
- "OTP" (not "one-time password" in display — keep as "OTP" but explain on first mention)
- Currency: Indian Rupee format (₹1,00,000 not $1,000)
- Phone number format examples: Indian numbers

---

## 13. Motion and Animation

Animations use **Framer Motion**. All animations respect `prefers-reduced-motion`.

| Element | Animation |
|---|---|
| Verdict card appearance | Fade in + slide up (200ms) |
| Risk level colour fill | Smooth colour transition (300ms) |
| Page transitions | Fade (150ms) |
| Loading spinner | CSS animation (not JS-driven) |
| File upload progress bar | Smooth width transition |
| Score ring | Animated draw from 0 to score value (800ms) |
| Toast notifications | Slide in from top-right (200ms), auto-dismiss fade (300ms) |

**Durations:**
- Micro-interactions: 100–200ms
- Content transitions: 200–300ms
- Intentional animations (score ring): 600–800ms

---

## 14. Open UX Decisions

| Decision | Status | Notes |
|---|---|---|
| Dark-only vs. dark/light theme toggle | TBD | Dark theme is the primary design; light mode is a potential addition |
| Bottom tab bar vs. hamburger menu for mobile navigation | TBD | Bottom tab bar preferred for primary pillar navigation |
| Guest access (scan without account) | TBD | Constitution and PRD permit scanning without account for some features; UX flow not yet defined |
| Share scan result feature | TBD | Phase 1 scope; needs privacy review |
| F-09 integration into registration (password strength check inline) | TBD | Desirable; implementation scope TBD |
| Progressive Web App (PWA) support | TBD | Offline support and install prompt — scope TBD |
| Toast vs. inline notification for async completion | TBD | User may navigate away; notification strategy required |

---

*End of CyberShakti UI/UX Specification — CSHAKTI-UX-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
