"""POST /correct and GET /categories — user corrections (the "learning" layer).

A correction re-labels every stored variant of the merchant AND is persisted so it
is re-applied on the next reseed. /categories powers the correction picker.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.repositories import corrections, transaction_repo
from app.schemas import CategoryOption, CorrectRequest, CorrectResult
from app.schemas.category import LABELS_AR, color, label_ar

router = APIRouter(tags=["corrections"])


@router.get("/categories", response_model=list[CategoryOption])
async def list_categories() -> list[CategoryOption]:
    return [
        CategoryOption(key=cat.value, label_ar=label, color=color(cat))
        for cat, label in LABELS_AR.items()
    ]


@router.post("/correct", response_model=CorrectResult)
async def correct_endpoint(
    req: CorrectRequest, session: AsyncSession = Depends(get_session)
) -> CorrectResult:
    label = label_ar(req.category)
    updated = await transaction_repo.apply_correction(
        session,
        req.raw,
        category=req.category.value,
        category_label_ar=label,
        display_name=req.display_name,
    )
    if updated == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"لا توجد عملية بالوصف: {req.raw}")

    corrections.save_correction(
        req.raw,
        category=req.category.value,
        category_label_ar=label,
        display_name=req.display_name,
    )
    return CorrectResult(
        updated=updated,
        category=req.category,
        category_label_ar=label,
        display_name=req.display_name,
    )
