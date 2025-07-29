from flask import Flask, request, jsonify
from agent import handle_query

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
