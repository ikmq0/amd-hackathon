"""ENRICH stage — derive display fields (city/channel/logo/color) for a match."""

from __future__ import annotations

from app.engine.cleaner import CITY_MAP, Cleaned
from app.schemas import Category, Merchant

_NO_CITY = "—"


def resolve_city(cleaned: Cleaned, merchant: Merchant) -> str:
    if cleaned.city_code:
        return CITY_MAP.get(cleaned.city_code, _NO_CITY)
    if merchant.channel == "إنترنت":
        return "أونلاين"
    if merchant.category in (Category.TELECOM, Category.TRANSFER):
        return _NO_CITY
    return _NO_CITY
