"""GET /transactions — decoded statement history (filterable)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dates import month_ar
from app.core.db import get_session
from app.repositories import transaction_repo
from app.schemas import TransactionOut

router = APIRouter(tags=["transactions"])


class MonthOption(BaseModel):
    key: str       # 'YYYY-MM'
    label: str     # Arabic month + year


class TransactionFilters(BaseModel):
    months: list[MonthOption]
    cities: list[str]


@router.get("/transactions", response_model=list[TransactionOut])
async def get_transactions(
    category: str | None = Query(default=None, description="Arabic category label filter"),
    search: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=1000),
    month: str | None = Query(default=None, description="'YYYY-MM' filter"),
    city: str | None = Query(default=None, description="Arabic city filter"),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionOut]:
    return await transaction_repo.list_transactions(session, category, search, limit, month, city)


@router.get("/transactions/filters", response_model=TransactionFilters)
async def get_transaction_filters(
    session: AsyncSession = Depends(get_session),
) -> TransactionFilters:
    months = await transaction_repo.available_months(session)
    cities = await transaction_repo.available_cities(session)

    def label(m: str) -> str:
        try:
            y, mm = m.split("-")
            return f"{month_ar(int(mm))} {y}"
        except (ValueError, KeyError):
            return m

    return TransactionFilters(
        months=[MonthOption(key=m, label=label(m)) for m in reversed(months)],
        cities=cities,
    )
