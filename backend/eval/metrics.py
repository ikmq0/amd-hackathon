"""Small metric helpers (no numpy dependency)."""

from __future__ import annotations


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolation percentile. q in [0,100]."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = (q / 100) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return s[lo] + (s[hi] - s[lo]) * frac


def confusion_matrix(pairs: list[tuple[str, str]], labels: list[str]) -> dict[str, dict[str, int]]:
    """pairs = (expected, predicted) -> nested counts[expected][predicted]."""
    matrix = {e: {p: 0 for p in labels} for e in labels}
    for expected, predicted in pairs:
        if expected in matrix and predicted in matrix[expected]:
            matrix[expected][predicted] += 1
    return matrix
