import re
from urllib.parse import urlparse


class Analyzer:
    def __init__(self):
        self.scam_patterns = {
            "Job Scam": [
                "hiring", "part time", "work from home", "easy job", "daily income",
                "per day", "no experience", "hr manager", "recruitment",
                "joining fee", "registration fee", "interview slot"
            ],
            "Crypto/Investment": [
                "crypto", "bitcoin", "investment", "double your money", "profit",
                "trading", "binance", "wallet", "mining", "forex", "signal group"
            ],
            "Lottery/Prize": [
                "lottery", "winner", "prize", "congratulations", "won", "claim",
                "lucky draw", "reward", "cashback", "gift voucher"
            ],
            "Phishing/Bank": [
                "account locked", "verify identity", "kyc", "pan card", "bank account",
                "password", "otp", "suspend", "update now", "refund pending", "customer care"
            ],
            "Emotional/Charity": [
                "help needed", "emergency", "donation", "hospital",
                "critical condition", "god bless", "accident", "medical emergency"
            ],
            "UPI/Payment Scam": [
                "upi", "scan and pay", "qr", "collect request", "payment request",
                "processing fee", "advance payment", "refund", "merchant support",
                "release payment", "security deposit"
            ],
            "Voice/Call Scam": [
                "call me", "customer support", "refund team", "helpline", "remote access",
                "screen share", "install app", "anydesk", "teamviewer"
            ]
        }

        self.emotion_keywords = {
            "Urgency (Fear of Missing Out)": [
                "urgent", "immediately", "act now", "limited time", "hurry", "expires",
                "deadline", "today only", "last chance", "jaldi", "abhi"
            ],
            "Fear (Loss Aversion)": [
                "risk", "danger", "alert", "warning", "suspended", "blocked",
                "legal action", "arrest", "police", "fir", "freeze"
            ],
            "Greed (High Reward)": [
                "exclusive", "secret", "fortune", "millionaire", "billionaire",
                "guaranteed", "100%", "free", "bonus", "cash"
            ],
            "Curiosity (Information Gap)": [
                "shocking", "you won't believe", "they are hiding this", "truth about",
                "exposed", "magic trick"
            ],
            "Authority (Obedience)": [
                "govt", "official", "police", "court", "tax department", "ceo", "admin",
                "rbi", "sebi", "npci", "bank manager", "support executive"
            ]
        }

        self.bias_map = {
            "Urgency (Fear of Missing Out)": "Scarcity Bias",
            "Fear (Loss Aversion)": "Fear Bias",
            "Greed (High Reward)": "Greed Bias",
            "Curiosity (Information Gap)": "Curiosity Gap",
            "Authority (Obedience)": "Authority Bias"
        }

        self.language_profiles = {
            "Hindi/Hinglish": [
                "bhai", "dosto", "paisa", "kamaye", "offer", "loot", "dhamaaka", "jio",
                "yojana", "lakshmi", "karo", "jaldi", "turant", "abhi", "bhejo",
                "madad", "bank", "paise", "jeet gaye", "inaam"
            ],
            "Bengali cues": ["taka", "bikash", "apni", "tatka", "proyojon", "loan"],
            "Tamil cues": ["udan", "seithi", "panam", "avasaram", "otp anuppu"],
            "Marathi cues": ["paisa", "lavkar", "tatkal", "madat kara", "bakshis"]
        }

        self.visual_red_flags = {
            "QR or payment prompt visible": [
                "qr", "scan", "scan and pay", "pay now", "collect request", "payment request"
            ],
            "Fake authority branding likely": [
                "official", "customer care", "helpline", "rbi", "npci", "bank", "govt", "verified"
            ],
            "Pressure banner / urgent CTA": [
                "urgent", "immediately", "limited time", "expires", "blocked", "suspended"
            ],
            "Prize / payout styling": [
                "winner", "reward", "cashback", "free gift", "bonus", "claim now"
            ]
        }

        self.shortener_domains = {
            "bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "shorturl.at", "t.co", "goo.gl"
        }
        self.brand_domains = {
            "googlepay": ["pay.google.com"],
            "gpay": ["pay.google.com"],
            "phonepe": ["phonepe.com"],
            "paytm": ["paytm.com"],
            "amazon": ["amazon.in", "amazon.com"],
            "flipkart": ["flipkart.com"],
            "sbi": ["sbi.co.in", "onlinesbi.sbi"],
            "hdfc": ["hdfcbank.com"],
            "icici": ["icicibank.com"],
            "axis": ["axisbank.com"],
            "rbi": ["rbi.org.in"],
            "npci": ["npci.org.in"],
            "airtel": ["airtel.in"]
        }

    def analyze(self, text, image_context="", voice_transcript="", qr_payload="", victim_context=None):
        text = text or ""
        image_context = image_context or ""
        voice_transcript = voice_transcript or ""
        qr_payload = qr_payload or ""
        victim_context = victim_context or []

        combined_text = "\n".join(
            part for part in [text, image_context, voice_transcript, qr_payload] if part
        ).strip()
        text_lower = combined_text.lower()

        detected_categories = {}
        for category, keywords in self.scam_patterns.items():
            count = sum(1 for word in keywords if word in text_lower)
            if count > 0:
                detected_categories[category] = count

        primary_category = (
            max(detected_categories, key=detected_categories.get)
            if detected_categories else "General Suspicion"
        )

        found_emotions = []
        emotion_score = 0
        detected_biases = set()
        for emotion, keywords in self.emotion_keywords.items():
            for word in keywords:
                if word in text_lower:
                    found_emotions.append(word)
                    detected_biases.add(self.bias_map[emotion])
                    emotion_score += 15
        emotion_score = min(100, emotion_score)

        too_good_score = 0
        if "free" in text_lower or "guaranteed" in text_lower:
            too_good_score += 30
        if "per day" in text_lower or "daily" in text_lower:
            too_good_score += 30
        if re.search(r"\d{4,}", combined_text):
            too_good_score += 20
        if "click" in text_lower or "link" in text_lower:
            too_good_score += 10
        too_good_score = min(100, too_good_score)

        screenshot_analysis = self._analyze_screenshot_context(image_context, text_lower)
        payment_analysis = self._analyze_payment_risk(combined_text, text_lower, qr_payload)
        voice_analysis = self._analyze_voice_transcript(voice_transcript)
        brand_analysis = self._analyze_brand_and_links(combined_text)
        language_analysis = self._analyze_language(combined_text)
        victim_guidance = self._build_victim_guidance(victim_context, payment_analysis, brand_analysis)

        scam_intensity = sum(detected_categories.values()) * 20
        manipulation_score = int(
            (scam_intensity * 0.22)
            + (emotion_score * 0.16)
            + (too_good_score * 0.12)
            + (screenshot_analysis["score"] * 0.12)
            + (payment_analysis["score"] * 0.14)
            + (voice_analysis["score"] * 0.10)
            + (brand_analysis["score"] * 0.14)
        )
        manipulation_score = min(100, manipulation_score)

        if manipulation_score < 20 and len(combined_text.split()) > 3:
            manipulation_score = 5

        source_credibility = "Medium"
        source_reason = "No verifiable source found."
        if brand_analysis["risk_level"] == "High":
            source_credibility = "Fake (Impersonation)"
            source_reason = "Brand name and link pattern look inconsistent."
        elif brand_analysis["risk_level"] == "Medium":
            source_credibility = "Low"
            source_reason = "External links or support identity need verification."
        elif "gov.in" in text_lower or "official" in text_lower:
            source_credibility = "Medium"
            source_reason = "Claims authority, but should still be cross-checked."

        questions = self._build_reality_questions(primary_category, payment_analysis["risk_level"], voice_analysis["risk_level"])
        advice = self._build_actions(manipulation_score, payment_analysis, screenshot_analysis, brand_analysis)

        confidence_breakdown = {
            "Scam Patterns": f"+{min(scam_intensity, 25)} ({primary_category} keyword overlap)",
            "Emotional Language": f"+{min(emotion_score, 20)} (Triggers: {', '.join(found_emotions[:3]) or 'none'})",
            "Visual / Screenshot Clues": f"+{min(screenshot_analysis['score'], 15)} ({screenshot_analysis['summary']})",
            "Payment / QR Risk": f"+{min(payment_analysis['score'], 15)} ({payment_analysis['summary']})",
            "Voice / Call Cues": f"+{min(voice_analysis['score'], 12)} ({voice_analysis['summary']})",
            "Brand / Link Integrity": f"+{min(brand_analysis['score'], 15)} ({brand_analysis['summary']})"
        }

        explainability = {
            "summary": self._build_explainability_summary(
                manipulation_score, payment_analysis, screenshot_analysis, voice_analysis, brand_analysis
            ),
            "evidence": self._build_explainable_evidence(
                combined_text,
                detected_categories,
                found_emotions,
                screenshot_analysis,
                payment_analysis,
                voice_analysis,
                brand_analysis
            ),
            "recommended_action_level": advice["priority"]
        }

        live_shield = {
            "level": "Danger" if manipulation_score > 75 else ("Warning" if manipulation_score > 45 else "Watch"),
            "alerts": self._build_live_alerts(payment_analysis, brand_analysis, voice_analysis, screenshot_analysis)
        }

        return {
            "manipulation_score": manipulation_score,
            "too_good_score": too_good_score,
            "emotion_score": emotion_score,
            "primary_category": primary_category,
            "verdict": (
                "High Risk" if manipulation_score > 75
                else ("Suspicious" if manipulation_score > 45 else "Likely Safe")
            ),
            "bias_detected": list(detected_biases) if detected_biases else ["None"],
            "language": language_analysis["primary_language"],
            "language_analysis": language_analysis,
            "source_credibility": source_credibility,
            "source_reason": source_reason,
            "reality_check_questions": questions,
            "human_reaction": (
                "This looks urgent or profitable. I should act fast."
                if manipulation_score > 70 else "Looks interesting. Maybe I should respond."
            ),
            "advice": advice["steps"],
            "action_recommendation": advice,
            "confidence_breakdown": confidence_breakdown,
            "screenshot_analysis": screenshot_analysis,
            "payment_analysis": payment_analysis,
            "voice_analysis": voice_analysis,
            "brand_analysis": brand_analysis,
            "victim_guidance": victim_guidance,
            "live_shield": live_shield,
            "explainability": explainability
        }

    def _analyze_screenshot_context(self, image_context, text_lower):
        context_lower = (image_context or "").lower()
        matched_cues = []
        score = 0

        for label, keywords in self.visual_red_flags.items():
            matches = [word for word in keywords if word in context_lower or word in text_lower]
            if matches:
                matched_cues.append({"label": label, "matches": matches[:3]})
                score += 20

        if image_context.strip() and re.search(r"(logo|stamp|banner|screenshot|chat|invoice|receipt)", context_lower):
            score += 10

        score = min(100, score)
        risk_level = "High" if score > 65 else ("Medium" if score > 30 else "Low")
        summary = (
            "Multiple visual scam cues detected"
            if matched_cues else
            ("No strong visual cue supplied" if not image_context.strip() else "Limited visual risk cues")
        )

        return {
            "enabled": bool(image_context.strip()),
            "score": score,
            "risk_level": risk_level,
            "summary": summary,
            "visual_cues": matched_cues if matched_cues else [{
                "label": "No specific screenshot red flag found",
                "matches": ["Add visible text, QR, logo, or receipt details for deeper analysis"]
            }]
        }

    def _analyze_payment_risk(self, combined_text, text_lower, qr_payload):
        upi_ids = re.findall(r"\b[\w.\-]{2,}@[a-zA-Z]{2,}\b", combined_text)
        amount_matches = re.findall(r"(?:rs\.?|inr|₹)\s?\d+(?:,\d{3})*(?:\.\d{1,2})?", combined_text, flags=re.IGNORECASE)
        qr_keywords = [word for word in ["qr", "scan", "scan and pay", "collect request", "payment request"] if word in text_lower]
        risky_keywords = [
            word for word in [
                "advance payment", "processing fee", "refund", "verification charge",
                "unlock", "release payment", "security deposit", "approval request"
            ] if word in text_lower
        ]

        qr_fields = self._parse_qr_payload(qr_payload)
        if qr_fields["upi_id"]:
            upi_ids = list(dict.fromkeys(upi_ids + [qr_fields["upi_id"]]))
        if qr_fields["amount"]:
            amount_matches = list(dict.fromkeys(amount_matches + [qr_fields["amount"]]))

        score = 0
        if upi_ids:
            score += 30
        if qr_keywords or qr_payload:
            score += 25
        if risky_keywords:
            score += 25
        if amount_matches:
            score += 10
        if "otp" in text_lower or "pin" in text_lower:
            score += 15
        score = min(100, score)

        risk_level = "High" if score > 65 else ("Medium" if score > 30 else "Low")
        summary_bits = []
        if upi_ids:
            summary_bits.append("UPI handle found")
        if qr_keywords or qr_payload:
            summary_bits.append("QR/payment trigger language found")
        if risky_keywords:
            summary_bits.append("fee/refund pressure language found")
        if qr_fields["payee"]:
            summary_bits.append("QR includes payee data")
        summary = ", ".join(summary_bits) if summary_bits else "No strong payment scam pattern detected"

        recommendation = (
            "Do not send money, scan QR, or approve collect requests until independently verified."
            if score > 30 else
            "Payment indicators are limited, but verify recipient identity before paying."
        )

        return {
            "score": score,
            "risk_level": risk_level,
            "summary": summary,
            "upi_ids": upi_ids[:3],
            "amounts": amount_matches[:3],
            "qr_signals": qr_keywords[:5],
            "payment_red_flags": risky_keywords[:5],
            "recommendation": recommendation,
            "qr_payload": qr_payload,
            "qr_details": qr_fields
        }

    def _parse_qr_payload(self, qr_payload):
        payload = qr_payload or ""
        upi_match = re.search(r"pa=([^&\s]+)", payload, flags=re.IGNORECASE)
        amount_match = re.search(r"am=([^&\s]+)", payload, flags=re.IGNORECASE)
        payee_match = re.search(r"pn=([^&\s]+)", payload, flags=re.IGNORECASE)
        return {
            "raw": payload,
            "upi_id": upi_match.group(1) if upi_match else "",
            "amount": amount_match.group(1) if amount_match else "",
            "payee": payee_match.group(1).replace("%20", " ") if payee_match else ""
        }

    def _analyze_voice_transcript(self, voice_transcript):
        transcript = (voice_transcript or "").lower().strip()
        if not transcript:
            return {
                "enabled": False,
                "score": 0,
                "risk_level": "Low",
                "summary": "No voice or call transcript supplied.",
                "red_flags": []
            }

        call_flags = []
        score = 0
        patterns = {
            "Impersonation / support identity claim": ["customer care", "support team", "bank officer", "rbi", "police"],
            "Remote access request": ["anydesk", "teamviewer", "screen share", "remote access", "download app"],
            "Payment pressure on call": ["scan qr", "collect request", "pay now", "transfer immediately"],
            "Threat / fear call scripting": ["account blocked", "legal action", "freeze your account", "otp now"]
        }
        for label, keywords in patterns.items():
            matches = [item for item in keywords if item in transcript]
            if matches:
                call_flags.append({"label": label, "matches": matches[:3]})
                score += 25

        score = min(100, score)
        risk_level = "High" if score > 60 else ("Medium" if score > 25 else "Low")
        summary = "Call transcript contains social-engineering cues." if call_flags else "Transcript supplied, but few explicit call-scam cues found."

        return {
            "enabled": True,
            "score": score,
            "risk_level": risk_level,
            "summary": summary,
            "red_flags": call_flags
        }

    def _analyze_brand_and_links(self, combined_text):
        urls = re.findall(r"(https?://[^\s]+|www\.[^\s]+)", combined_text, flags=re.IGNORECASE)
        url_details = []
        matched_brands = []
        score = 0

        lower_text = combined_text.lower()
        for brand, valid_domains in self.brand_domains.items():
            if brand in lower_text:
                matched_brands.append(brand.upper())

        for raw_url in urls:
            normalized = raw_url if raw_url.startswith("http") else f"https://{raw_url}"
            parsed = urlparse(normalized)
            domain = parsed.netloc.lower().replace("www.", "")
            reason = []

            if domain in self.shortener_domains:
                reason.append("shortened link")
                score += 15

            for brand, valid_domains in self.brand_domains.items():
                if brand in domain and domain not in valid_domains:
                    reason.append(f"{brand.upper()}-like domain mismatch")
                    score += 25

            if any(marker in domain for marker in ["support", "verify", "secure", "help", "care"]) and not any(domain.endswith(valid) for values in self.brand_domains.values() for valid in values):
                reason.append("support-style external domain")
                score += 10

            url_details.append({
                "url": raw_url,
                "domain": domain,
                "reasons": reason or ["No obvious issue found"]
            })

        if matched_brands and not urls:
            score += 10

        score = min(100, score)
        risk_level = "High" if score > 45 else ("Medium" if score > 15 else "Low")
        summary = "Potential brand impersonation or link mismatch detected." if score else "No strong impersonation or link mismatch signal."

        return {
            "score": score,
            "risk_level": risk_level,
            "summary": summary,
            "matched_brands": matched_brands[:5],
            "links": url_details[:5]
        }

    def _analyze_language(self, combined_text):
        lowered = combined_text.lower()
        devanagari = bool(re.search(r"[\u0900-\u097F]", combined_text))
        detected = []
        for label, keywords in self.language_profiles.items():
            matches = [word for word in keywords if word in lowered]
            if matches:
                detected.append({"label": label, "matches": matches[:4]})

        if devanagari:
            primary = "Hindi/Devanagari"
        elif detected:
            primary = detected[0]["label"]
        else:
            primary = "English"

        return {
            "primary_language": primary if primary != "Hindi/Hinglish" else "Hinglish/Mixed",
            "detected_profiles": detected if detected else [{"label": "English", "matches": []}]
        }

    def _build_victim_guidance(self, victim_context, payment_analysis, brand_analysis):
        guidance_map = {
            "paid_money": [
                "Call your bank or wallet support immediately and request transaction hold or dispute.",
                "Report the UPI ID or transaction in your banking app if that option exists.",
                "Preserve screenshots, QR details, and payment proof for complaint filing."
            ],
            "shared_otp": [
                "Reset banking, email, and wallet passwords right away.",
                "Call the bank to freeze risky transactions and revoke session access.",
                "Review linked devices and active logins immediately."
            ],
            "shared_bank_details": [
                "Monitor statements, disable auto-debit if needed, and alert your bank.",
                "Change net-banking password and UPI PIN.",
                "Treat any new caller claiming to help as untrusted."
            ],
            "installed_app": [
                "Uninstall the remote-access or suspicious app immediately.",
                "Review screen-sharing, accessibility, and unknown app permissions.",
                "Run device security scan and change sensitive passwords from a clean device."
            ]
        }

        enabled_steps = []
        for item in victim_context:
            enabled_steps.extend(guidance_map.get(item, []))

        if not enabled_steps and payment_analysis["risk_level"] == "High":
            enabled_steps = [
                "If you have not paid yet, stop immediately and do not approve the request.",
                "If you already paid, contact your bank or UPI provider now with the transaction reference."
            ]

        priority = "Immediate" if enabled_steps or brand_analysis["risk_level"] == "High" else "Precautionary"
        return {
            "priority": priority,
            "steps": enabled_steps if enabled_steps else [
                "No post-incident signal selected. Use this section if money, OTP, or access has already been shared."
            ]
        }

    def _build_reality_questions(self, primary_category, payment_risk_level, voice_risk_level):
        if primary_category == "Job Scam":
            return [
                "Did you apply for this role yourself, or did they contact you randomly?",
                "Are they asking for registration, training, or deposit money before joining?",
                "Is the salary or payout realistic for the job being offered?"
            ]
        if primary_category == "Crypto/Investment":
            return [
                "Is the return far above normal bank or regulated market returns?",
                "Are they pushing you to invest immediately without due diligence?",
                "Can you verify the platform through SEBI, RBI, or a known exchange?"
            ]
        if payment_risk_level in ["High", "Medium"]:
            return [
                "Why are they asking you to scan a QR or approve a collect request?",
                "Did you verify the UPI ID or merchant with an official source you found yourself?",
                "Are they using refund, KYC, prize, or emergency pressure to make you pay?"
            ]
        if voice_risk_level in ["High", "Medium"]:
            return [
                "Why is the caller rushing you instead of giving time to verify independently?",
                "Did they ask for OTP, remote access, or app installation on the call?",
                "Can you hang up and call the official helpline from the brand's real website or app?"
            ]
        return [
            "Do you know this sender or brand from a trusted prior interaction?",
            "Why is the message creating urgency instead of giving clear proof?",
            "Have you verified the claim on an official site or independent search?"
        ]

    def _build_actions(self, manipulation_score, payment_analysis, screenshot_analysis, brand_analysis):
        if manipulation_score > 75 or payment_analysis["risk_level"] == "High":
            return {
                "priority": "Block Immediately",
                "steps": [
                    "Do not click links, scan QR codes, or approve any payment request.",
                    "Do not share OTP, UPI PIN, bank details, or screen-sharing access.",
                    "Verify the claim manually using the official app, website, or helpline.",
                    "Block and report the sender if they continue pressuring you."
                ]
            }
        if manipulation_score > 45 or screenshot_analysis["risk_level"] == "Medium" or brand_analysis["risk_level"] == "Medium":
            return {
                "priority": "Verify First",
                "steps": [
                    "Pause before acting and cross-check the sender independently.",
                    "Treat payment requests, urgent screenshots, and support links as untrusted until verified.",
                    "Ask a trusted person to review the message before sharing or paying."
                ]
            }
        return {
            "priority": "Monitor",
            "steps": [
                "No major red flag found, but keep verifying unknown senders.",
                "Avoid sharing sensitive credentials even if the message looks normal."
            ]
        }

    def _build_explainable_evidence(self, combined_text, detected_categories, found_emotions, screenshot_analysis, payment_analysis, voice_analysis, brand_analysis):
        evidence = []

        for category, count in sorted(detected_categories.items(), key=lambda item: item[1], reverse=True)[:3]:
            evidence.append({
                "type": "Category Signal",
                "title": category,
                "detail": f"Matched {count} keyword cues linked to this scam pattern."
            })

        if found_emotions:
            evidence.append({
                "type": "Emotion Trigger",
                "title": "Pressure Language",
                "detail": f"Words like {', '.join(found_emotions[:4])} are commonly used to rush victims."
            })

        if screenshot_analysis["enabled"]:
            for cue in screenshot_analysis["visual_cues"][:2]:
                evidence.append({
                    "type": "Screenshot/Image",
                    "title": cue["label"],
                    "detail": f"Observed cues: {', '.join(cue['matches'])}."
                })

        if payment_analysis["upi_ids"] or payment_analysis["payment_red_flags"] or payment_analysis["qr_payload"]:
            details = []
            if payment_analysis["upi_ids"]:
                details.append(f"UPI: {', '.join(payment_analysis['upi_ids'])}")
            if payment_analysis["qr_details"]["payee"]:
                details.append(f"Payee: {payment_analysis['qr_details']['payee']}")
            if payment_analysis["payment_red_flags"]:
                details.append(f"Flags: {', '.join(payment_analysis['payment_red_flags'])}")
            evidence.append({
                "type": "Payment Risk",
                "title": "UPI/QR indicators",
                "detail": " | ".join(details)
            })

        if voice_analysis["enabled"] and voice_analysis["red_flags"]:
            evidence.append({
                "type": "Voice Transcript",
                "title": voice_analysis["red_flags"][0]["label"],
                "detail": f"Transcript cues: {', '.join(voice_analysis['red_flags'][0]['matches'])}."
            })

        if brand_analysis["matched_brands"] or any(item["reasons"] != ["No obvious issue found"] for item in brand_analysis["links"]):
            mismatch = next((item for item in brand_analysis["links"] if item["reasons"] != ["No obvious issue found"]), None)
            detail = (
                f"Matched brands: {', '.join(brand_analysis['matched_brands'])}."
                if brand_analysis["matched_brands"] else "Brand identity references detected."
            )
            if mismatch:
                detail += f" Link issue: {mismatch['domain']} -> {', '.join(mismatch['reasons'])}."
            evidence.append({
                "type": "Brand/Link",
                "title": "Impersonation risk",
                "detail": detail
            })

        if not evidence and combined_text.strip():
            evidence.append({
                "type": "Baseline",
                "title": "Low signal input",
                "detail": "Not enough strong scam markers were found in the provided content."
            })

        return evidence

    def _build_explainability_summary(self, manipulation_score, payment_analysis, screenshot_analysis, voice_analysis, brand_analysis):
        if manipulation_score > 75:
            return "High-confidence warning driven by combined language, payment, brand, and visual cues."
        if payment_analysis["risk_level"] == "High":
            return "Payment-specific risk is the main reason this content was flagged."
        if voice_analysis["risk_level"] == "High":
            return "Call transcript strongly resembles scripted social-engineering behavior."
        if brand_analysis["risk_level"] == "High":
            return "Brand impersonation and link mismatch signals are the biggest concern."
        if screenshot_analysis["risk_level"] == "High":
            return "Screenshot-side cues strongly resemble common scam layouts and prompts."
        if manipulation_score > 45:
            return "Several suspicious indicators were found, but manual verification is still recommended."
        return "The content has limited scam signals based on the provided inputs."

    def _build_live_alerts(self, payment_analysis, brand_analysis, voice_analysis, screenshot_analysis):
        alerts = []
        if payment_analysis["risk_level"] in ["High", "Medium"]:
            alerts.append("Payment or QR prompt detected")
        if brand_analysis["risk_level"] in ["High", "Medium"]:
            alerts.append("Brand or link integrity check failed")
        if voice_analysis["risk_level"] in ["High", "Medium"]:
            alerts.append("Call transcript pressure detected")
        if screenshot_analysis["risk_level"] in ["High", "Medium"]:
            alerts.append("Visual screenshot cues look suspicious")
        return alerts if alerts else ["No major real-time warning yet"]


if __name__ == "__main__":
    analyzer = Analyzer()
    sample = "Refund pending. Scan this QR and approve collect request from payhelp@ybl. Visit https://phonepe-refund-help.xyz."
    print(
        analyzer.analyze(
            sample,
            "Screenshot shows QR code, fake bank logo, urgent banner.",
            "Hello sir from customer care, install AnyDesk and share OTP now.",
            "upi://pay?pa=payhelp@ybl&pn=Refund Desk&am=4999"
        )
    )
