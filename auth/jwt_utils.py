import os
import requests
from jose import jwt
from flask import request, jsonify

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
OPENID_CONFIG_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"

openid_config = requests.get(OPENID_CONFIG_URL).json()
jwks_uri = openid_config["jwks_uri"]
jwks = requests.get(jwks_uri).json()

def validate_token(token):
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]
        key = next(k for k in jwks["keys"] if k["kid"] == kid)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLIENT_ID
        )
        return payload
    except Exception as e:
        print(f"[ERROR] Invalid token: {e}")
        return None

def require_auth(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth_header.split(" ")[1]
        payload = validate_token(token)
        if not payload:
            return jsonify({"error": "Invalid token"}), 403

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
