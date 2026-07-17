"""CLASSIFY stage — category comes deterministically from the matched merchant.

No inference, no guessing: a resolved merchant carries its curated category.
"""

from __future__ import annotations

from app.schemas import Category, Merchant


def classify(merchant: Merchant) -> Category:
    return merchant.category
