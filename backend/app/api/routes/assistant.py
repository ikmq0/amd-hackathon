"""POST /report and POST /chat — Layer 3 (LLM) endpoints.

Both ground the model on aggregates the deterministic pipeline already produced;
neither ever passes a raw descriptor to the LLM.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dates import month_ar
from app.core.db import get_session
from app.repositories import transaction_repo
from app.schemas import ChatRequest, ChatResult, ReportRequest, ReportResult
from app.services import llm

router = APIRouter(tags=["assistant"])


def _month_label(month: str) -> str:
    """'2026-07' -> 'يوليو 2026'."""
    try:
        year, mm = month.split("-")
        return f"{month_ar(int(mm))} {year}"
    except (ValueError, KeyError):
        return month


@router.post("/report", response_model=ReportResult)
async def report_endpoint(
    req: ReportRequest, session: AsyncSession = Depends(get_session)
) -> ReportResult:
    months = await transaction_repo.available_months(session)
    if not months:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "لا توجد عمليات لإنشاء تقرير.")
    month = req.month or months[-1]
    if month not in months:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"لا توجد عمليات في الشهر {month}.")

    aggregate = await transaction_repo.category_aggregate(session, month)
    try:
        markdown = llm.generate_report(aggregate, _month_label(month))
    except llm.LLMUnavailable as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    return ReportResult(month=month, month_label=_month_label(month), report_markdown=markdown)


@router.post("/chat", response_model=ChatResult)
async def chat_endpoint(
    req: ChatRequest, session: AsyncSession = Depends(get_session)
) -> ChatResult:
    aggregate = await transaction_repo.category_aggregate(session, month=None)
    try:
        answer = llm.answer_chat(aggregate, req.message)
    except llm.LLMUnavailable as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    return ChatResult(answer=answer)
