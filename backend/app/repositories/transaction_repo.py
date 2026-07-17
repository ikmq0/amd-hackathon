"""Read queries + aggregations over the seeded transactions (SQLite)."""

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


async def list_transactions(
    session: AsyncSession,
    category: str | None = None,
    search: str | None = None,
    limit: int | None = None,
) -> list[TransactionOut]:
    stmt = select(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc())
    if category:
        stmt = stmt.where(Transaction.category_label_ar == category)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(Transaction.merchant.ilike(like) | Transaction.raw.ilike(like))
    if limit:
        stmt = stmt.limit(limit)
    rows = (await session.scalars(stmt)).all()
    return [
        TransactionOut(
            name=t.merchant or t.raw,
            raw=t.raw,
            cat=t.category_label_ar,
            city=t.city,
            date=format_date_ar(t.date),
            amt=t.amount,
            acc=round(t.confidence * 100),
            resolved=t.resolved,
        )
        for t in rows
    ]


async def totals(session: AsyncSession) -> tuple[float, int, int]:
    sum_stmt = select(func.coalesce(func.sum(Transaction.amount), 0.0))
    total_spend = (await session.scalar(sum_stmt)) or 0.0
    tx_count = (await session.scalar(select(func.count(Transaction.id)))) or 0
    resolved = (
        await session.scalar(
            select(func.count(Transaction.id)).where(Transaction.resolved.is_(True))
        )
    ) or 0
    return float(total_spend), int(tx_count), int(resolved)


async def merchant_stats(session: AsyncSession) -> list[MerchantStats]:
    stmt = (
        select(
            Transaction.merchant,
            Transaction.category_label_ar,
            func.count(Transaction.id),
            func.sum(Transaction.amount),
            func.avg(Transaction.confidence),
        )
        .where(Transaction.resolved.is_(True))
        .group_by(Transaction.merchant, Transaction.category_label_ar)
        .order_by(func.sum(Transaction.amount).desc())
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
    ]


async def breakdown(
    session: AsyncSession, month: str | None = None
) -> list[BreakdownSlice]:
    stmt = (
        select(Transaction.category, func.sum(Transaction.amount))
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    if month:
        stmt = stmt.where(func.substr(Transaction.date, 1, 7) == month)
    rows = (await session.execute(stmt)).all()
    return [
        BreakdownSlice(
            name=label_ar(Category(cat)),
            val=round(float(total), 2),
            color=color(Category(cat)),
        )
        for cat, total in rows
    ]


async def monthly(session: AsyncSession, months: int = 6) -> list[MonthPoint]:
    ym = func.substr(Transaction.date, 1, 7)
    stmt = select(ym, func.sum(Transaction.amount)).group_by(ym).order_by(ym)
    rows = (await session.execute(stmt)).all()
    points = [
        MonthPoint(m=month_ar(int(key.split("-")[1])), v=round(float(total), 2), key=key)
        for key, total in rows
    ]
    return points[-months:]


async def accuracy_trend(session: AsyncSession, months: int = 6) -> list[MonthPoint]:
    ym = func.substr(Transaction.date, 1, 7)
    stmt = select(ym, func.avg(Transaction.confidence)).group_by(ym).order_by(ym)
    rows = (await session.execute(stmt)).all()
    points = [
        MonthPoint(m=month_ar(int(key.split("-")[1])), v=round(float(avg) * 100))
        for key, avg in rows
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
    ym = func.substr(Transaction.date, 1, 7)
    stmt = select(ym).group_by(ym).order_by(ym)
    return [row for row in (await session.scalars(stmt)).all()]


async def category_aggregate(
    session: AsyncSession, month: str | None = None
) -> list[dict[str, object]]:
    """Spend aggregated by Arabic category label, optionally scoped to one 'YYYY-MM'.

    This is the ONLY thing Layer 3 (the LLM) ever sees — clean, already-categorized
    totals, never a raw descriptor. Ordered by total ascending to mirror the engine's
    report format.
    """
    stmt = select(
        Transaction.category_label_ar,
        func.count(Transaction.id),
        func.sum(Transaction.amount),
    ).group_by(Transaction.category_label_ar)
    if month:
        stmt = stmt.where(func.substr(Transaction.date, 1, 7) == month)
    stmt = stmt.order_by(func.sum(Transaction.amount))
    rows = (await session.execute(stmt)).all()
    return [
        {"category": cat, "count": int(count), "total": round(float(total or 0.0), 2)}
        for cat, count, total in rows
    ]
