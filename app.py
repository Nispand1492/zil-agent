from flask import Flask, request, jsonify
from agent import run_agent
import yaml


app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "zil@example.com")
    prompt = data["prompt"]
    response = run_agent(prompt, user_id=user_id)
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

@app.route("/reset-profile", methods=["POST"])
def reset_profile():
    try:
        with open("default_profile.yaml", "r") as default_file:
            default_config = yaml.safe_load(default_file)
        with open("config_zil.yaml", "w") as config_file:
            yaml.dump(default_config, config_file)
        return jsonify({"message": "Profile reset to empty default"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
