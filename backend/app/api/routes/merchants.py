"""GET /merchants — aggregated per-merchant stats for the directory page."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.repositories import transaction_repo
from app.schemas import MerchantStats

router = APIRouter(tags=["merchants"])


@router.get("/merchants", response_model=list[MerchantStats])
async def get_merchants(session: AsyncSession = Depends(get_session)) -> list[MerchantStats]:
    return await transaction_repo.merchant_stats(session)
