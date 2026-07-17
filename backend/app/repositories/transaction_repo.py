"""Read queries + aggregations over the seeded transactions (SQLite).

Amounts are signed: negative = outflow (spend), positive = inflow (income). "Spend"
aggregations therefore sum the magnitude of negative rows; income is reported
separately and never counted as spend.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dates import format_date_ar, month_ar
from app.engine.cleaner import key_norm
from app.models import Transaction
from app.schemas import (
    BreakdownSlice,
    Category,
    MerchantStats,
    MonthPoint,
    TransactionOut,
    color,
    label_ar,
)

_MONTH = func.substr(Transaction.date, 1, 7)
_OUTFLOW = Transaction.amount < 0  # spend


async def list_transactions(
    session: AsyncSession,
    category: str | None = None,
    search: str | None = None,
    limit: int | None = None,
    month: str | None = None,
    city: str | None = None,
) -> list[TransactionOut]:
    stmt = select(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc())
    if category:
        stmt = stmt.where(Transaction.category_label_ar == category)
    if month:
        stmt = stmt.where(_MONTH == month)
    if city:
        stmt = stmt.where(Transaction.city == city)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            Transaction.merchant.ilike(like)
            | Transaction.raw.ilike(like)
            | Transaction.display_name.ilike(like)
        )
    if limit:
        stmt = stmt.limit(limit)
    rows = (await session.scalars(stmt)).all()
    return [
        TransactionOut(
            name=t.display_name or t.merchant or t.raw,
            raw=t.raw,
            cat=t.category_label_ar,
            city=t.city,
            date=format_date_ar(t.date),
            amt=t.amount,
            acc=round(t.confidence * 100),
            resolved=t.resolved,
            type=t.txn_type,
            income=t.is_income,
        )
        for t in rows
    ]


async def totals(session: AsyncSession) -> tuple[float, int, int]:
    """(total_spend, tx_count, resolved_count) — total_spend is outflow magnitude."""
    spend = (
        await session.scalar(
            select(func.coalesce(func.sum(-Transaction.amount), 0.0)).where(_OUTFLOW)
        )
    ) or 0.0
    tx_count = (await session.scalar(select(func.count(Transaction.id)))) or 0
    resolved = (
        await session.scalar(
            select(func.count(Transaction.id)).where(Transaction.resolved.is_(True))
        )
    ) or 0
    return float(spend), int(tx_count), int(resolved)


async def income_total(session: AsyncSession) -> float:
    val = (
        await session.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(Transaction.amount > 0)
        )
    ) or 0.0
    return float(val)


async def merchant_stats(session: AsyncSession) -> list[MerchantStats]:
    stmt = (
        select(
            Transaction.merchant,
            Transaction.category_label_ar,
            func.count(Transaction.id),
            func.sum(-Transaction.amount),
            func.avg(Transaction.confidence),
        )
        .where(Transaction.resolved.is_(True), Transaction.txn_type == "purchase", _OUTFLOW)
        .group_by(Transaction.merchant, Transaction.category_label_ar)
        .order_by(func.sum(-Transaction.amount).desc())
    )
    rows = (await session.execute(stmt)).all()
    return [
        MerchantStats(
            name=name,
            cat=cat,
            count=int(count),
            total=round(float(total), 2),
            acc=round(float(avg_conf) * 100),
        )
        for name, cat, count, total, avg_conf in rows
        if name
    ]


async def breakdown(session: AsyncSession, month: str | None = None) -> list[BreakdownSlice]:
    """Spend by category (outflows only; income is not spend)."""
    stmt = (
        select(Transaction.category, func.sum(-Transaction.amount))
        .where(_OUTFLOW)
        .group_by(Transaction.category)
        .order_by(func.sum(-Transaction.amount).desc())
    )
    if month:
        stmt = stmt.where(_MONTH == month)
    rows = (await session.execute(stmt)).all()
    return [
        BreakdownSlice(name=label_ar(Category(cat)), val=round(float(total), 2), color=color(Category(cat)))
        for cat, total in rows
    ]


async def monthly(session: AsyncSession, months: int = 12) -> list[MonthPoint]:
    stmt = select(_MONTH, func.sum(-Transaction.amount)).where(_OUTFLOW).group_by(_MONTH).order_by(_MONTH)
    rows = (await session.execute(stmt)).all()
    points = [
        MonthPoint(m=month_ar(int(key.split("-")[1])), v=round(float(total), 2), key=key)
        for key, total in rows
    ]
    return points[-months:]


async def accuracy_trend(session: AsyncSession, months: int = 12) -> list[MonthPoint]:
    stmt = select(_MONTH, func.avg(Transaction.confidence)).group_by(_MONTH).order_by(_MONTH)
    rows = (await session.execute(stmt)).all()
    points = [
        MonthPoint(m=month_ar(int(key.split("-")[1])), v=round(float(avg) * 100)) for key, avg in rows
    ]
    return points[-months:]


async def apply_correction(
    session: AsyncSession,
    raw: str,
    *,
    category: str,
    category_label_ar: str,
    display_name: str,
) -> int:
    """Re-label every stored transaction that shares this descriptor's merchant key.

    Matches on the canonical normalized key (not the exact string) so that all
    obfuscated variants of the same merchant get corrected together. Returns the
    number of rows updated.
    """
    target = key_norm(raw)
    rows = (await session.scalars(select(Transaction))).all()
    updated = 0
    for t in rows:
        if key_norm(t.raw) != target:
            continue
        t.merchant = display_name
        t.display_name = display_name
        t.category = category
        t.category_label_ar = category_label_ar
        t.confidence = 1.0
        t.resolved_by = "correction"
        t.resolved = True
        updated += 1
    await session.commit()
    return updated


async def available_months(session: AsyncSession) -> list[str]:
    """Distinct 'YYYY-MM' months present in the statement, newest last."""
    stmt = select(_MONTH).group_by(_MONTH).order_by(_MONTH)
    return list((await session.scalars(stmt)).all())


async def available_cities(session: AsyncSession) -> list[str]:
    """Distinct cities present, most-frequent first (blanks/'—' last)."""
    stmt = (
        select(Transaction.city, func.count(Transaction.id))
        .group_by(Transaction.city)
        .order_by(func.count(Transaction.id).desc())
    )
    rows = (await session.execute(stmt)).all()
    return [city for city, _ in rows if city and city != "—"]


async def chat_context(session: AsyncSession) -> dict[str, object]:
    """Rich, already-aggregated grounding for the LLM chat — enough to answer
    month-vs-month comparisons, per-category questions, top-merchant questions and
    grounded saving advice. Still never exposes a raw descriptor."""
    spend, _, _ = await totals(session)
    income = await income_total(session)
    by_category = await category_aggregate(session)
    by_month = [{"month": p.m, "key": p.key, "total": p.v} for p in await monthly(session, months=24)]
    merchants = await merchant_stats(session)
    top_merchants = [
        {"name": m.name, "count": m.count, "total": m.total} for m in merchants[:8]
    ]

    # spend per month per category (for "compare May vs June by category")
    stmt = (
        select(_MONTH, Transaction.category_label_ar, func.sum(-Transaction.amount))
        .where(_OUTFLOW)
        .group_by(_MONTH, Transaction.category_label_ar)
        .order_by(_MONTH)
    )
    rows = (await session.execute(stmt)).all()
    labels = {p["key"]: p["month"] for p in by_month}
    per_month: dict[str, list[dict[str, object]]] = {}
    for key, cat, total in rows:
        per_month.setdefault(labels.get(key, key), []).append(
            {"category": cat, "total": round(float(total or 0.0), 2)}
        )

    return {
        "total_spend": round(spend, 2),
        "total_income": round(income, 2),
        "by_category": by_category,
        "by_month": [{"month": m["month"], "total": m["total"]} for m in by_month],
        "by_month_category": per_month,
        "top_merchants": top_merchants,
    }


async def category_aggregate(session: AsyncSession, month: str | None = None) -> list[dict[str, object]]:
    """Spend by Arabic category label (outflows only), optionally scoped to one month.

    This is the ONLY thing Layer 3 (the LLM) ever sees — clean, already-categorized
    totals, never a raw descriptor. Ordered by total descending.
    """
    stmt = (
        select(Transaction.category_label_ar, func.count(Transaction.id), func.sum(-Transaction.amount))
        .where(_OUTFLOW)
        .group_by(Transaction.category_label_ar)
    )
    if month:
        stmt = stmt.where(_MONTH == month)
    stmt = stmt.order_by(func.sum(-Transaction.amount).desc())
    rows = (await session.execute(stmt)).all()
    return [
        {"category": cat, "count": int(count), "total": round(float(total or 0.0), 2)}
        for cat, count, total in rows
    ]
