"""User-correction store — the one thing in the engine that "learns".

Ported from the Khawarizm engine's corrections concept: once a user corrects how a
descriptor is categorized, the same descriptor always resolves via that correction
from then on — including across reseeds. The store is a small JSON file keyed by the
canonical normalized form of the raw descriptor (so ``MCD_2938_RYD`` and
``MCD 1122 JED`` share one correction: they are the same merchant).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.core.config import DATA_DIR
from app.engine.cleaner import key_norm

CORRECTIONS_PATH: Path = DATA_DIR / "corrections.json"


def correction_key(raw: str) -> str:
    """Canonical key for a raw descriptor (no separators, no digits, normalized)."""
    return key_norm(raw)


def load_corrections() -> dict[str, dict]:
    if CORRECTIONS_PATH.exists():
        try:
            return json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def lookup(raw: str) -> dict | None:
    return load_corrections().get(correction_key(raw))


def save_correction(
    raw: str, *, category: str, category_label_ar: str, display_name: str
) -> str:
    store = load_corrections()
    key = correction_key(raw)
    store[key] = {
        "category": category,
        "category_label_ar": category_label_ar,
        "display_name": display_name,
    }
    CORRECTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CORRECTIONS_PATH.write_text(
        json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return key
