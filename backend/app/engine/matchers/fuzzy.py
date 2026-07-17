"""Tier 2 — fuzzy match (RapidFuzz). Handles typos/variants the exact tier misses.

Confidence = best score / 100. Accepts only above the configured threshold; below
that, returns None so the pipeline falls through to unknown (never a low-quality guess).
"""

from __future__ import annotations

from rapidfuzz import fuzz, process

from app.core.config import settings
from app.engine.cleaner import Cleaned
from app.engine.matchers.base import MatchResult
from app.repositories.merchant_repo import MerchantRepo
from app.schemas import ResolvedBy


class FuzzyMatcher:
    def __init__(self, threshold: int | None = None):
        self.threshold = threshold if threshold is not None else settings.fuzzy_threshold

    def match(self, cleaned: Cleaned, repo: MerchantRepo) -> MatchResult | None:
        candidates = cleaned.tokens or ([cleaned.concat] if cleaned.concat else [])
        if not candidates:
            return None

        keys = [k for k, _ in repo.fuzzy_keys]
        best_score = 0.0
        best_mid: str | None = None
        for cand in candidates:
            hit = process.extractOne(cand, keys, scorer=fuzz.WRatio, score_cutoff=self.threshold)
            if hit and hit[1] > best_score:
                best_score = hit[1]
                best_mid = repo.fuzzy_keys[hit[2]][1]

        if best_mid is None:
            return None
        return MatchResult(best_mid, ResolvedBy.FUZZY, round(best_score / 100, 4))
