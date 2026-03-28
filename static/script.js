let uploadedImageState = { file: null, ocrText: '', metadata: '', qrPayload: '', qrSummary: '' };
let selectedVictimSignals = new Set();
let latestAnalysisData = null;

async function analyzeText() {
    const text = getValue('inputText');
    const imageContext = getValue('imageContext');
    const voiceTranscript = getValue('voiceTranscript');

    if (!text && !imageContext && !voiceTranscript && !uploadedImageState.file && !uploadedImageState.qrPayload) {
        alert('Please add message text, screenshot clues, transcript, or an uploaded image first.');
        return;
    }

    showLoading(true);

    try {
        let finalText = text;
        let finalImageContext = imageContext;

        if (uploadedImageState.file) {
            const extraction = await extractImageSignals(uploadedImageState.file);
            uploadedImageState.ocrText = extraction.ocrText;
            uploadedImageState.metadata = extraction.metadata;
            uploadedImageState.qrPayload = extraction.qrPayload;
            uploadedImageState.qrSummary = extraction.qrSummary;
            updateImagePreview(uploadedImageState.file.name, extraction);

            if (extraction.ocrText) {
                finalText = [text, extraction.ocrText].filter(Boolean).join('\n');
            }

            finalImageContext = [imageContext, extraction.metadata, extraction.qrSummary].filter(Boolean).join('. ');
        }

        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: finalText,
                image_context: finalImageContext,
                voice_transcript: voiceTranscript,
                qr_payload: uploadedImageState.qrPayload,
                victim_context: Array.from(selectedVictimSignals)
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }

        latestAnalysisData = data;
        showResults(data);
    } catch (error) {
        alert(error.message || 'Error connecting to server!');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function getValue(id) {
    const el = document.getElementById(id);
    return el ? el.value.trim() : '';
}

function showLoading(isLoading) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    if (loading) loading.classList.toggle('hidden', !isLoading);
    if (results && isLoading) results.classList.add('hidden');
}

function showResults(data) {
    const results = document.getElementById('results');
    if (results) results.classList.remove('hidden');

    setText('verdictTitle', data.verdict);
    setText('verdictSubtitle', buildVerdictSubtitle(data));
    setWidth('riskMeterFill', data.manipulation_score);

    updateBar('manipulationBar', 'manipulationVal', data.manipulation_score);
    updateBar('tooGoodBar', 'tooGoodVal', data.too_good_score);
    updateBar('emotionBar', 'emotionVal', data.emotion_score);

    setText('humanReactionText', `"${data.human_reaction}"`);
    setText('aiReasoningText', `"${data.explainability.summary}"`);

    renderTagList('biasTags', data.bias_detected || [], 'bias-tag');
    renderConfidence(data.confidence_breakdown || {});
    renderList('questionsList', data.reality_check_questions || []);
    renderActionCards('actionButtons', data.action_recommendation?.steps || []);
    setText('actionPriority', data.action_recommendation?.priority || 'Verify First');

    setText('categoryText', data.primary_category || 'General Suspicion');
    setText('sourceText', data.source_credibility || 'Medium');
    setText('languageText', data.language || 'English');

    renderExplainability(data.explainability || {});
    renderScreenshotAnalysis(data.screenshot_analysis || {});
    renderPaymentAnalysis(data.payment_analysis || {});
    renderVoiceAnalysis(data.voice_analysis || {});
    renderBrandAnalysis(data.brand_analysis || {});
    renderLanguageAnalysis(data.language_analysis || {});
    renderVictimGuidance(data.victim_guidance || {});
    renderLiveShieldResults(data.live_shield || {});

    if (window.lucide) window.lucide.createIcons();
}

function buildVerdictSubtitle(data) {
    const parts = [];
    if (data.payment_analysis) parts.push(`Payment risk: ${data.payment_analysis.risk_level}`);
    if (data.brand_analysis) parts.push(`Link risk: ${data.brand_analysis.risk_level}`);
    if (data.voice_analysis?.enabled) parts.push(`Call risk: ${data.voice_analysis.risk_level}`);
    return parts.join(' | ') || 'High probability of manipulation detected.';
}

function renderConfidence(confidence) {
    const list = document.getElementById('confidenceList');
    if (!list) return;
    list.innerHTML = '';
    Object.entries(confidence).forEach(([key, value]) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${key}:</strong> ${value}`;
        list.appendChild(li);
    });
}

function renderExplainability(explainability) {
    setText('explainabilitySummary', explainability.summary || 'Why the model flagged this content.');
    const wrap = document.getElementById('evidenceList');
    if (!wrap) return;
    wrap.innerHTML = '';
    (explainability.evidence || []).forEach((item) => {
        const div = document.createElement('div');
        div.className = 'evidence-item';
        div.innerHTML = `<small>${item.type}</small><strong>${item.title}</strong><p>${item.detail}</p>`;
        wrap.appendChild(div);
    });
}

function renderScreenshotAnalysis(data) {
    setText('screenshotRisk', data.risk_level || 'Low');
    setText('screenshotSummary', data.summary || 'No screenshot clues supplied yet.');
    renderList('screenshotCues', (data.visual_cues || []).map((item) => `${item.label}: ${(item.matches || []).join(', ')}`));
}

function renderPaymentAnalysis(data) {
    setText('paymentRiskText', data.risk_level || 'Low');
    setText('paymentUpiText', (data.upi_ids || []).join(', ') || 'None');
    setText('paymentAmountText', (data.amounts || []).join(', ') || 'None');
    setText('paymentPayeeText', data.qr_details?.payee || 'Unknown');
    setText('paymentQrPayloadText', data.qr_payload ? trimText(data.qr_payload, 48) : 'Not decoded');
    setText('paymentRecommendation', data.recommendation || '');

    const flags = [];
    (data.qr_signals || []).forEach((item) => flags.push(`QR signal: ${item}`));
    (data.payment_red_flags || []).forEach((item) => flags.push(`Payment red flag: ${item}`));
    if (data.qr_details?.upi_id) flags.push(`QR UPI: ${data.qr_details.upi_id}`);
    if (flags.length === 0) flags.push(data.summary || 'No strong payment scam pattern detected.');
    renderList('paymentFlags', flags);
}

function renderVoiceAnalysis(data) {
    setText('voiceRiskText', data.risk_level || 'Low');
    setText('voiceSummary', data.summary || 'No voice transcript supplied yet.');
    const flags = (data.red_flags || []).map((item) => `${item.label}: ${(item.matches || []).join(', ')}`);
    renderList('voiceFlags', flags.length ? flags : ['No strong call-scam signal found.']);
}

function renderBrandAnalysis(data) {
    setText('brandRiskText', data.risk_level || 'Low');
    setText('brandSummary', data.summary || 'No strong impersonation signal yet.');
    renderTagList('brandTags', data.matched_brands || [], 'bias-tag');
    const links = (data.links || []).map((item) => `${item.domain}: ${(item.reasons || []).join(', ')}`);
    renderList('brandLinks', links.length ? links : ['No suspicious link pattern found.']);
}

function renderLanguageAnalysis(data) {
    setText('languagePrimaryText', data.primary_language || 'English');
    const profiles = (data.detected_profiles || []).map((item) => item.matches?.length ? `${item.label}: ${item.matches.join(', ')}` : item.label);
    renderList('languageProfiles', profiles);
}

function renderVictimGuidance(data) {
    setText('victimPriorityText', data.priority || 'Precautionary');
    renderActionCards('victimGuidanceList', data.steps || []);
}

function renderLiveShieldResults(data) {
    setText('liveShieldLevel', data.level || 'Watch');
    setText('liveShieldNote', (data.alerts || ['No major real-time warning yet'])[0]);
    renderTagList('liveShieldAlerts', data.alerts || [], 'status-badge');
}

function renderList(targetId, items) {
    const list = document.getElementById(targetId);
    if (!list) return;
    list.innerHTML = '';
    items.forEach((item) => {
        const li = document.createElement('li');
        li.innerText = item;
        list.appendChild(li);
    });
}

function renderActionCards(targetId, items) {
    const wrap = document.getElementById(targetId);
    if (!wrap) return;
    wrap.innerHTML = '';
    items.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'action-btn';
        div.innerText = item;
        wrap.appendChild(div);
    });
}

function renderTagList(targetId, items, className) {
    const wrap = document.getElementById(targetId);
    if (!wrap) return;
    wrap.innerHTML = '';
    items.forEach((item) => {
        const span = document.createElement('span');
        span.className = className;
        span.innerText = item;
        wrap.appendChild(span);
    });
}

function updateBar(barId, valId, value) {
    setWidth(barId, value);
    setText(valId, `${value}%`);
}

function setWidth(id, value) {
    const el = document.getElementById(id);
    if (el) el.style.width = `${value}%`;
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.innerText = value;
}

async function handleImageUpload(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) {
        clearImageUpload();
        return;
    }

    uploadedImageState = { file, ocrText: '', metadata: '', qrPayload: '', qrSummary: '' };
    setText('uploadStatus', `${file.name} selected`);
    document.getElementById('ocrPreview')?.classList.remove('hidden');
    setText('previewName', file.name);
    setText('ocrStatusText', 'Image attached. OCR and QR scan will run during analysis.');
    updateLiveShield();
    if (window.lucide) window.lucide.createIcons();
}

function clearImageUpload() {
    uploadedImageState = { file: null, ocrText: '', metadata: '', qrPayload: '', qrSummary: '' };
    const input = document.getElementById('imageUpload');
    if (input) input.value = '';
    setText('uploadStatus', 'No image selected');
    document.getElementById('ocrPreview')?.classList.add('hidden');
    setText('ocrStatusText', 'OCR / QR scan not run yet.');
    const ocr = document.getElementById('ocrExtractBox');
    const qr = document.getElementById('qrExtractBox');
    if (ocr) { ocr.classList.add('hidden'); ocr.innerText = ''; }
    if (qr) { qr.classList.add('hidden'); qr.innerText = ''; }
    updateLiveShield();
}

async function extractImageSignals(file) {
    const metadata = await readImageMetadata(file);
    const imageBitmap = await loadImageBitmap(file);
    const qrPayload = decodeQrFromImage(imageBitmap);
    const ocrText = await runOcr(file);
    return {
        metadata,
        qrPayload,
        qrSummary: qrPayload ? `QR decoded: ${trimText(qrPayload, 120)}` : 'QR not detected from image.',
        ocrText,
        message: ocrText ? 'OCR completed and merged into analysis.' : 'No readable text found from OCR.'
    };
}

async function runOcr(file) {
    if (!window.Tesseract) return '';
    try {
        const result = await window.Tesseract.recognize(file, 'eng');
        return (result.data.text || '').replace(/\s+\n/g, '\n').trim();
    } catch (error) {
        console.error(error);
        return '';
    }
}

function decodeQrFromImage(image) {
    if (!window.jsQR || !image) return '';
    const canvas = document.createElement('canvas');
    canvas.width = image.width;
    canvas.height = image.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(image, 0, 0);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const code = window.jsQR(imageData.data, imageData.width, imageData.height);
    return code ? code.data : '';
}

function loadImageBitmap(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => {
            const image = new Image();
            image.onload = () => resolve(image);
            image.onerror = reject;
            image.src = event.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function readImageMetadata(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (event) => {
            const image = new Image();
            image.onload = () => resolve(`Uploaded image: ${file.name}, ${Math.round(file.size / 1024)} KB, ${image.width}x${image.height}`);
            image.onerror = () => resolve(`Uploaded image: ${file.name}, ${Math.round(file.size / 1024)} KB`);
            image.src = event.target.result;
        };
        reader.onerror = () => resolve(`Uploaded image: ${file.name}, ${Math.round(file.size / 1024)} KB`);
        reader.readAsDataURL(file);
    });
}

function updateImagePreview(fileName, extraction) {
    document.getElementById('ocrPreview')?.classList.remove('hidden');
    setText('previewName', fileName);
    setText('ocrStatusText', extraction.qrPayload ? 'OCR + QR extraction completed.' : extraction.message);

    const ocr = document.getElementById('ocrExtractBox');
    if (ocr) {
        if (extraction.ocrText) {
            ocr.classList.remove('hidden');
            ocr.innerText = extraction.ocrText.slice(0, 600);
        } else {
            ocr.classList.add('hidden');
            ocr.innerText = '';
        }
    }

    const qr = document.getElementById('qrExtractBox');
    if (qr) {
        if (extraction.qrPayload) {
            qr.classList.remove('hidden');
            qr.innerText = `QR Payload: ${trimText(extraction.qrPayload, 200)}`;
        } else {
            qr.classList.add('hidden');
            qr.innerText = '';
        }
    }
}

function toggleVictimChip(event) {
    const chip = event.currentTarget;
    const value = chip.dataset.victim;
    if (selectedVictimSignals.has(value)) {
        selectedVictimSignals.delete(value);
        chip.classList.remove('chip-active');
    } else {
        selectedVictimSignals.add(value);
        chip.classList.add('chip-active');
    }
}

function updateLiveShield() {
    const textBlob = [
        getValue('inputText'),
        getValue('imageContext'),
        getValue('voiceTranscript'),
        uploadedImageState.qrPayload
    ].join(' ').toLowerCase();

    const alerts = [];
    if (/qr|upi|collect request|pay now|refund/.test(textBlob)) alerts.push('Payment or QR prompt detected');
    if (/otp|pin|urgent|blocked|legal action/.test(textBlob)) alerts.push('Urgency / credential pressure detected');
    if (/anydesk|teamviewer|screen share|customer care/.test(textBlob)) alerts.push('Voice or remote-access scam cue detected');
    if (/bit\.ly|tinyurl|support|verify|secure/.test(textBlob)) alerts.push('Potential impersonation or external support link detected');
    if (uploadedImageState.file) alerts.push('Uploaded image ready for OCR / QR analysis');

    setText('liveShieldLevel', alerts.length > 2 ? 'Danger' : (alerts.length > 0 ? 'Warning' : 'Watch'));
    setText('liveShieldNote', alerts[0] || 'No major real-time warning yet');
    renderTagList('liveShieldAlerts', alerts.length ? alerts : ['No major real-time warning yet'], 'status-badge');
}

function startVoiceCapture() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        setText('voiceStatus', 'Mic capture not supported in this browser. Paste transcript manually.');
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    setText('voiceStatus', 'Listening...');
    recognition.start();

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const el = document.getElementById('voiceTranscript');
        if (el) el.value = [el.value.trim(), transcript].filter(Boolean).join(' ');
        setText('voiceStatus', 'Transcript captured');
        updateLiveShield();
    };

    recognition.onerror = () => setText('voiceStatus', 'Mic capture failed. Paste transcript manually.');
}

function downloadEvidenceReport() {
    if (!latestAnalysisData) {
        alert('Run analysis first to generate the report.');
        return;
    }

    const lines = [
        'AI Scam Analysis Report',
        '',
        `Verdict: ${latestAnalysisData.verdict}`,
        `Category: ${latestAnalysisData.primary_category}`,
        `Language: ${latestAnalysisData.language}`,
        `Source Credibility: ${latestAnalysisData.source_credibility}`,
        '',
        'Evidence:'
    ];
    (latestAnalysisData.explainability?.evidence || []).forEach((item) => {
        lines.push(`- [${item.type}] ${item.title}: ${item.detail}`);
    });
    lines.push('', 'Action Recommendation:');
    (latestAnalysisData.action_recommendation?.steps || []).forEach((step) => lines.push(`- ${step}`));
    lines.push('', 'Post-Scam Rescue:');
    (latestAnalysisData.victim_guidance?.steps || []).forEach((step) => lines.push(`- ${step}`));

    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'scam-evidence-report.txt';
    a.click();
    URL.revokeObjectURL(url);
}

function loadExample(type) {
    const examples = {
        job: {
            text: 'Hiring now! Earn Rs 50,000/day from home. No experience needed. Pay registration fee and join immediately.',
            image: 'Screenshot shows HR chat, fake company logo, and QR code to pay joining fee.',
            voice: ''
        },
        crypto: {
            text: 'Invest Rs 5000 today and get guaranteed double return by tomorrow. Join our private signal group now.',
            image: 'Image shows green profit dashboard, bonus banner, and urgent countdown.',
            voice: ''
        },
        payment: {
            text: 'Refund pending. Scan this QR or approve collect request from payhelp@ybl to receive money. Visit https://phonepe-refund-help.xyz',
            image: 'Screenshot shows fake bank logo, QR code, and blocked-account warning.',
            voice: ''
        },
        voice: {
            text: 'Your account is under review. Call support now.',
            image: '',
            voice: 'Hello sir, I am from customer care. Install AnyDesk right now and share OTP to stop account block.'
        }
    };

    const example = examples[type] || { text: '', image: '', voice: '' };
    const textEl = document.getElementById('inputText');
    const imageEl = document.getElementById('imageContext');
    const voiceEl = document.getElementById('voiceTranscript');
    if (textEl) textEl.value = example.text;
    if (imageEl) imageEl.value = example.image;
    if (voiceEl) voiceEl.value = example.voice;
    updateLiveShield();
}

function pasteClipboard() {
    navigator.clipboard.readText().then((text) => {
        const el = document.getElementById('inputText');
        if (el) el.value = text;
        updateLiveShield();
    });
}

function clearText() {
    ['inputText', 'imageContext', 'voiceTranscript'].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    selectedVictimSignals.clear();
    document.querySelectorAll('.toggle-chip').forEach((chip) => chip.classList.remove('chip-active'));
    clearImageUpload();
    document.getElementById('results')?.classList.add('hidden');
    latestAnalysisData = null;
    updateLiveShield();
}

function trimText(text, maxLength) {
    return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
}

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('particles');
    if (container) {
        for (let i = 0; i < 50; i += 1) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.width = `${Math.random() * 3}px`;
            particle.style.height = particle.style.width;
            particle.style.animationDuration = `${10 + (Math.random() * 20)}s`;
            particle.style.animationDelay = `${Math.random() * 5}s`;
            container.appendChild(particle);
        }
    }
    updateLiveShield();
});

function openSimulation(type) {
    const modal = document.getElementById('simModal');
    const title = document.getElementById('modalTitle');
    const loadingText = document.getElementById('modalLoadingText');
    const successText = document.getElementById('modalSuccessText');
    const details = document.getElementById('modalDetails');
    const step1 = document.getElementById('modalStep1');
    const step2 = document.getElementById('modalStep2');
    if (!modal || !title || !loadingText || !successText || !details || !step1 || !step2) return;

    const config = {
        fintech: ['Fintech API Integration', 'Connecting to UPI banking gateway...', 'Transaction blocked successfully!', 'Detected fraudulent UPI ID and prevented a suspicious collect request.'],
        govt: ['Govt Cyber Portal Sync', 'Packaging complaint evidence...', 'Report kit ready', 'Evidence report prepared for complaint submission flow.'],
        extension: ['Browser Shield Extension', 'Scanning live web content...', 'Live warning triggered', 'Potential scam overlay warning raised before click-through.'],
        social: ['Social Awareness Module', 'Generating safety training module...', 'Awareness module created', 'User received a scam-spotting micro lesson.']
    };
    const data = config[type];
    if (!data) return;

    step1.classList.remove('hidden');
    step2.classList.add('hidden');
    modal.classList.remove('hidden');
    modal.style.opacity = '1';
    modal.style.pointerEvents = 'all';
    title.innerText = data[0];
    loadingText.innerText = data[1];
    successText.innerText = data[2];
    details.innerText = data[3];

    setTimeout(() => {
        step1.classList.add('hidden');
        step2.classList.remove('hidden');
        if (window.lucide) window.lucide.createIcons();
    }, 1500);
}

function closeSimulation() {
    const modal = document.getElementById('simModal');
    if (!modal) return;
    modal.style.opacity = '0';
    modal.style.pointerEvents = 'none';
    setTimeout(() => modal.classList.add('hidden'), 200);
}
