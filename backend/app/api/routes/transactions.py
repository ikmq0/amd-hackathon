"""GET /transactions — decoded statement history (filterable)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.repositories import transaction_repo
from app.schemas import TransactionOut

router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=list[TransactionOut])
async def get_transactions(
    category: str | None = Query(default=None, description="Arabic category label filter"),
    search: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionOut]:
    return await transaction_repo.list_transactions(session, category, search, limit)
