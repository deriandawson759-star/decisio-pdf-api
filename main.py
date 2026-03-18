"""
DECISIO AGENCY — API V2
Flask + Claude API + Playwright (Chromium headless)
Architecture : JSON structuré → HTML/CSS pixel-perfect → PDF
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import os
import traceback

from ai_analyzer import analyze_business
from pdf_generator import generate_pdf_from_data
from scoring import calculate_scores

app = Flask(__name__)
CORS(app, origins=[
    "https://decisio-final.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000"
])

# ─────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "DECISIO PDF API V2",
        "engine": "Playwright + Chromium"
    })

# ─────────────────────────────────────────
# GENERATE PDF — ENDPOINT PRINCIPAL
# ─────────────────────────────────────────

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_endpoint():
    """
    Reçoit les données client → Claude analyse → Playwright génère PDF.

    Body JSON:
    {
        "nom": "Lucas Bernard",
        "secteur": "Électricien indépendant",
        "mode": "premium",
        "date": "18 mars 2026",         (optionnel)
        "probleme": "...",
        "ca_mensuel": 3200,
        "charges_mensuel": 1800,
        "objectif_net": 2800,
        "nb_employes": 0,
        "annees_activite": 5,
        "contexte": "..."               (optionnel)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Body JSON requis"}), 400

        nom  = data.get('nom', 'Client')
        mode = data.get('mode', 'premium')

        # Analyse IA complète
        analysis = analyze_business(data)

        # Scores automatiques
        scores = calculate_scores(analysis)

        # Génération PDF via Playwright
        pdf_bytes = generate_pdf_from_data(data, analysis, scores, mode)

        slug     = nom.replace(' ', '_')[:20]
        filename = f"DECISIO_Audit_{slug}.pdf"

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# ANALYZE ONLY (sans PDF)
# ─────────────────────────────────────────

@app.route('/analyze', methods=['POST'])
def analyze_only():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Body JSON requis"}), 400
        analysis = analyze_business(data)
        scores   = calculate_scores(analysis)
        return jsonify({"success": True, "analysis": analysis, "scores": scores})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
