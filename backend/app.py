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

    results = run_all_agents(idea, budget)
    return jsonify({"success": True, "agents": results})

if __name__ == "__main__":
    app.run(debug=True, port=5000)