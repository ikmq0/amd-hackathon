"""Pydantic contracts — the frozen interface between engine, API, and frontend."""

from .assistant import (
    CategoryOption,
    ChatRequest,
    ChatResult,
    CorrectRequest,
    CorrectResult,
    ReportRequest,
    ReportResult,
)
from .category import (
    COLORS,
    LABELS_AR,
    LABELS_EN,
    Category,
    color,
    label_ar,
    label_en,
)
from .decode import (
    BatchDecodeRequest,
    DecodeItem,
    DecodeRequest,
    DecodeResult,
    ResolvedBy,
)
from .merchant import Merchant, MerchantStats
from .views import BreakdownSlice, MonthPoint, Stats, TransactionOut

__all__ = [
    "Category",
    "COLORS",
    "LABELS_AR",
    "LABELS_EN",
    "color",
    "label_ar",
    "label_en",
    "DecodeRequest",
    "DecodeItem",
    "BatchDecodeRequest",
    "DecodeResult",
    "ResolvedBy",
    "Merchant",
    "MerchantStats",
    "TransactionOut",
    "BreakdownSlice",
    "MonthPoint",
    "Stats",
    "ReportRequest",
    "ReportResult",
    "ChatRequest",
    "ChatResult",
    "CorrectRequest",
    "CorrectResult",
    "CategoryOption",
]
