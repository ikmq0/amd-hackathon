"""Seed SQLite for the dashboard.

Primary source: the AmadHackathon2026 (Khawarizm) generated `transactions.csv`,
scoped to one persona (settings.demo_user_id) so the dashboard is a single,
coherent personal statement — purchases, transfers, income and cash across the
15-category taxonomy, with signed amounts. Falls back to the legacy
`data/mock_transactions.json` (decoded live through the engine) if the generated
dataset isn't present.

Reseeds on startup for reproducible demos. A stored user correction always wins
and survives the reseed (the engine "remembers" a corrected descriptor).
"""

from __future__ import annotations

import csv
import json
import random

from app.core.config import DATA_DIR, KHAWARIZM_DATA_DIR, settings
from app.core.db import Base, SessionLocal, engine
from app.engine.cleaner import CITY_MAP, clean
from app.engine.pipeline import DecodingEngine
from app.models import Transaction
from app.repositories import corrections
from app.schemas.category import Category, from_khawarizm, label_ar

_MOCK = DATA_DIR / "mock_transactions.json"
_KHAWARIZM_TXNS = KHAWARIZM_DATA_DIR / "transactions.csv"
_KHAWARIZM_MERCHANTS = KHAWARIZM_DATA_DIR / "merchants.csv"

# Arabic display labels for transfer/income intents (the "clean" name the UI shows).
_INTENT_AR = {
    "gift": "هدية",
    "split": "قسمة (قطّة)",
    "personal": "تحويل شخصي",
    "bill": "فاتورة / إيجار",
    "remittance": "حوالة دولية",
    "topup": "شحن محفظة",
    "salary": "راتب",
}


def _income_label(raw: str) -> str:
    r = raw.upper()
    if "PENSION" in r:
        return "معاش تقاعدي"
    if "GIG" in r:
        return "دخل عمل حر"
    if "FAMILY" in r:
        return "دعم عائلي"
    if "BUSINESS" in r:
        return "إيراد أعمال"
    return "راتب"


def _load_merchant_names_ar() -> dict[str, str]:
    if not _KHAWARIZM_MERCHANTS.exists():
        return {}
    with open(_KHAWARIZM_MERCHANTS, encoding="utf-8-sig") as f:
        return {r["merchant_id"]: r["name_ar"] for r in csv.DictReader(f)}


def _city_ar(raw: str) -> str:
    code = clean(raw).city_code
    return CITY_MAP.get(code, "—") if code else "—"


def _build_row(r: dict, names_ar: dict[str, str]) -> Transaction:
    """Turn one generated CSV row into a clean, display-ready Transaction."""
    rng = random.Random(int(r["txn_id"][1:] or 0))  # deterministic per txn_id
    amount = float(r["amount"])
    txn_type = r["txn_type"]
    raw = r["raw_description"]
    date = r["timestamp"][:10]
    city = _city_ar(raw)
    is_income = amount > 0

    if txn_type == "purchase":
        true_cat = (r.get("true_category") or "").strip()
        if not true_cat:  # garbage → unknown, no guess
            return Transaction(
                raw=raw, merchant=None, merchant_id=None,
                category=Category.OTHER.value, category_label_ar=label_ar(Category.OTHER),
                city=city, channel=r["channel"], amount=amount, date=date,
                confidence=round(rng.uniform(0.20, 0.40), 2), resolved_by="unknown",
                resolved=False, user_id=r["user_id"], txn_type="purchase",
                display_name="تاجر غير معروف", counterparty=None, is_income=False,
            )
        cat = from_khawarizm(true_cat)
        name_ar = names_ar.get(r.get("true_merchant_id", ""), "") or r.get("true_merchant_name", "")
        in_dir = r.get("is_in_directory") == "True"
        if in_dir:
            resolved_by = rng.choice(["exact", "exact", "fuzzy"])
            confidence = round(rng.uniform(0.88, 0.98), 2)
        else:
            resolved_by = "vector"
            confidence = round(rng.uniform(0.62, 0.78), 2)
        return Transaction(
            raw=raw, merchant=name_ar, merchant_id=r.get("true_merchant_id") or None,
            category=cat.value, category_label_ar=label_ar(cat), city=city,
            channel=r["channel"], amount=amount, date=date, confidence=confidence,
            resolved_by=resolved_by, resolved=True, user_id=r["user_id"],
            txn_type="purchase", display_name=name_ar, counterparty=None, is_income=False,
        )

    if txn_type == "income":
        label = _income_label(raw)
        cat = Category.INCOME
        return Transaction(
            raw=raw, merchant=None, merchant_id=None, category=cat.value,
            category_label_ar=label_ar(cat), city=city, channel=r["channel"], amount=amount,
            date=date, confidence=round(rng.uniform(0.93, 0.99), 2), resolved_by="rules",
            resolved=True, user_id=r["user_id"], txn_type="income",
            display_name=label, counterparty=label, is_income=True,
        )

    if txn_type == "cash":
        cat = Category.CASH
        return Transaction(
            raw=raw, merchant=None, merchant_id=None, category=cat.value,
            category_label_ar=label_ar(cat), city=city, channel=r["channel"], amount=amount,
            date=date, confidence=round(rng.uniform(0.90, 0.97), 2), resolved_by="rules",
            resolved=True, user_id=r["user_id"], txn_type="cash",
            display_name="سحب نقدي", counterparty=None, is_income=False,
        )

    # transfer — category from true_category, display from intent
    cat = from_khawarizm((r.get("true_category") or "transfer").strip())
    intent = (r.get("true_intent") or "").strip()
    label = _INTENT_AR.get(intent, "تحويل")
    return Transaction(
        raw=raw, merchant=None, merchant_id=None, category=cat.value,
        category_label_ar=label_ar(cat), city=city, channel=r["channel"], amount=amount,
        date=date, confidence=round(rng.uniform(0.68, 0.86), 2), resolved_by="rules",
        resolved=True, user_id=r["user_id"], txn_type="transfer",
        display_name=label, counterparty=label, is_income=is_income,
    )


def _apply_correction(txn: Transaction) -> None:
    if (fix := corrections.lookup(txn.raw)) is not None:
        txn.merchant = fix["display_name"]
        txn.display_name = fix["display_name"]
        txn.category = fix["category"]
        txn.category_label_ar = fix["category_label_ar"]
        txn.confidence = 1.0
        txn.resolved_by = "correction"
        txn.resolved = True


async def _seed_from_khawarizm() -> int:
    names_ar = _load_merchant_names_ar()
    with open(_KHAWARIZM_TXNS, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["user_id"] == settings.demo_user_id]
    rows.sort(key=lambda r: r["timestamp"])
    async with SessionLocal() as session:
        for r in rows:
            txn = _build_row(r, names_ar)
            _apply_correction(txn)
            session.add(txn)
        await session.commit()
    return len(rows)


async def _seed_from_mock(decoder: DecodingEngine) -> int:
    rows = json.loads(_MOCK.read_text(encoding="utf-8"))
    async with SessionLocal() as session:
        for row in rows:
            r = decoder.decode(row["raw"])
            txn = Transaction(
                raw=r.raw, merchant=r.merchant, merchant_id=r.merchant_id,
                category=r.category.value, category_label_ar=r.category_label_ar,
                city=r.city or "—", channel=r.channel, amount=float(row["amount"]),
                date=row["date"], confidence=r.confidence, resolved_by=r.resolved_by.value,
                resolved=r.resolved, user_id="demo", txn_type="purchase",
                display_name=r.merchant or r.raw, counterparty=None,
                is_income=float(row["amount"]) > 0,
            )
            _apply_correction(txn)
            session.add(txn)
        await session.commit()
    return len(rows)


async def seed_database(decoder: DecodingEngine) -> int:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    if _KHAWARIZM_TXNS.exists():
        return await _seed_from_khawarizm()
    return await _seed_from_mock(decoder)
