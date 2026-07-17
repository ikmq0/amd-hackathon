"""In-memory merchant directory + match indices (the closed set).

Loaded once from data/merchants.yaml at startup. 40 curated rows → indices are tiny
and live in memory; nothing hits a DB on the decode hot path.
"""

from __future__ import annotations

import yaml

from app.core.config import DATA_DIR
from app.engine.cleaner import key_norm
from app.schemas import Merchant

_MERCHANTS_YAML = DATA_DIR / "merchants.yaml"


class MerchantRepo:
    def __init__(self, merchants: list[Merchant]):
        self.merchants = merchants
        self.by_id: dict[str, Merchant] = {m.id: m for m in merchants}

        # exact key -> (merchant_id, tier)  where tier is "exact" (pattern/en name) or "alias"
        self.exact_keys: dict[str, tuple[str, str]] = {}
        # flat list for the fuzzy tier: (key, merchant_id)
        self.fuzzy_keys: list[tuple[str, str]] = []

        for m in merchants:
            for p in [*m.patterns, m.name_en]:
                self._add(p, m.id, "exact")
            for a in [*m.aliases, m.name_ar]:
                self._add(a, m.id, "alias")

    def _add(self, raw_key: str, merchant_id: str, tier: str) -> None:
        k = key_norm(raw_key)
        if not k:
            return
        # first writer wins for exact (patterns registered before aliases)
        self.exact_keys.setdefault(k, (merchant_id, tier))
        self.fuzzy_keys.append((k, merchant_id))

    def get(self, merchant_id: str) -> Merchant | None:
        return self.by_id.get(merchant_id)


def load_merchants() -> list[Merchant]:
    rows = yaml.safe_load(_MERCHANTS_YAML.read_text(encoding="utf-8"))
    return [Merchant(**row) for row in rows]


def build_repo() -> MerchantRepo:
    return MerchantRepo(load_merchants())
