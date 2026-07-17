"""FastAPI application entrypoint.

Lifespan builds the decoding engine (loads the merchant directory once) and seeds
SQLite from the synthetic statement, then attaches all routes.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import SCHEMA_VERSION
from app.api.routes import (
    analytics,
    assistant,
    corrections,
    decode,
    health,
    merchants,
    stats,
    transactions,
)
from app.core.config import settings
from app.core.seed import seed_database
from app.engine.pipeline import DecodingEngine
from app.repositories.merchant_repo import build_repo


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.decoder = DecodingEngine(build_repo())
    await seed_database(app.state.decoder)
    yield


app = FastAPI(
    title=settings.app_name,
    version=SCHEMA_VERSION,
    description="محرك فك تشفير العمليات البنكية — Open Banking transaction decoding engine.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (
    health,
    decode,
    transactions,
    merchants,
    analytics,
    stats,
    assistant,
    corrections,
):
    app.include_router(module.router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs", "schema_version": SCHEMA_VERSION}
