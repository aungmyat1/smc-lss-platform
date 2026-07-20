"""Focused tests for the corrected ST-C1 research baseline."""
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from symbol_metadata import resolve_symbol  # noqa: E402
from validation.historical_replay_engine import HistoricalReplayEngine, SignalRecord  # noqa: E402
from src.research.run_baseline import run_baseline  # noqa: E402


CONTRACT_PATH = os.path.join(ROOT, "strategies", "candidates", "ST-C1_v1.yaml")
BASELINE_SPEC_PATH = os.path.join(ROOT, "specs", "research", "v1_baseline.yaml")


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _write_series(path: Path, closes: list[float], start_time: str, step_minutes: int, overrides: dict[int, dict[str, float]] | None = None) -> None:
    overrides = overrides or {}
    rows = []
    prev_close = closes[0]
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
        rows.append((_iso(dt), open_, high, low, close))
        prev_close = close
        dt += timedelta(minutes=step_minutes)

    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close"])
        writer.writerows(rows)


def _build_fixture(tmp_path: Path) -> tuple[str, str]:
    m5_path = tmp_path / "EURUSD_M5.csv"
    h1_path = tmp_path / "EURUSD_H1.csv"
    _write_series(
        m5_path,
        [95.0, 94.6, 94.2, 94.0, 93.8, 94.0, 94.2, 94.4, 94.6, 94.8, 95.0, 95.2, 95.0, 94.8, 94.6, 94.8, 95.0, 95.1, 94.9, 94.7, 94.9, 95.1, 95.2, 95.3, 94.7, 94.4, 95.6, 96.2, 96.8, 97.4, 98.0, 98.6, 99.2, 99.8, 100.4, 101.0],
        "2026-07-17T06:00:00Z",
        5,
        overrides={
            24: {"open": 95.3, "close": 94.7, "high": 95.4, "low": 93.2},
            25: {"open": 94.7, "close": 94.4, "high": 100.0, "low": 94.1},
        },
    )
    _write_series(
        h1_path,
        [95.0, 95.8, 96.6],
        "2026-07-17T06:00:00Z",
        60,
        overrides={
            0: {"open": 94.8, "close": 95.0, "high": 95.2, "low": 94.6},
            1: {"open": 95.0, "close": 95.8, "high": 96.0, "low": 94.9},
            2: {"open": 95.8, "close": 96.6, "high": 96.8, "low": 95.7},
        },
    )
    return str(m5_path), str(h1_path)


def test_symbol_metadata_alias_resolution():
    meta = resolve_symbol("XAUUSD-VIP")
    assert meta.canonical_symbol == "XAUUSD"
    assert meta.point_size == 0.01
    assert meta.pip_size == 0.1


def test_trade_detail_records_management_and_costs(tmp_path):
    m5_path, h1_path = _build_fixture(tmp_path)
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20, point_size=None)
    m5, h1, _ = engine.load_series(m5_path, h1_path=h1_path)
    m5 = list(m5)
    m5[25] = dict(m5[25], high=96.35, low=94.85, close=96.0)
    m5[26] = dict(m5[26], high=97.25, low=95.8, close=97.1)
    signal = SignalRecord(
        index=24,
        time=m5[24]["time"],
        direction="long",
        entry=95.0,
        stop=94.0,
        target=97.0,
        structure_key="fixture:1",
        reason_codes=("TEST",),
    )
    detail = engine._simulate_trade_detail(signal, m5, entry_index=25, symbol="EURUSD")

    assert detail["partial_taken"] is True
    assert detail["break_even_activated"] is True
    assert detail["gross_r"] > 1.0
    assert detail["net_r"] <= detail["gross_r"]
    assert any(event["event"] == "BREAK_EVEN_ACTIVATED" for event in detail["management_events"])


def test_baseline_runner_smoke(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    result = run_baseline(BASELINE_SPEC_PATH, data_dir, output_dir)

    assert (output_dir / "baseline_manifest.json").exists()
    assert (output_dir / "baseline_report.md").exists()
    assert "combined" in result
    assert result["combined"]["total_trades"] >= 1
