"""Tier 3 — semantic vector match. PRESENT BUT DISABLED for the MVP.

For 40 merchants, exact + fuzzy resolve the overwhelming majority; pulling in a
sentence-transformer (torch, ~2GB) would wreck cold-start and undercut the
"less compute" claim. This stub keeps the Strategy interface intact so a
numpy-cosine (or Qdrant) implementation can drop in later without touching the
pipeline — enable only if fuzzy is demonstrably insufficient on real Arabic cases.
"""

from __future__ import annotations

from app.engine.cleaner import Cleaned
from app.engine.matchers.base import MatchResult
from app.repositories.merchant_repo import MerchantRepo


class VectorMatcher:
    enabled = False

    def match(self, cleaned: Cleaned, repo: MerchantRepo) -> MatchResult | None:
        return None
