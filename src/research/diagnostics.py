"""Deterministic diagnosis helpers for strategy refinement."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable


def classify_trade(trade: Any) -> str:
    if getattr(trade, "unresolved_open_position", False):
        return "end-of-data-unresolved"
    if getattr(trade, "ambiguous_bar", False):
        return "same-bar-ambiguity"
    if getattr(trade, "break_even_activated", False) and float(getattr(trade, "net_r", 0.0)) <= 0:
        return "management-fragility"
    if float(getattr(trade, "net_r", 0.0)) < 0:
        return "loss"
    return "win"


def failure_counts(results: Iterable[Any]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for result in results:
        for trade in getattr(result, "trades", []):
            counter[classify_trade(trade)] += 1
    return dict(counter)


def compare_segments(results: Iterable[Any], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        for trade in getattr(result, "trades", []):
            label = str(getattr(trade, key, "UNKNOWN"))
            grouped[label].append(float(trade.net_r))
    from validation.performance_metrics import compute_metrics

    return {label: compute_metrics(values) for label, values in grouped.items()}

