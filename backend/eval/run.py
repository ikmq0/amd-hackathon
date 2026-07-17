"""Evaluation harness — turns "94% / <120ms / 2000 tx/s" into measured numbers.

Runs the engine over the HELD-OUT eval set (heavier/unseen surface forms + deliberate
unknowns) and reports:
  - merchant-ID accuracy (headline)   - category accuracy
  - coverage (% resolved)             - resolved_by tier distribution
  - category confusion matrix
  - latency p50/p95/p99 (single-request, deterministic path)
  - throughput (tx/s, warm cache + dedupe)

Writes reports/eval_summary.json (consumed by GET /stats) and prints a report.

Run:  uv run python -m eval.run
"""

from __future__ import annotations

import json
import time

from app.core.config import BACKEND_DIR, DATA_DIR
from app.engine.pipeline import DecodingEngine
from app.repositories.merchant_repo import build_repo
from app.schemas import Category
from eval.metrics import confusion_matrix, percentile

EVAL_SET = DATA_DIR / "eval" / "transactions.jsonl"
REPORTS = BACKEND_DIR / "reports"


def load_eval() -> list[dict]:
    rows = []
    with EVAL_SET.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run() -> dict:
    rows = load_eval()
    engine = DecodingEngine(build_repo())

    merchant_correct = 0
    category_correct = 0
    resolved_count = 0
    latencies: list[float] = []
    conf_pairs: list[tuple[str, str]] = []
    misses: list[tuple[str, str | None, str | None]] = []  # (raw, expected, got)

    for row in rows:
        exp_mid = row.get("expected_merchant_id")
        exp_cat = row.get("expected_category", Category.OTHER.value)

        t0 = time.perf_counter()
        r = engine.decode(row["raw"])
        latencies.append((time.perf_counter() - t0) * 1000)

        if r.resolved:
            resolved_count += 1

        # merchant accuracy: known -> id must match; unknown -> must NOT resolve
        if exp_mid is None:
            merchant_ok = not r.resolved
        else:
            merchant_ok = r.merchant_id == exp_mid
        merchant_correct += int(merchant_ok)
        if not merchant_ok:
            misses.append((row["raw"], exp_mid, r.merchant_id))

        # category accuracy + confusion (over the resolved/expected label space)
        if r.category.value == exp_cat:
            category_correct += 1
        conf_pairs.append((exp_cat, r.category.value))

    n = len(rows)
    # throughput: tight loop over the whole set, warm cache (batch/dedupe conditions)
    raws = [row["raw"] for row in rows]
    loops = 20
    t0 = time.perf_counter()
    for _ in range(loops):
        for raw in raws:
            engine.decode(raw)
    throughput = (n * loops) / (time.perf_counter() - t0)

    labels = [c.value for c in Category]
    summary = {
        "n": n,
        "merchant_accuracy_pct": round(merchant_correct / n * 100, 1),
        "category_accuracy_pct": round(category_correct / n * 100, 1),
        "coverage_pct": round(resolved_count / n * 100, 1),
        "latency_p50_ms": round(percentile(latencies, 50), 3),
        "latency_p95_ms": round(percentile(latencies, 95), 3),
        "latency_p99_ms": round(percentile(latencies, 99), 3),
        "throughput_tx_s": round(throughput),
        "resolved_by": dict(engine.resolved_by_counts),
        "cache_hit_rate": engine.cache.hit_rate,
    }

    _print_report(summary, confusion_matrix(conf_pairs, labels), misses)
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "eval_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n-> wrote {(REPORTS / 'eval_summary.json').relative_to(BACKEND_DIR)}")
    return summary


def _print_report(summary: dict, matrix: dict, misses: list) -> None:
    print("=" * 60)
    print("مِدْ — Evaluation report (held-out set)")
    print("=" * 60)
    print(f"  samples                : {summary['n']}")
    print(f"  merchant accuracy      : {summary['merchant_accuracy_pct']}%   <- headline")
    print(f"  category accuracy      : {summary['category_accuracy_pct']}%")
    print(f"  coverage (resolved)    : {summary['coverage_pct']}%")
    print(f"  resolved_by            : {summary['resolved_by']}")
    lat = f"{summary['latency_p50_ms']} / {summary['latency_p95_ms']} / {summary['latency_p99_ms']}"
    print(f"  latency p50/p95/p99 ms : {lat}")
    tps = f"{summary['throughput_tx_s']:,}"
    print(f"  throughput             : {tps} tx/s (warm cache)")
    print(f"  cache hit rate         : {summary['cache_hit_rate']}")

    print("\n  Category confusion (expected -> predicted, non-zero off-diagonal):")
    for exp, preds in matrix.items():
        offs = {p: c for p, c in preds.items() if c and p != exp}
        if offs:
            print(f"    {exp:14s} -> {offs}")

    if misses:
        print(f"\n  Misses ({len(misses)} shown up to 8):")
        for raw, exp, got in misses[:8]:
            print(f"    {raw:34s} expected={exp}  got={got}")


if __name__ == "__main__":
    run()
