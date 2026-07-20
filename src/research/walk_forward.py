"""Chronological walk-forward helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class WalkForwardFold:
    fold: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    trades: int
    net_pf: Any
    net_expectancy_r: Any
    max_drawdown_r: Any


def rolling_folds(trade_rows: list[dict[str, Any]], train_size: int, test_size: int, step: int) -> list[WalkForwardFold]:
    folds: list[WalkForwardFold] = []
    if train_size <= 0 or test_size <= 0:
        return folds
    for fold_index, start in enumerate(range(0, max(0, len(trade_rows) - train_size - test_size + 1), max(1, step)), start=1):
        train = trade_rows[start : start + train_size]
        test = trade_rows[start + train_size : start + train_size + test_size]
        if not test:
            continue
        from validation.performance_metrics import compute_metrics

        metrics = compute_metrics([float(row["net_r"]) for row in test])
        folds.append(
            WalkForwardFold(
                fold=fold_index,
                train_start=str(train[0].get("entry_time")) if train else "",
                train_end=str(train[-1].get("entry_time")) if train else "",
                test_start=str(test[0].get("entry_time")),
                test_end=str(test[-1].get("entry_time")),
                trades=int(metrics.get("total_trades") or 0),
                net_pf=metrics.get("profit_factor"),
                net_expectancy_r=metrics.get("expectancy_r"),
                max_drawdown_r=metrics.get("maximum_drawdown_r"),
            )
        )
    return folds

