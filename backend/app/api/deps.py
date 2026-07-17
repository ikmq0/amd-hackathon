"""Shared FastAPI dependencies: the decoder singleton and demo API-key auth."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request, status

from app.core.config import settings
from app.engine.pipeline import DecodingEngine


def get_decoder(request: Request) -> DecodingEngine:
    return request.app.state.decoder


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Disabled when MIDD_API_KEY is empty (local/dev default).
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
