"""Tests for the ST-C1 historical replay scaffold."""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from validation.historical_replay_engine import HistoricalReplayEngine, write_baseline_report  # noqa: E402


CONTRACT_PATH = os.path.join(ROOT, "strategies", "candidates", "ST-C1_v1.yaml")


def _write_series(path: Path, closes: list[float], start_time: str, step_minutes: int, overrides: dict[int, dict[str, float]] | None = None) -> None:
    overrides = overrides or {}
    rows = []
    prev_close = closes[0]
    current_time = start_time
    from datetime import datetime, timedelta

    dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    for idx, close in enumerate(closes):
        open_ = prev_close if idx > 0 else close
        high = max(open_, close) + 0.25
        low = min(open_, close) - 0.25
        if idx in overrides:
            high = overrides[idx].get("high", high)
            low = overrides[idx].get("low", low)
            open_ = overrides[idx].get("open", open_)
            close = overrides[idx].get("close", close)
        rows.append((dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"), open_, high, low, close))
        prev_close = close
        dt += timedelta(minutes=step_minutes)

    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close"])
        writer.writerows(rows)


def _m5_closes() -> list[float]:
    return [
        95.0, 94.6, 94.2, 94.0, 93.8, 94.0, 94.2, 94.4, 94.6, 94.8,
        95.0, 95.2, 95.0, 94.8, 94.6, 94.8, 95.0, 95.1, 94.9, 94.7,
        94.9, 95.1, 95.2, 95.3, 94.7, 94.4, 95.6, 96.2, 96.8, 97.4,
        98.0, 98.6, 99.2, 99.8, 100.4, 101.0,
    ]


def _h1_closes() -> list[float]:
    return [95.0, 95.8, 96.6]


def _build_fixture(tmp_path: Path) -> tuple[str, str]:
    m5_path = tmp_path / "EURUSD_M5.csv"
    h1_path = tmp_path / "EURUSD_H1.csv"
    _write_series(
        m5_path,
        _m5_closes(),
        "2026-07-17T06:00:00Z",
        5,
        overrides={
            24: {"open": 95.3, "close": 94.7, "high": 95.4, "low": 93.2},
            25: {"open": 94.7, "close": 94.4, "high": 100.0, "low": 94.1},
        },
    )
    _write_series(
        h1_path,
        _h1_closes(),
        "2026-07-17T06:00:00Z",
        60,
        overrides={
            0: {"open": 94.8, "close": 95.0, "high": 95.2, "low": 94.6},
            1: {"open": 95.0, "close": 95.8, "high": 96.0, "low": 94.9},
            2: {"open": 95.8, "close": 96.6, "high": 96.8, "low": 95.7},
        },
    )
    return str(m5_path), str(h1_path)


def test_historical_replay_generates_trade_and_metrics(tmp_path):
    m5_path, h1_path = _build_fixture(tmp_path)
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20, commission_r=0.02, point_size=0.0001)
    result = engine.run_from_paths(m5_path, h1_path=h1_path, symbol="EURUSD")

    assert result.status == "READY_FOR_STATISTICAL_VALIDATION"
    assert len(result.signals) >= 1
    assert len(result.trades) >= 1
    assert result.metrics["total_trades"] == len(result.trades)
    assert "profit_factor" in result.metrics
    assert "expectancy_r" in result.metrics
    assert "average_r" in result.metrics
    assert "maximum_drawdown_r" in result.metrics
    assert "sharpe_ratio" in result.metrics

    trade = result.trades[0]
    assert trade.entry_index == result.signals[0].index + 1
    assert trade.outcome in {"TARGET", "STOP", "TIMEOUT"}
    signal = result.signals[0]
    assert signal.structure_identity
    assert signal.canonical_symbol == "EURUSD"
    assert signal.poi_time
    assert signal.sweep_time


def test_replay_rejects_unsorted_data(tmp_path):
    m5_path, h1_path = _build_fixture(tmp_path)
    lines = Path(m5_path).read_text(encoding="utf-8").splitlines()
    header, rows = lines[0], lines[1:]
    Path(m5_path).write_text("\n".join([header] + list(reversed(rows))) + "\n", encoding="utf-8")
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20)
    with pytest.raises(ValueError):
        engine.run_from_paths(m5_path, h1_path=h1_path, symbol="EURUSD")


def test_baseline_report_is_written(tmp_path):
    m5_path, h1_path = _build_fixture(tmp_path)
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20, commission_r=0.02, point_size=0.0001)
    result = engine.run_from_paths(m5_path, h1_path=h1_path, symbol="EURUSD")
    report_path = tmp_path / "ST-C1_BASELINE_BACKTEST_REPORT.md"
    write_baseline_report(result, path=str(report_path))

    text = report_path.read_text(encoding="utf-8")
    assert "ST-C1 Baseline Backtest Report" in text
    assert "READY_FOR_STATISTICAL_VALIDATION" in text
    assert "profit_factor" in text
