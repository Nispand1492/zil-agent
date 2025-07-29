from flask import Flask, request, jsonify
from agent import handle_query
import yaml


app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400
    query = data.get("prompt", "")
    if not query:
        return jsonify({"error": "Missing prompt"}), 400
    response = handle_query(query)
    return jsonify({"response": response})

@app.route("/", methods=["GET"])
def index():
    return "Zil's LangChain Agent is running!"


@app.route("/profile", methods=["GET"])
def profile():
    try:
        with open("config_zil.yaml", "r") as f:
            config = yaml.safe_load(f)
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
