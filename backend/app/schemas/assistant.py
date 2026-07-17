"""Request/response contracts for Layer 3 (report + chat) and user corrections."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .category import Category


class ReportRequest(BaseModel):
    month: str | None = Field(
        default=None, description="Target month 'YYYY-MM'; defaults to the latest month present"
    )


class ReportResult(BaseModel):
    month: str                 # 'YYYY-MM'
    month_label: str           # Arabic month + year, e.g. 'يوليو 2026'
    report_markdown: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResult(BaseModel):
    answer: str


class CorrectRequest(BaseModel):
    raw: str = Field(..., description="Raw descriptor of the transaction being corrected")
    category: Category
    display_name: str = Field(..., min_length=1, description="Corrected merchant / label")


class CorrectResult(BaseModel):
    updated: int               # rows re-labeled (all variants of this merchant)
    category: Category
    category_label_ar: str
    display_name: str


class CategoryOption(BaseModel):
    key: str                   # Category enum value
    label_ar: str
    color: str
