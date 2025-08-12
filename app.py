from flask import Flask, request, jsonify
from agent import run_agent
from utils.dbutils import get_user_profile, upsert_user_profile

from flask_cors import CORS
from agent import run_agent


app = Flask(__name__)
CORS(app, origins=["https://salmon-mud-01e8de810.1.azurestaticapps.net"])

@app.route("/healthz", methods=["GET"])
def healthz():
    try:
        # Optional: check Cosmos connection
        get_user_profile("healthcheck@example.com")
        return "OK", 200
    except Exception as e:
        return f"Health check failed: {e}", 500


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)

    if not data or "prompt" not in data:
        return jsonify({"error": "Missing prompt"}), 400

    user_id = data.get("user_id", "zil@example.com")
    try:
        response = run_agent(data["prompt"], user_id)
        return jsonify({"response": response})
    except Exception as e:
        print(f"[ERROR] /chat failed: {e}")
        return jsonify({"error": "Agent failure"}), 500


@app.route("/", methods=["GET"])
def index():
    return "Zil's LangChain Agent is running!"


@app.route("/profile", methods=["GET"])
def profile():
    user_id = request.args.get("user_id", "zil@example.com")
    profile_data = get_user_profile(user_id)
    if profile_data:
        return jsonify(profile_data), 200
    else:
        return jsonify({"error": "Profile not found"}), 404

@app.route("/reset-profile", methods=["POST"])
def reset_profile():
    user_id = request.args.get("user_id", "zil@example.com")
    default_profile = {
        "job_titles": [],
        "locations": [],
        "required_skills": [],
        "industries": [],
        "employment_type": "",
        "experience_level": "",
        "certifications": [],
        "must_have_keywords": [],
        "excluded_keywords": [],
        "education": [],
        "preferred_company_types": [],
        "language_preferences": [],
        "remote_flexibility": "flexible",
        "minimum_salary_expectation": "",
        "resume_version_notes": "",
        "summary_profile": "",
        "experience_paragraphs": [],
        "project_paragraphs": [],
        "strengths_paragraphs": [],
        "custom_profile_notes": "",
        "user_id": user_id,
        "pending_questions": []
    }
    upsert_user_profile(user_id, default_profile)
    return jsonify({"message": "Profile reset successfully"}), 200

@app.route("/create-user", methods=["POST"])
def create_user():
    try:
        data = request.get_json(force=True)
        user_id = data["user_id"]
        name = data.get("name", "")

        # Default profile structure
        default_profile = {
            "user_id": user_id,
            "name": name,
            "headline": "",
            "summary": "",
            "current_title": "",
            "current_company": "",
            "location": "",
            "skills": [],
            "tools": [],
            "strengths": [],
            "industries": [],
            "experience_paragraphs": [],
            "project_paragraphs": [],
            "custom_profile_notes": [],
            "pending_questions": []
        }

        upsert_user_profile(user_id, default_profile)
        return jsonify({"message": "User created"}), 201

    except Exception as e:
        print(f"[ERROR] /create-user failed: {e}")
        return jsonify({"error": "Failed to create user"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
