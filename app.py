from flask import Flask, request, jsonify
from agent import run_agent
from utils.dbutils import get_user_profile, upsert_user_profile

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
        "user_id": user_id
    }
    upsert_user_profile(user_id, default_profile)
    return jsonify({"message": "Profile reset successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
