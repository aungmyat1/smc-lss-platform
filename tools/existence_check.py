#!/usr/bin/env python3
"""Generic existence-check helper for a candidate strategy.

Runs a candidate's signal-generation callable over historical candle data
and tallies how many bars produced a signal vs. each rejection code, without
running a full backtest/replay engine. This is the "cheap before expensive"
gate: answer "does this spec ever fire, and on what does it reject" before
committing to golden cases, a reference kernel, or a full replay engine for
a new candidate.

Deliberately spec-agnostic: callers supply a `signal_fn` matching the
`SignalFn` contract below rather than this module hardcoding any strategy's
own detection logic, so it is reusable across candidates instead of becoming
another one-off script (see `validation/run_st_c2_gbp_existence.py` for the
ST-C2-specific precedent this generalizes).

This module does not authorize implementation of any new strategy candidate
by itself — it is a research tool. Whether and when to run it against a
given candidate is still governed by `NEXT_ACTION.md`/`docs/RESEARCH-CHARTER.md`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


@dataclass(frozen=True)
class ExistenceOutcome:
    signal: bool
    rejection_code: str | None = None


SignalFn = Callable[[Sequence[dict], int], ExistenceOutcome]


@dataclass(frozen=True)
class ExistenceCheckResult:
    spec_id: str
    symbol: str
    timeframe: str
    bars_scanned: int
    total_windows: int
    signals: int
    rejections_by_code: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "spec_id": self.spec_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "bars_scanned": self.bars_scanned,
            "total_windows": self.total_windows,
            "signals": self.signals,
            "rejections_by_code": dict(self.rejections_by_code),
            "signal_rate": (self.signals / self.total_windows) if self.total_windows else 0.0,
        }


def run_existence_check(
    spec_id: str,
    symbol: str,
    timeframe: str,
    candles: Sequence[dict],
    signal_fn: SignalFn,
    *,
    warmup_bars: int = 0,
) -> ExistenceCheckResult:
    """Scan `candles` with `signal_fn`, tallying signals vs. rejection codes.

    `signal_fn(candles, i)` is called once per bar index `i` in
    `[warmup_bars, len(candles))` and must return an `ExistenceOutcome`. No
    trade simulation, sizing, or replay happens here — an existence check
    only answers "does the spec ever produce a signal," not "is it
    profitable" (that is `validation`/`backtesting`'s job, gated separately).
    """
    total_windows = 0
    signals = 0
    rejections: dict[str, int] = {}
    n = len(candles)
    for i in range(warmup_bars, n):
        total_windows += 1
        outcome = signal_fn(candles, i)
        if outcome.signal:
            signals += 1
        elif outcome.rejection_code:
            rejections[outcome.rejection_code] = rejections.get(outcome.rejection_code, 0) + 1
    return ExistenceCheckResult(
        spec_id=spec_id,
        symbol=symbol,
        timeframe=timeframe,
        bars_scanned=n,
        total_windows=total_windows,
        signals=signals,
        rejections_by_code=rejections,
    )


def write_existence_report(
    result: ExistenceCheckResult,
    out_dir: str | Path = "reports/existence",
) -> Path:
    out_path = Path(out_dir) / f"{result.spec_id}_{result.symbol}_{result.timeframe}_existence.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path
