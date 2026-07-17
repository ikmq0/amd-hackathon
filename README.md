# مِدْ (Midd) — محرك فك تشفير العمليات البنكية

> Open Banking **infrastructure layer** that turns obfuscated bank transaction
> descriptors (`INMA_E_PAY_9482`, `MCD_2938_RYD*SP`) into clean, categorized,
> **schema-validated** JSON — real merchant, category, city, channel, confidence.
> The value is *data quality/standardization*, not another AI model.

**Hallucination is eliminated structurally**: every stage returns a `merchant_id`
that exists in the directory, or an explicit `unknown` — never a guess. A fixed
category **enum** + a Pydantic envelope gate the shape; the closed candidate set
gates the truth.

## Measured results (held-out eval, `uv run python -m eval.run`)
| Metric | Value |
|---|---|
| Merchant-ID accuracy | **97.0%** |
| Category accuracy | 97.8% |
| Coverage (resolved) | 90.4% |
| Latency p50 / p95 / p99 | **0.03 / 0.6 / 1.4 ms** |
| Throughput (warm cache) | **~78,000 tx/s** |

> Numbers are measured on synthetic, **held-out** data (different surface forms than
> training) — reported honestly, not asserted. Latency (single request) and throughput
> (warm cache + in-batch dedupe) are reported separately.

## Architecture
```
raw descriptor
  → NORMALIZE   regex + PyArabic (device/terminal IDs, Arabic-Indic digits, city codes)
  → MATCH       exact/alias (O(1)) → fuzzy (RapidFuzz)   [vector tier present, off]
  → CLASSIFY    category from matched merchant (deterministic)
  → VALIDATE    Pydantic gate + explicit "unknown" (Null Object)
  → ENRICH      city/channel/logo/color  →  DecodeResult (JSON)
  ↳ cache-aside on hash(normalized), namespaced by directory_version
```

## Stack (2026)
- **Backend:** Python 3.11+ · FastAPI · Pydantic v2 · SQLAlchemy 2 (SQLite) · RapidFuzz · PyArabic · **uv**
- **Frontend:** Next.js 16 (App Router) · React 19 · Tailwind v4 · IBM Plex Sans Arabic (RTL)
- **Data:** 40-brand Saudi merchant directory (`backend/data/merchants.yaml`, in git) +
  150 synthetic transactions + a held-out eval split (`data/generate.py`)

## Run it

**Backend** (http://127.0.0.1:8000 · docs at `/docs`):
```bash
cd backend
uv sync
uv run python -m data.generate      # (re)build synthetic data  [optional]
uv run python -m eval.run           # accuracy + latency report → reports/eval_summary.json
uv run uvicorn app.main:app --reload
uv run pytest                        # 21 tests
```

**Frontend** (http://localhost:3000):
```bash
cd frontend
npm install
npm run dev
```
Set `NEXT_PUBLIC_API_BASE` if the API is not on `127.0.0.1:8000`.

## Layout
```
backend/   FastAPI app (app/engine = the pipeline), data/, eval/, tests/
frontend/  Next.js 16 dashboard (5 pages) — live decode box, KPIs from /stats
```

## API
`POST /decode` · `POST /decode/batch` · `GET /transactions` · `GET /merchants`
· `GET /analytics/{breakdown,monthly,accuracy}` · `GET /stats` · `GET /health`

## Deferred (post-hackathon)
Claude Haiku 4.5 **closed-set** LLM tail (structured-output `merchant_id` enum) ·
unknown-queue → new-alias active-learning loop · Qdrant + embeddings at scale ·
real auth/rate-limiting · Postgres · 500-brand directory.
