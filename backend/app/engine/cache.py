"""Cache-aside for the match resolution — the throughput lever.

Keyed by hash(normalized-concat) namespaced by directory_version. We cache the
*match* (merchant_id/tier/confidence), NOT the full result, so per-call context
(city, amount, date) stays correct while the expensive matching is reused.
Hashing also keeps the raw descriptor out of the cache (PII hygiene).
"""

from __future__ import annotations

import hashlib

from app.engine.matchers.base import MatchResult

_MISS = object()


class MatchCache:
    def __init__(self, version: str):
        self.version = version
        self._store: dict[str, MatchResult | None] = {}
        self.hits = 0
        self.misses = 0

    def _key(self, concat: str) -> str:
        digest = hashlib.sha1(concat.encode("utf-8")).hexdigest()
        return f"{self.version}:{digest}"

    def get(self, concat: str) -> tuple[bool, MatchResult | None]:
        val = self._store.get(self._key(concat), _MISS)
        if val is _MISS:
            self.misses += 1
            return False, None
        self.hits += 1
        return True, val  # type: ignore[return-value]

    def set(self, concat: str, value: MatchResult | None) -> None:
        self._store[self._key(concat)] = value

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total else 0.0
