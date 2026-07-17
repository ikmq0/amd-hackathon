"""Matcher Strategy interface + result type.

Every matcher returns either a MatchResult whose merchant_id is guaranteed to exist
in the directory, or None. No matcher may ever invent a merchant — that is the
structural anti-hallucination guarantee.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.engine.cleaner import Cleaned
from app.repositories.merchant_repo import MerchantRepo
from app.schemas import ResolvedBy


@dataclass
class MatchResult:
    merchant_id: str
    tier: ResolvedBy
    confidence: float  # per-tier scale, 0..1


class Matcher(Protocol):
    def match(self, cleaned: Cleaned, repo: MerchantRepo) -> MatchResult | None: ...
