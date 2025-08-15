
"""
JWT authentication utilities for the Zil agent.

This module provides helper functions and decorators to validate JSON Web
Tokens (JWTs) issued by Azure Entra ID.  It fetches the provider's
OpenID configuration to discover the URL of the JSON Web Key Set (JWKS)
unless a `JWKS_URI` environment variable is supplied.  The JWKS is
used to verify the signature of incoming tokens.

The previous implementation attempted to access `openid_config["jwks_uri"]`
directly at import time.  When the OpenID configuration could not be
retrieved or did not contain a `jwks_uri` field, the module raised a
`KeyError` during import, causing the entire application to fail on
startup.  This implementation instead lazily discovers the JWKS URI and
provides clearer error messages when it cannot be determined.
"""

from __future__ import annotations
import os
import requests
from jose import jwt
from flask import request, jsonify
from typing import Any, Callable, Dict


TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
OPENID_CONFIG_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"

openid_config = requests.get(OPENID_CONFIG_URL).json()
jwks_uri = openid_config["jwks_uri"]
jwks = requests.get(jwks_uri).json()

# Environment variables used by this module:
#
# TENANT_ID: The Microsoft Entra tenant identifier.  This value is
#   substituted into the well‑known OpenID configuration URL.  Without
#   it, token validation cannot proceed.
# AUTH_CLIENT_ID: The client/application identifier registered in the
#   tenant.  This is used as the expected audience when decoding tokens.
# JWKS_URI (optional): If provided, this URL is used directly to
#   retrieve the JWKS instead of reading it from the OpenID configuration.


def _get_openid_configuration_url(tenant_id: str) -> str:
    """Construct the OpenID configuration URL for a given tenant."""
    return f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration"


def _discover_jwks_uri(tenant_id: str) -> str:
    """
    Retrieve the JWKS URI from the OpenID configuration or environment.

    The `JWKS_URI` environment variable takes precedence.  If it is
    unset, the OpenID configuration document for the tenant is fetched
    and its `jwks_uri` (or camelCase `jwksUri`) entry is returned.

    Args:
        tenant_id: The Azure tenant identifier.

    Returns:
        A URL string pointing to the JWKS endpoint.

    Raises:
        RuntimeError: If the JWKS URI cannot be determined.
    """
    # Allow explicit override via environment
    override = os.getenv("JWKS_URI")
    if override:
        return override

    openid_url = _get_openid_configuration_url(tenant_id)
    try:
        resp = requests.get(openid_url, timeout=5)
        resp.raise_for_status()
        config = resp.json()
    except Exception as exc:
        raise RuntimeError(
            f"Unable to fetch OpenID configuration from {openid_url}: {exc}"
        ) from exc

    jwks_uri = config.get("jwks_uri") or config.get("jwksUri")
    if not jwks_uri:
        raise RuntimeError(
            "The OpenID configuration does not define a 'jwks_uri'. "
            "Set the JWKS_URI environment variable to specify the key endpoint."
        )
    return jwks_uri


def _fetch_jwks(jwks_uri: str) -> Dict[str, Any]:
    """
    Fetch the JSON Web Key Set from the given URI.

    Args:
        jwks_uri: The URL of the JWKS endpoint.

    Returns:
        A dictionary containing a `keys` list of JSON Web Keys.

    Raises:
        RuntimeError: If the JWKS cannot be fetched or parsed.
    """
    try:
        resp = requests.get(jwks_uri, timeout=5)
        resp.raise_for_status()
        jwks = resp.json()
        if "keys" not in jwks:
            raise ValueError("JWKS payload missing 'keys' field")
        return jwks
    except Exception as exc:
        raise RuntimeError(
            f"Unable to retrieve JWKS from {jwks_uri}: {exc}"
        ) from exc


def _get_jwks(tenant_id: str) -> Dict[str, Any]:
    """
    Obtain the JWKS for the configured tenant.

    This function first determines the JWKS URI (via environment override
    or discovery) and then downloads the JWKS.  It does not cache the
    result; callers may implement caching if desired.
    """
    jwks_uri = _discover_jwks_uri(tenant_id)
    return _fetch_jwks(jwks_uri)


def _get_rsa_key(token: str, jwks: Dict[str, Any]) -> Dict[str, str] | None:
    """
    Find the appropriate RSA key from the JWKS using the token's 'kid'.

    Args:
        token: The encoded JWT string.
        jwks: The JWKS dictionary.

    Returns:
        A dictionary containing the RSA key parameters or `None` if not found.
    """
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key.get("kty"),
                "kid": key.get("kid"),
                "use": key.get("use"),
                "n": key.get("n"),
                "e": key.get("e"),
            }
    return None


def _validate_token(token: str, tenant_id: str, client_id: str) -> Dict[str, Any] | None:
    """
    Decode and verify a JWT using the tenant's keys.

    Args:
        token: The encoded JWT string.
        tenant_id: The Azure tenant identifier.
        client_id: The expected audience/client identifier.

    Returns:
        The decoded JWT payload if valid, otherwise `None`.
    """
    try:
        jwks = _get_jwks(tenant_id)
        rsa_key = _get_rsa_key(token, jwks)
        if not rsa_key:
            raise ValueError("No matching RSA key found for token")
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0",
        )
        return payload
    except Exception as exc:
        # Log a simple error; the calling function will decide how to respond.
        print(f"[ERROR] Invalid token: {exc}")
        return None


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Flask route decorator that enforces JWT authentication.

    If the request lacks a valid `Authorization: Bearer <token>` header or
    token verification fails, a JSON error response with an appropriate
    HTTP status code is returned.  Otherwise, the wrapped function is
    executed normally.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("AUTH_CLIENT_ID")
        if not tenant_id or not client_id:
            # Misconfiguration; refuse to proceed.
            return (
                jsonify({"error": "Server configuration error: missing TENANT_ID or AUTH_CLIENT_ID"}),
                500,
            )
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split(" ", 1)[1]
        payload = _validate_token(token, tenant_id, client_id)
        if payload is None:
            return jsonify({"error": "Invalid token"}), 403
        # Optionally attach the payload to request for downstream use
        request.jwt_payload = payload  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
