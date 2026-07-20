"""Deterministic Monte Carlo helpers for trade sequences."""
from __future__ import annotations

import random
from typing import Any, Iterable

from validation.performance_metrics import compute_metrics


def trade_shuffle_simulation(trade_rs: Iterable[float], *, seeds: Iterable[int]) -> list[dict[str, Any]]:
    values = list(trade_rs)
    out: list[dict[str, Any]] = []
    for seed in seeds:
        rng = random.Random(seed)
        sample = values[:]
        rng.shuffle(sample)
        metrics = compute_metrics(sample)
        out.append({"seed": seed, "metrics": metrics})
    return out

