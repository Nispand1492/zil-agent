from flask import Flask, jsonify, request
from flask_cors import CORS

from agent import run_agent

app = Flask(__name__)
CORS(app, origins=["https://salmon-mud-01e8de810.1.azurestaticapps.net"])
@app.route("/", methods=["GET"])
def index():
    return "Zil's LangChain Agent is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "zil@example.com")
    prompt = data["prompt"]
    response = run_agent(prompt, user_id=user_id)
    return jsonify({"response": response})
