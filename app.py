from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://salmon-mud-01e8de810.1.azurestaticapps.net"])
@app.route("/")
def index():
    return "Hello from Azure!"
