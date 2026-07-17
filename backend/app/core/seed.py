"""Seed SQLite from the synthetic statement (data/mock_transactions.json).

Decodes each raw descriptor through the engine and stores the enriched row, so
/transactions and /analytics are driven by real engine output. Reseeds on startup
for reproducible demos (150 rows -> instant).
"""

from __future__ import annotations

import json

from app.core.config import DATA_DIR
from app.core.db import Base, SessionLocal, engine
from app.engine.pipeline import DecodingEngine
from app.models import Transaction
from app.repositories import corrections

_MOCK = DATA_DIR / "mock_transactions.json"


async def seed_database(decoder: DecodingEngine) -> int:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    rows = json.loads(_MOCK.read_text(encoding="utf-8"))
    async with SessionLocal() as session:
        for row in rows:
            r = decoder.decode(row["raw"])
            txn = Transaction(
                raw=r.raw,
                merchant=r.merchant,
                merchant_id=r.merchant_id,
                category=r.category.value,
                category_label_ar=r.category_label_ar,
                city=r.city or "—",
                channel=r.channel,
                amount=float(row["amount"]),
                date=row["date"],
                confidence=r.confidence,
                resolved_by=r.resolved_by.value,
                resolved=r.resolved,
            )
            # A stored user correction always wins — it survives reseeds (the engine
            # "remembers" once a descriptor has been corrected).
            if (fix := corrections.lookup(row["raw"])) is not None:
                txn.merchant = fix["display_name"]
                txn.category = fix["category"]
                txn.category_label_ar = fix["category_label_ar"]
                txn.confidence = 1.0
                txn.resolved_by = "correction"
                txn.resolved = True
            session.add(txn)
        await session.commit()
    return len(rows)
