"""Tests for the resumable ST-C1 batch validation runner."""
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from validation.batch_validation_runner import BatchValidationRunner, ValidationTarget  # noqa: E402


CONTRACT_PATH = os.path.join(ROOT, "strategies", "candidates", "ST-C1_v1.yaml")


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _write_series(
    path: Path,
    closes: list[float],
    start_time: str,
    step_minutes: int,
    overrides: dict[int, dict[str, float]] | None = None,
) -> None:
    overrides = overrides or {}
    rows = []
    prev_close = closes[0]
    current = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    for idx, close in enumerate(closes):
        open_ = prev_close if idx > 0 else close
        high = max(open_, close) + 0.25
        low = min(open_, close) - 0.25
        if idx in overrides:
            high = overrides[idx].get("high", high)
            low = overrides[idx].get("low", low)
            open_ = overrides[idx].get("open", open_)
            close = overrides[idx].get("close", close)
        rows.append((_iso(current), open_, high, low, close))
        prev_close = close
        current += timedelta(minutes=step_minutes)

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


def _build_fixture(symbol: str, tmp_path: Path) -> tuple[str, str]:
    m5_path = tmp_path / f"{symbol}_M5.csv"
    h1_path = tmp_path / f"{symbol}_H1.csv"
    m5_path.parent.mkdir(parents=True, exist_ok=True)
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


def _build_target(symbol: str, tmp_path: Path, source_symbol: str | None = None) -> ValidationTarget:
    m5_path, h1_path = _build_fixture(symbol, tmp_path)
    return ValidationTarget(
        symbol=symbol,
        timeframe="M5",
        m5_path=m5_path,
        h1_path=h1_path,
        d1_path=None,
        source_symbol=source_symbol or symbol,
    )


def test_batch_validation_runner_can_resume_partial_run(tmp_path):
    target = _build_target("EURUSD", tmp_path)
    cache_dir = tmp_path / "cache"
    runner = BatchValidationRunner(
        contract_path=CONTRACT_PATH,
        cache_dir=cache_dir,
        report_path=tmp_path / "report.md",
        warmup_bars=20,
        progress_every=4,
        progress_sink=lambda progress: (_ for _ in ()).throw(RuntimeError("interrupt")) if progress.trades_generated >= 1 and progress.phase == "running" else None,
    )

    with pytest.raises(RuntimeError):
        runner.run_job(target, resume=True)

    cache_files = list(cache_dir.glob("*.json"))
    assert cache_files
    cached = cache_files[0].read_text(encoding="utf-8")
    assert '"complete": false' in cached.lower()

    resumed_runner = BatchValidationRunner(
        contract_path=CONTRACT_PATH,
        cache_dir=cache_dir,
        report_path=tmp_path / "report.md",
        warmup_bars=20,
        progress_every=4,
        progress_sink=lambda progress: None,
    )
    resumed = resumed_runner.run_job(target, resume=True)
    assert resumed.complete is True
    assert resumed.resumed is True
    assert resumed.result.metrics["total_trades"] >= 1

    cached_again = resumed_runner.run_job(target, resume=True)
    assert cached_again.cache_hit is True
    assert cached_again.complete is True
    assert cached_again.result.metrics == resumed.result.metrics


def test_batch_validation_runner_writes_real_data_report(tmp_path):
    eur = _build_target("EURUSD", tmp_path / "eur")
    xau = _build_target("XAUUSD", tmp_path / "xau", source_symbol="XAUUSD-VIP")
    report_path = tmp_path / "ST-C1_REAL_DATA_STATISTICAL_VALIDATION.md"
    runner = BatchValidationRunner(
        contract_path=CONTRACT_PATH,
        cache_dir=tmp_path / "cache",
        report_path=report_path,
        warmup_bars=20,
        progress_every=100,
        progress_sink=lambda progress: None,
    )

    results = runner.run_all([eur, xau], resume=True)
    assert len(results) == 2
    assert all(item.complete for item in results)

    text = report_path.read_text(encoding="utf-8")
    assert "ST-C1 Real Data Statistical Validation Report" in text
    assert "READY_FOR_ROBUSTNESS_VALIDATION" in text
    assert "EURUSD" in text
    assert "XAUUSD" in text
    assert "XAUUSD-VIP" in text
