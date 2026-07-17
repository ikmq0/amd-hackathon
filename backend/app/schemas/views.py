"""Frontend-facing view models — shaped to match the dashboard renderers 1:1.

Field names intentionally mirror the existing `dashboard/script.js` data so the
frontend swap is a fetch(), not a rewrite: transactions use {name, raw, cat, city,
date, amt, acc}; charts use the breakdown/monthly/accuracy shapes.
"""

from __future__ import annotations

from pydantic import BaseModel


class TransactionOut(BaseModel):
    name: str          # display name (merchant / intent), raw fallback when unknown
    raw: str
    cat: str           # Arabic category label
    city: str
    date: str
    amt: float         # signed: negative = spend, positive = income
    acc: int           # confidence percent
    resolved: bool
    type: str = "purchase"   # purchase|transfer|income|cash
    income: bool = False     # inflow (amount > 0)


class BreakdownSlice(BaseModel):
    name: str          # Arabic category label
    val: float
    color: str


class MonthPoint(BaseModel):
    m: str             # month label (ar)
    v: float
    key: str = ""      # 'YYYY-MM' identifier for month filtering (blank for trend charts)


class Stats(BaseModel):
    """Real telemetry that backs the dashboard KPIs (no more hardcoded numbers)."""

    total_spend: float
    tx_count: int
    accuracy_pct: int          # merchant-resolution accuracy
    avg_latency_ms: float
    coverage_pct: int          # % of tx resolved (non-unknown)
    cache_hit_rate: float
    resolved_by: dict[str, int]  # tier -> count
