"""Tier 1 — exact/alias match. O(1) dict lookup, zero cost, confidence 1.0."""

from __future__ import annotations

from app.engine.cleaner import Cleaned
from app.engine.matchers.base import MatchResult
from app.repositories.merchant_repo import MerchantRepo
from app.schemas import ResolvedBy


class ExactMatcher:
    def match(self, cleaned: Cleaned, repo: MerchantRepo) -> MatchResult | None:
        # Gather all exact candidates (token hits + concat substrings) and let the
        # LONGEST key win — specificity beats generality, so "STCPAY" beats "STC".
        candidates: list[tuple[int, str, str]] = []  # (key_len, merchant_id, tier)

        for tok in cleaned.tokens:
            hit = repo.exact_keys.get(tok)
            if hit:
                candidates.append((len(tok), hit[0], hit[1]))

        concat = cleaned.concat
        if concat:
            for key, (mid, tier) in repo.exact_keys.items():
                if len(key) >= 3 and key in concat:
                    candidates.append((len(key), mid, tier))

        if not candidates:
            return None
        _, merchant_id, tier = max(candidates, key=lambda c: c[0])
        return MatchResult(merchant_id, ResolvedBy(tier), 1.0)
