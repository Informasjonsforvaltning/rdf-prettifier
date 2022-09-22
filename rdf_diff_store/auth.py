"""Auth."""

import os

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.getenv("API_KEY", "test-key")
API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
) -> str:
    """Validate API key."""
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
