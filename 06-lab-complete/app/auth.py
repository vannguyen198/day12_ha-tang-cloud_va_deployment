"""
API Key Authentication Module

Flow:
    Client sends request with header: X-API-Key: <key>
    verify_api_key() checks against AGENT_API_KEY env var
    Returns the key (used as user identity bucket) if valid
    Raises HTTP 401 if key is missing or wrong
"""
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    FastAPI dependency: validates the X-API-Key header.
    Returns the key string on success (used downstream as rate-limit bucket).
    Raises HTTP 401 on failure.
    """
    from app.config import settings  # lazy import avoids circular dependency

    if not api_key or api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include header: X-API-Key: <key>",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key