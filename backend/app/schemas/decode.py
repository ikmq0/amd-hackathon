"""The decode contract — request/response models for the decoding engine.

`DecodeResult` is the single source of truth for the output shape; both the API
and the frontend depend on it. Pydantic validates the SHAPE; the closed merchant
set (enforced in the engine) validates the TRUTH — together they make the
"no hallucination" guarantee structural.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app import SCHEMA_VERSION

from .category import Category, label_ar


class ResolvedBy(str, Enum):
    EXACT = "exact"
    ALIAS = "alias"
    FUZZY = "fuzzy"
    VECTOR = "vector"
    UNKNOWN = "unknown"


class DecodeRequest(BaseModel):
    raw: str = Field(..., description="Raw obfuscated descriptor", examples=["MCD_2938_RYD*SP"])


class DecodeItem(BaseModel):
    """One line of a statement: descriptor plus optional financial context."""

    raw: str
    amount: float | None = None
    date: str | None = None


class BatchDecodeRequest(BaseModel):
    items: list[DecodeItem]


class DecodeResult(BaseModel):
    raw: str
    normalized: str
    merchant: str | None = None
    merchant_id: str | None = None
    category: Category = Category.OTHER
    category_label_ar: str = label_ar(Category.OTHER)
    city: str | None = None
    channel: str | None = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    resolved_by: ResolvedBy = ResolvedBy.UNKNOWN
    resolved: bool = False
    logo: str | None = None
    brand_color: str | None = None
    schema_version: str = SCHEMA_VERSION

    @property
    def accuracy_pct(self) -> int:
        return round(self.confidence * 100)
