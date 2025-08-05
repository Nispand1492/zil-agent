from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://salmon-mud-01e8de810.1.azurestaticapps.net"])
@app.route("/", methods=["GET"])
def index():
    return "Zil's LangChain Agent is running!"
