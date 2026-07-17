"""DecodingEngine — the facade orchestrating the pipeline.

    NORMALIZE -> (cache) -> MATCH tiers (exact -> fuzzy -> [vector off]) -> CLASSIFY
    -> VALIDATE/ENRICH -> DecodeResult

Records `resolved_by` attribution and latency so /stats reports real numbers.
Batch decode dedupes automatically via the match cache (statements repeat merchants).
"""

from __future__ import annotations

import time
from collections import Counter

from app.core.config import settings
from app.engine.cache import MatchCache
from app.engine.cleaner import clean
from app.engine.matchers import ExactMatcher, FuzzyMatcher
from app.engine.matchers.base import Matcher, MatchResult
from app.engine.validator import build_result, unknown_result
from app.repositories.merchant_repo import MerchantRepo
from app.schemas import DecodeItem, DecodeResult

_LATENCY_CAP = 5000


class DecodingEngine:
    def __init__(
        self,
        repo: MerchantRepo,
        matchers: list[Matcher] | None = None,
        cache: MatchCache | None = None,
    ):
        self.repo = repo
        self.matchers: list[Matcher] = matchers or [ExactMatcher(), FuzzyMatcher()]
        self.cache = cache or MatchCache(settings.directory_version)
        self.resolved_by_counts: Counter[str] = Counter()
        self.latencies_ms: list[float] = []

    def _resolve(self, concat: str, cleaned) -> MatchResult | None:
        if concat:
            found, cached = self.cache.get(concat)
            if found:
                return cached
        result: MatchResult | None = None
        for matcher in self.matchers:
            result = matcher.match(cleaned, self.repo)
            if result is not None:
                break
        if concat:
            self.cache.set(concat, result)
        return result

    def decode(self, raw: str) -> DecodeResult:
        start = time.perf_counter()
        cleaned = clean(raw)
        match = self._resolve(cleaned.concat, cleaned)
        if match is not None and (merchant := self.repo.get(match.merchant_id)) is not None:
            result = build_result(raw, cleaned, match, merchant)
        else:
            result = unknown_result(raw, cleaned)

        self.resolved_by_counts[result.resolved_by.value] += 1
        elapsed = (time.perf_counter() - start) * 1000
        if len(self.latencies_ms) < _LATENCY_CAP:
            self.latencies_ms.append(elapsed)
        return result

    def decode_batch(self, items: list[DecodeItem]) -> list[DecodeResult]:
        # Dedup is handled by the match cache: repeated descriptors hit the cache.
        return [self.decode(it.raw) for it in items]

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return round(sum(self.latencies_ms) / len(self.latencies_ms), 3)
