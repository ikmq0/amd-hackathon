"""Typed application settings (Pydantic Settings)."""

from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]  # .../backend
DATA_DIR = BACKEND_DIR / "data"
# Generated dataset from the AmadHackathon2026 (Khawarizm) scripts, now moved to backend/data/khawarizm.
KHAWARIZM_DATA_DIR = BACKEND_DIR / "data" / "khawarizm"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MIDD_", extra="ignore")

    app_name: str = "مِدْ (Midd) API"
    # Comma-free list via JSON in env, or defaults for local dev.
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Simple demo auth. Empty string disables the check (dev default).
    api_key: str = ""

    # Matching thresholds (see engine).
    fuzzy_threshold: int = 82          # RapidFuzz score (0-100) to accept a fuzzy match
    directory_version: str = "1.0"     # bumped when merchants.yaml changes -> cache namespace

    database_url: str = f"sqlite+aiosqlite:///{(BACKEND_DIR / 'midd.db').as_posix()}"

    # Which generated persona the dashboard is seeded from. The generated
    # transactions.csv is per-user; one user = one coherent personal statement.
    demo_user_id: str = "U0088"

    # Gemini LLM (Layer 3 — report + chat). Accepts either MIDD_GEMINI_API_KEY or a
    # plain GEMINI_API_KEY in the environment / .env. Empty = LLM features disabled.
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("MIDD_GEMINI_API_KEY", "GEMINI_API_KEY"),
    )
    # gemini-2.5-flash is no longer offered to new keys; the -latest alias tracks the
    # current free-tier flash model.
    gemini_model: str = "gemini-flash-latest"


settings = Settings()
