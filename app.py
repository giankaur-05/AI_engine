from flask import Flask, request, jsonify, render_template
from analyzer import Analyzer
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
analyzer = Analyzer()

@app.route('/')
def home():
    return render_template('analyzer.html', active_page='analyzer')

@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html', active_page='roadmap')

@app.route('/trends')
def trends():
    return render_template('trends.html', active_page='trends')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    image_context = data.get('image_context', '')
    voice_transcript = data.get('voice_transcript', '')
    qr_payload = data.get('qr_payload', '')
    victim_context = data.get('victim_context', [])
    
    if not text and not image_context and not voice_transcript and not qr_payload:
        return jsonify({"error": "No text, image context, transcript, or QR data provided"}), 400
        
    result = analyzer.analyze(
        text,
        image_context=image_context,
        voice_transcript=voice_transcript,
        qr_payload=qr_payload,
        victim_context=victim_context
    )
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
