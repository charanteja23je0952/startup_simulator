import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from agents import run_all_agents

app = Flask(__name__)
CORS(app)

@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json()
    idea = data.get("idea", "").strip()
    budget = data.get("budget", 10)

    if not idea:
        return jsonify({"error": "Please provide a startup idea"}), 400

    try:
        results = run_all_agents(idea, budget)
    except RuntimeError as e:
        # e.g. missing GROQ_API_KEY
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Simulation failed: {e}"}), 500

    return jsonify({"success": True, **results})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)