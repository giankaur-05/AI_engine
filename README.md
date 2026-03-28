# AI Reality Check Engine

An explainable multimodal scam-detection web app built for hackathon demos and real-world cyber-safety use cases.

It analyzes suspicious:
- messages
- screenshots
- QR / UPI payment prompts
- voice / call transcripts
- brand impersonation links

and then tells the user:
- what looks suspicious
- why it was flagged
- how risky it is
- what to do next

## Why This Project

Online scam victims usually do not need "just a score".
They need:
- a clear verdict
- explainable evidence
- payment-risk detection
- post-scam rescue advice
- something simple enough to use in panic

This project is designed as an AI-powered scam safety assistant for Indian users, especially around UPI, QR, refund, job, impersonation, and call-based fraud.

## Key Features

### 1. Screenshot / Image Scam Analysis
- Accepts screenshot clues
- Supports image upload
- Runs browser-side OCR
- Uses screenshot context in final risk scoring

### 2. UPI / QR / Payment Scam Detection
- Detects UPI IDs, QR-trigger language, fee/refund scams
- Extracts QR payload when possible
- Shows payee, amount, and payment-risk evidence

### 3. Explainable Evidence Engine
- Shows exactly why content was flagged
- Breaks evidence into category, emotional, payment, voice, screenshot, and brand signals

### 4. Voice / Call Scam Analysis
- Accepts suspicious call transcript
- Detects impersonation, remote-access, OTP, and pressure tactics

### 5. Brand Impersonation & Fake Link Detection
- Flags shortened links
- Detects support-style suspicious domains
- Highlights possible brand/domain mismatches

### 6. Indian Language / Hinglish Awareness
- Supports mixed-language scam cues
- Detects Hinglish and other regional indicators

### 7. Post-Scam Rescue Mode
- Lets user mark if they already:
  - paid money
  - shared OTP
  - shared bank details
  - installed a remote app
- Generates immediate recovery guidance

### 8. Live Warning Mode
- Gives real-time warning cues while user types or uploads

### 9. Downloadable Evidence Report
- Exports a plain-text scam evidence summary for reporting or complaint support

## Tech Stack

- Python
- Flask
- HTML / CSS / JavaScript
- Tesseract.js for browser-side OCR
- jsQR for browser-side QR decoding

## Project Structure

```text
AI---engine/
├── app.py
├── analyzer.py
├── requirements.txt
├── README.md
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    ├── analyzer.html
    ├── layout.html
    ├── roadmap.html
    └── trends.html
```

## How It Works

1. User enters suspicious text, screenshot clues, voice transcript, or uploads an image.
2. Browser extracts OCR text and QR payload when possible.
3. Backend analyzer evaluates:
   - scam category
   - emotional manipulation
   - screenshot risk
   - QR / UPI risk
   - call transcript risk
   - impersonation / link mismatch risk
   - language cues
4. The app returns:
   - verdict
   - score breakdown
   - explainable evidence
   - recommended actions
   - rescue guidance

## Local Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
python app.py
```

### 3. Open in browser

```text
http://127.0.0.1:5000
```

## Demo Flow For Judges

Best demo sequence:

1. Paste a fake refund / QR scam
2. Upload a screenshot with QR or fake bank branding
3. Paste a fake support-call transcript
4. Toggle a post-scam case like `Shared OTP`
5. Show:
   - final verdict
   - evidence cards
   - payment risk
   - impersonation detection
   - rescue guidance
   - downloadable report

## Problem Statement Fit

This project addresses:
- cyber fraud prevention
- user safety in digital payments
- explainable AI for trust and actionability
- scam awareness for Indian users

## Future Scope

- real cybercrime complaint portal integration
- WhatsApp / browser extension mode
- multilingual OCR and speech support
- scam history intelligence and repeat offender signals
- bank / fintech alert integrations

## Pitch Line

`AI Reality Check Engine is an explainable multimodal scam-defense assistant that helps users detect fraud across text, screenshots, QR payments, and voice scams, then tells them exactly what to do next.`

## Team Value

This is not just a detector.
It is a user-safety decision support system built to reduce panic, increase trust, and make scam response actionable.
