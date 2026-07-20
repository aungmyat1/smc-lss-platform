"""Research metrics and segmentation helpers."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from statistics import mean
from typing import Any, Iterable

from validation.performance_metrics import compute_metrics


def flatten_trade_rs(results: Iterable[Any]) -> list[float]:
    trade_rs: list[float] = []
    for result in results:
        for trade in getattr(result, "trades", []):
            trade_rs.append(float(trade.net_r))
    return trade_rs


def combined_metrics(results: Iterable[Any]) -> dict[str, Any]:
    return compute_metrics(flatten_trade_rs(results))


def symbol_metrics(results: Iterable[Any]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        for trade in getattr(result, "trades", []):
            grouped[str(getattr(result, "symbol", "UNKNOWN"))].append(float(trade.net_r))
    return {symbol: compute_metrics(values) for symbol, values in grouped.items()}


def session_metrics(results: Iterable[Any]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        for trade in getattr(result, "trades", []):
            session = trade.management_events[0]["event"] if getattr(trade, "management_events", None) else "ALL"
            grouped[str(session)].append(float(trade.net_r))
    return {name: compute_metrics(values) for name, values in grouped.items()}

