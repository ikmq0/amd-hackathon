"""GET /analytics/* — chart data (breakdown, monthly spend, accuracy trend)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.repositories import transaction_repo
from app.schemas import BreakdownSlice, MonthPoint

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/breakdown", response_model=list[BreakdownSlice])
async def breakdown(
    month: str | None = None, session: AsyncSession = Depends(get_session)
) -> list[BreakdownSlice]:
    """Spend-by-category slices; pass ?month=YYYY-MM to scope to a single month."""
    return await transaction_repo.breakdown(session, month)


@router.get("/monthly", response_model=list[MonthPoint])
async def monthly(session: AsyncSession = Depends(get_session)) -> list[MonthPoint]:
    return await transaction_repo.monthly(session)


@router.get("/accuracy", response_model=list[MonthPoint])
async def accuracy(session: AsyncSession = Depends(get_session)) -> list[MonthPoint]:
    return await transaction_repo.accuracy_trend(session)
