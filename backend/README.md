# مِدْ (Midd) — Backend

Open Banking transaction **decoding engine**: turns obfuscated bank descriptors
(`MCD_2938_RYD*SP`) into clean, categorized, schema-validated JSON.

## Run
```bash
uv sync
uv run uvicorn app.main:app --reload      # http://127.0.0.1:8000  (docs at /docs)
uv run pytest
uv run python -m eval.run                 # accuracy + latency report
```

Deterministic pipeline: **normalize → exact/alias → fuzzy → classify → validate → enrich**.
Unresolved descriptors return an explicit `unknown` — never a guessed merchant.
