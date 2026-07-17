"""GET /stats — real telemetry backing the dashboard KPIs (no hardcoded numbers).

The headline accuracy comes from the eval harness (reports/eval_summary.json) when
present — the defensible, held-out number — otherwise it falls back to live coverage.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_decoder
from app.core.config import BACKEND_DIR
from app.core.db import get_session
from app.engine.pipeline import DecodingEngine
from app.repositories import transaction_repo
from app.schemas import Stats

_EVAL_SUMMARY = BACKEND_DIR / "reports" / "eval_summary.json"

router = APIRouter(tags=["stats"])


def _load_eval() -> dict | None:
    if _EVAL_SUMMARY.exists():
        try:
            return json.loads(_EVAL_SUMMARY.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return None
    return None


@router.get("/stats", response_model=Stats)
async def get_stats(
    session: AsyncSession = Depends(get_session),
    decoder: DecodingEngine = Depends(get_decoder),
) -> Stats:
    total_spend, tx_count, resolved = await transaction_repo.totals(session)
    coverage = round(resolved / tx_count * 100) if tx_count else 0

    ev = _load_eval()
    accuracy = int(ev["merchant_accuracy_pct"]) if ev else coverage
    avg_latency = float(ev["latency_p50_ms"]) if ev else decoder.avg_latency_ms

    return Stats(
        total_spend=round(total_spend, 2),
        tx_count=tx_count,
        accuracy_pct=accuracy,
        avg_latency_ms=avg_latency,
        coverage_pct=coverage,
        cache_hit_rate=decoder.cache.hit_rate,
        resolved_by=dict(decoder.resolved_by_counts),
    )
