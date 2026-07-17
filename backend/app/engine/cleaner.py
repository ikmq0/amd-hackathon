"""NORMALIZE stage — turn a raw obfuscated descriptor into clean, matchable tokens.

Handles: Arabic-Indic digits, separator noise, terminal/device-id digit runs, known
noise tokens (POS/TXN/TERM/…), city-code extraction, and Arabic normalization
(tashkeel/tatweel/alef/haa). Zero-cost, deterministic, no ML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pyarabic.araby as araby

# City codes seen in Saudi descriptors -> Arabic display name.
CITY_MAP: dict[str, str] = {
    "RUH": "الرياض",
    "RYD": "الرياض",
    "JED": "جدة",
    "DMM": "الدمام",
    "MKH": "مكة",
    "MAK": "مكة",
    "ONLINE": "أونلاين",
    "ECOM": "أونلاين",
}

# Structural noise tokens that never identify a merchant.
NOISE: set[str] = {
    "POS", "TXN", "TERM", "SA", "SP", "APP", "MKTP", "PURCHASE", "DEBIT", "CREDIT",
    "CARD", "PAYMENT", "PMT", "REF", "NO", "AUTH", "VISA", "MADA", "MC", "DLVR",
    "TOPUP", "BILL", "STORE", "STORES", "HYPER", "E",
}

_AR_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_SUBTOKEN = re.compile(r"[A-Za-z]+|[؀-ۿ]+|[0-9]+")

# Arabic city names (normalized form) -> Latin city code, so enrichment reuses CITY_MAP.
AR_CITY: dict[str, str] = {
    "الرياض": "RUH",
    "جده": "JED",
    "الدمام": "DMM",
    "مكه": "MKH",
}


def normalize_arabic(s: str) -> str:
    s = araby.strip_tashkeel(s)
    s = araby.strip_tatweel(s)
    replacements = (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"),
                    ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي"))
    for a, b in replacements:
        s = s.replace(a, b)
    return s


def key_norm(s: str) -> str:
    """Canonical key form for a merchant name/alias/pattern (no separators, no digits)."""
    s = s.translate(_AR_INDIC)
    parts: list[str] = []
    for sub in _SUBTOKEN.findall(s):
        if sub.isdigit():
            continue
        parts.append(normalize_arabic(sub) if re.search(r"[؀-ۿ]", sub) else sub.upper())
    return "".join(parts)


@dataclass
class Cleaned:
    raw: str
    tokens: list[str]      # kept, normalized tokens (merchant candidates)
    concat: str            # tokens joined (no spaces) — the fuzzy/cache key basis
    city_code: str | None  # extracted city code, if any


def clean(raw: str) -> Cleaned:
    s = raw.translate(_AR_INDIC)
    tokens: list[str] = []
    city: str | None = None
    for sub in _SUBTOKEN.findall(s):
        if sub.isdigit():
            continue
        is_ar = bool(re.search(r"[؀-ۿ]", sub))
        norm = normalize_arabic(sub) if is_ar else sub.upper()
        if city is None:
            if is_ar and norm in AR_CITY:
                city = AR_CITY[norm]
                continue
            if not is_ar and norm in CITY_MAP:
                city = norm
                continue
        if not is_ar and norm in NOISE:
            continue
        tokens.append(norm)
    return Cleaned(raw=raw, tokens=tokens, concat="".join(tokens), city_code=city)
