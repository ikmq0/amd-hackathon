"""Templated synthetic data generator.

Produces two self-labeled datasets from the merchant directory:

  data/mock_transactions.json   150 seed transactions (raw + amount + date + ground truth)
                                -> seeds SQLite / powers the dashboard
  data/eval/transactions.jsonl  held-out eval set with HEAVIER, unseen surface forms
                                (extra noise, alt separators, lowercase, Arabic-Indic digits,
                                mild typos, transliteration) + deliberate unknowns

Anti-leakage: the eval set uses different templates/noise than the seed set, so the eval
measures the normalizer + fuzzy matcher — not memorization of exact strings.

Run:  uv run python -m data.generate
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent
MERCHANTS = DATA_DIR / "merchants.yaml"
SEED_OUT = DATA_DIR / "mock_transactions.json"
EVAL_OUT = DATA_DIR / "eval" / "transactions.jsonl"

RNG = random.Random(42)
BASE_DATE = date(2026, 7, 15)  # fixed reference for reproducibility

CITY_CODES = ["RUH", "JED", "DMM", "MKH", "ONLINE"]

AMOUNT_RANGES = {
    "GROCERY": (35, 620),
    "RESTAURANT": (14, 185),
    "FOOD_DELIVERY": (28, 165),
    "SHOPPING": (45, 950),
    "TELECOM": (50, 320),
    "TRANSFER": (100, 3200),
    "OTHER": (20, 400),
}

# Weight recent months heavier so the monthly trend rises toward July (matches the pitch).
MONTH_WEIGHTS = [(150, 1), (120, 1), (90, 2), (60, 3), (30, 4), (5, 6)]  # (days_ago_center, weight)

_A2I = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def d(n: int) -> str:
    return "".join(RNG.choice("0123456789") for _ in range(n))


def rand_alpha(n: int) -> str:
    return "".join(RNG.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(n))


def pick_city(m: dict) -> str:
    hints = m.get("city_hints") or []
    return RNG.choice(hints) if hints else RNG.choice(CITY_CODES)


def pick_amount(cat: str) -> float:
    lo, hi = AMOUNT_RANGES.get(cat, AMOUNT_RANGES["OTHER"])
    return round(RNG.uniform(lo, hi), 2)


def pick_date() -> str:
    centers, weights = zip(*MONTH_WEIGHTS, strict=True)
    center = RNG.choices(centers, weights=weights, k=1)[0]
    days_ago = max(0, int(RNG.gauss(center, 12)))
    return (BASE_DATE - timedelta(days=days_ago)).isoformat()


def mild_typo(s: str) -> str:
    """Drop or duplicate one char to exercise the fuzzy tier (kept mild)."""
    if len(s) < 5:
        return s
    i = RNG.randrange(1, len(s) - 1)
    return s[:i] + s[i + 1 :] if RNG.random() < 0.5 else s[:i] + s[i] + s[i:]


# --- template banks (seed = moderate noise; eval = heavier / unseen forms) ---
def seed_descriptor(pat: str, city: str) -> str:
    t = RNG.choice(
        [
            f"{pat}_{d(4)}_{city}",
            f"{pat}*{city}_{d(3)}",
            f"{pat}_{city}_{d(4)}",
            f"{pat} {d(4)} {city}",
            f"{pat}_POS_{d(5)}",
            f"{pat}_{city}_TXN{d(4)}",
        ]
    )
    return t


def eval_descriptor(pat: str, city: str) -> str:
    sep = RNG.choice(["_", "-", "*", " "])
    base = mild_typo(pat) if RNG.random() < 0.25 else pat
    t = RNG.choice(
        [
            f"SA*{base}_{d(6)}",
            f"{base}-{city}-{d(4)}-{rand_alpha(3)}",
            f"{base}{sep}{d(4)}{sep}TERM{d(3)}",
            f"{base.lower()}_{city}_{d(4)}",
            f"{base}_{d(4).translate(_A2I)}_{city}",
            f"POS{d(3)} {base} {city}",
            f"{base}{sep}{rand_alpha(2)}{d(3)}{sep}{city}",
        ]
    )
    return t


def build() -> None:
    merchants = yaml.safe_load(MERCHANTS.read_text(encoding="utf-8"))

    # ---- seed set: ~150 rows, spread across merchants ----
    seed: list[dict] = []
    per = 4  # base rows per merchant -> 40*4 = 160, trimmed to 150
    for m in merchants:
        for _ in range(per):
            pat = RNG.choice(m["patterns"])
            city = pick_city(m)
            # ~28% of a real statement is messy → exercises the fuzzy tier / honest accuracy
            noisy = RNG.random() < 0.28
            raw = eval_descriptor(pat, city) if noisy else seed_descriptor(pat, city)
            seed.append(
                {
                    "raw": raw,
                    "amount": pick_amount(m["category"]),
                    "date": pick_date(),
                    "expected_merchant_id": m["id"],
                    "expected_category": m["category"],
                }
            )
    RNG.shuffle(seed)
    seed = seed[:150]
    SEED_OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- eval set: held-out, heavier noise + deliberate unknowns ----
    ev: list[dict] = []
    for m in merchants:
        for _ in range(3):  # 40*3 = 120
            pat = RNG.choice(m["patterns"])
            city = pick_city(m)
            ev.append(
                {
                    "raw": eval_descriptor(pat, city),
                    "expected_merchant_id": m["id"],
                    "expected_category": m["category"],
                }
            )
    # 15 unknowns: garbage tokens that match no pattern -> must resolve to unknown
    for _ in range(15):
        ev.append(
            {
                "raw": f"{rand_alpha(4)}_{d(4)}_{rand_alpha(3)}{d(2)}",
                "expected_merchant_id": None,
                "expected_category": "OTHER",
            }
        )
    RNG.shuffle(ev)
    EVAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    with EVAL_OUT.open("w", encoding="utf-8") as f:
        for row in ev:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"seed:  {len(seed):>3} rows -> {SEED_OUT.relative_to(DATA_DIR.parent)}")
    print(f"eval:  {len(ev):>3} rows -> {EVAL_OUT.relative_to(DATA_DIR.parent)}  "
          f"({sum(1 for r in ev if r['expected_merchant_id'] is None)} unknowns)")
    print("sample seed:", seed[0]["raw"], "->", seed[0]["expected_merchant_id"])
    print("sample eval:", ev[0]["raw"], "->", ev[0]["expected_merchant_id"])


if __name__ == "__main__":
    build()
