"""Merchant directory models — the closed set the engine matches against."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .category import Category


class Merchant(BaseModel):
    """A single directory entry (loaded from data/merchants.yaml)."""

    id: str
    name_ar: str
    name_en: str
    category: Category
    aliases: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    mcc: str | None = None
    city_hints: list[str] = Field(default_factory=list)
    channel: str | None = None
    logo: str | None = None
    brand_color: str | None = None


class MerchantStats(BaseModel):
    """Aggregated per-merchant view for the dashboard's merchants page."""

    name: str
    cat: str  # Arabic category label
    count: int
    total: float
    acc: int  # average accuracy percent
