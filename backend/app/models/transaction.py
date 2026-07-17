"""SQLAlchemy model for a decoded transaction (the seeded statement history)."""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw: Mapped[str]
    merchant: Mapped[str | None]
    merchant_id: Mapped[str | None]
    category: Mapped[str]              # enum key
    category_label_ar: Mapped[str]
    city: Mapped[str]
    channel: Mapped[str | None]
    amount: Mapped[float]              # signed: negative = out, positive = in
    date: Mapped[str]                  # ISO yyyy-mm-dd
    confidence: Mapped[float]
    resolved_by: Mapped[str]
    resolved: Mapped[bool]
    # Rich-dataset fields (Khawarizm txn types + flow direction).
    user_id: Mapped[str] = mapped_column(default="")
    txn_type: Mapped[str] = mapped_column(default="purchase")  # purchase|transfer|income|cash
    display_name: Mapped[str] = mapped_column(default="")
    counterparty: Mapped[str | None] = mapped_column(default=None)
    is_income: Mapped[bool] = mapped_column(default=False)      # inflow (amount > 0)
