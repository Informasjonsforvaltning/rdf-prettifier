"""Auth."""

import os

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.getenv("API_KEY", "test-key")
API_KEY_NAME = "X-API-KEY"

api_key_header_value = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=True))


async def get_api_key(
    api_key: str = api_key_header_value,
) -> str:
    """Validate API key."""
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
