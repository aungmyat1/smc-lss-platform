"""Tests for the generic existence-check helper (tools/existence_check.py)."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.existence_check import ExistenceOutcome, run_existence_check, write_existence_report  # noqa: E402


def _make_candles(n: int) -> list[dict]:
    return [{"i": i} for i in range(n)]


def test_run_existence_check_counts_signals_and_rejections():
    candles = _make_candles(1000)

    def signal_fn(_candles, i):
        if i % 100 == 0:
            return ExistenceOutcome(signal=True)
        return ExistenceOutcome(signal=False, rejection_code="R1_TEST")

    result = run_existence_check("TEST", "EURUSD", "M15", candles, signal_fn)

    assert result.bars_scanned == 1000
    assert result.total_windows == 1000
    assert result.signals == 10
    assert result.rejections_by_code == {"R1_TEST": 990}
    assert result.to_dict()["signal_rate"] == 0.01


def test_run_existence_check_respects_warmup_bars():
    candles = _make_candles(100)

    def signal_fn(_candles, _i):
        return ExistenceOutcome(signal=True)

    result = run_existence_check("TEST", "EURUSD", "M15", candles, signal_fn, warmup_bars=40)

    assert result.total_windows == 60
    assert result.signals == 60


def test_run_existence_check_never_fires_reports_zero_rate():
    candles = _make_candles(50)

    def signal_fn(_candles, _i):
        return ExistenceOutcome(signal=False, rejection_code="R1_NEVER")

    result = run_existence_check("TEST", "EURUSD", "M15", candles, signal_fn)

    assert result.signals == 0
    assert result.to_dict()["signal_rate"] == 0.0
    assert result.rejections_by_code == {"R1_NEVER": 50}


def test_write_existence_report_writes_json(tmp_path):
    candles = _make_candles(10)

    def signal_fn(_candles, i):
        return ExistenceOutcome(signal=(i == 5))

    result = run_existence_check("TEST", "EURUSD", "M15", candles, signal_fn)
    out_path = write_existence_report(result, out_dir=tmp_path)

    assert out_path.exists()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["spec_id"] == "TEST"
    assert payload["signals"] == 1
