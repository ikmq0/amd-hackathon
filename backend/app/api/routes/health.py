"""Liveness endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app import SCHEMA_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "schema_version": SCHEMA_VERSION}
