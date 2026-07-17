"""Arabic date/month helpers (display only)."""

from __future__ import annotations

MONTHS_AR: dict[int, str] = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
    7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر",
}


def month_ar(month: int) -> str:
    return MONTHS_AR[month]


def format_date_ar(iso: str) -> str:
    """'2026-07-16' -> '16 يوليو'."""
    try:
        y, m, d = iso.split("-")
        return f"{int(d):02d} {MONTHS_AR[int(m)]}"
    except (ValueError, KeyError):
        return iso
