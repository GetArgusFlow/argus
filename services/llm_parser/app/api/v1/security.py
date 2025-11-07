# argus/services/llm_parser/app/api/v1/security.py

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Checks if the provided API key in the 'x-api-key' header is valid.
    """
    if api_key == settings.auth.api_key:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
