"""FastAPI dependencies: DB session and API key auth."""

from __future__ import annotations

import logging

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings, parse_api_keys

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_key(
    x_api_key: str | None = Security(api_key_header),
    bearer: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    """Validate `X-API-Key` or `Authorization: Bearer` token."""

    settings = get_settings()
    keys = parse_api_keys(settings.admin_api_keys)
    if not keys:
        logger.error("ADMIN_API_KEYS is empty")
        raise HTTPException(status_code=503, detail="API keys not configured on server")

    token = (x_api_key or "").strip() if x_api_key else ""
    if bearer and bearer.credentials:
        token = bearer.credentials.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Missing API key")

    if token not in keys:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return token
