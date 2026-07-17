"""VALIDATE stage — build the Pydantic-gated result, or an explicit unknown.

Constructing a DecodeResult IS the validation (shape + category enum + confidence
bounds). Unresolved descriptors return a first-class `unknown` — never a guess.
"""

from __future__ import annotations

from app.engine.classifier import classify
from app.engine.cleaner import Cleaned
from app.engine.enrich import resolve_city
from app.engine.matchers.base import MatchResult
from app.schemas import Category, DecodeResult, Merchant, ResolvedBy, label_ar


def build_result(
    raw: str, cleaned: Cleaned, match: MatchResult, merchant: Merchant
) -> DecodeResult:
    category = classify(merchant)
    return DecodeResult(
        raw=raw,
        normalized=" ".join(cleaned.tokens),
        merchant=merchant.name_ar,
        merchant_id=merchant.id,
        category=category,
        category_label_ar=label_ar(category),
        city=resolve_city(cleaned, merchant),
        channel=merchant.channel,
        confidence=match.confidence,
        resolved_by=match.tier,
        resolved=True,
        logo=merchant.logo,
        brand_color=merchant.brand_color,
    )


def unknown_result(raw: str, cleaned: Cleaned) -> DecodeResult:
    return DecodeResult(
        raw=raw,
        normalized=" ".join(cleaned.tokens),
        merchant=None,
        merchant_id=None,
        category=Category.OTHER,
        category_label_ar=label_ar(Category.OTHER),
        city="—",
        channel=None,
        confidence=0.0,
        resolved_by=ResolvedBy.UNKNOWN,
        resolved=False,
    )
