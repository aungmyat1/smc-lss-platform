"""Focused tests for the corrected ST-C1 research baseline."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from config import load as load_config  # noqa: E402
from src.live_signal import size as live_size  # noqa: E402
from symbol_metadata import resolve_symbol  # noqa: E402
from validation.batch_validation_runner import BatchValidationRunner, ValidationTarget  # noqa: E402
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


def test_live_sizing_equivalence_for_canonical_and_alias_symbols():
    cfg = load_config()
    sig = {"dir": "long", "entry": 2000.0, "stop": 1990.0}
    xau = cfg.symbol("XAUUSD")
    alias_meta = resolve_symbol("XAUUSD-VIP")
    canonical = live_size(sig, 10000.0, cfg.risk.risk_pct_demo, cfg.risk.min_rr, pip=xau.pip, pip_value=xau.pip_value_per_lot, lot_step=cfg.execution.lot_step, min_rr=cfg.risk.min_rr)
    aliased = live_size(sig, 10000.0, cfg.risk.risk_pct_demo, cfg.risk.min_rr, pip=alias_meta.pip_size, pip_value=alias_meta.pip_value_per_lot, lot_step=cfg.execution.lot_step, min_rr=cfg.risk.min_rr)

    assert canonical == aliased
    assert canonical["decision"] == "GO"
    assert canonical["rr"] == cfg.risk.min_rr


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


def test_cost_math_matches_hand_calculation():
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20, point_size=None)

    eur_meta, eur_cost = engine._cost_to_r("EURUSD", 1.1000, 1.0990)
    assert eur_meta.canonical_symbol == "EURUSD"
    assert eur_cost["spread_price"] == pytest.approx(0.00025)
    assert eur_cost["entry_slippage_price"] == pytest.approx(0.00003)
    assert eur_cost["total_cost_r"] == pytest.approx(0.28)
    assert (2.0 - eur_cost["total_cost_r"]) == pytest.approx(1.72)

    xau_meta, xau_cost = engine._cost_to_r("XAUUSD-VIP", 2000.0, 1990.0)
    assert xau_meta.canonical_symbol == "XAUUSD"
    assert xau_cost["spread_price"] == pytest.approx(0.25)
    assert xau_cost["entry_slippage_price"] == pytest.approx(0.05)
    assert xau_cost["total_cost_r"] == pytest.approx(0.03)
    assert (2.0 - xau_cost["total_cost_r"]) == pytest.approx(1.97)


def test_baseline_runner_smoke(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    result = run_baseline(BASELINE_SPEC_PATH, data_dir, output_dir)

    manifest_path = output_dir / "baseline_manifest.json"
    assert manifest_path.exists()
    assert (output_dir / "baseline_report.md").exists()
    assert "combined" in result
    assert result["combined"]["total_trades"] >= 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["strategy_version"] == "1.0.0"


def test_research_baseline_rejects_conflicting_timeframes(tmp_path):
    spec_path = tmp_path / "conflicting.yaml"
    spec_path.write_text(
        """
strategy:
  strategy_id: ST-C1
  name: London SMC Reversal
  version: 1.0.0
  status: candidate
  source:
    specification: docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md
    research_spec: specs/v3.6.yaml
    execution_spec: specs/v1.yaml
  validation:
    status: pending
    approval_status: pending
    qualification: not_started
market_universe:
  asset_class: [forex, metals]
  instruments: [EURUSD, XAUUSD]
  sessions: [London, NewYork]
  timezone: UTC
  timeframes:
    bias: H1
    setup: H1
    confirmation: M5
    execution: M5
version: 1
track: research
status: baseline
promotion_stage: research_only
symbol: EURUSD
htf: H4
entry_tf: M15
ltf_confirm: M1
swing_lookback: 2
equal_level_tol_pips: 2
min_fvg_pips: 3
risk_pct: 1.0
min_rr: 2.0
sessions: [london, ny]
""",
        encoding="utf-8",
    )
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _build_fixture(data_dir)

    with pytest.raises(ValueError, match="deprecated top-level timeframe/spec keys"):
        run_baseline(spec_path, data_dir, tmp_path / "out")


def test_cache_identity_changes_for_symbol_metadata_and_old_generic_model(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, h1_path = _build_fixture(data_dir)
    runner = BatchValidationRunner(cache_dir=tmp_path / "cache")
    target = ValidationTarget(
        symbol="XAUUSD",
        timeframe="M5",
        m5_path=m5_path,
        h1_path=h1_path,
        source_symbol="XAUUSD-VIP",
    )
    dataset_hash = runner._dataset_hash(target)
    new_path = runner._cache_path(target, dataset_hash)
    old_execution_params = {
        "spread_points": 25.0,
        "slippage_points": 3.0,
        "commission_r": 0.0,
        "point_size": 0.0001,
        "stop_buffer_atr_mult": 0.15,
        "warmup_bars": 40,
    }
    old_hash = hashlib.sha256()
    for part in (
        json.dumps(old_execution_params, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
        runner.strategy_version,
        dataset_hash,
        target.source_symbol or target.display_symbol,
    ):
        old_hash.update(part.encode("utf-8"))
        old_hash.update(b"\0")
    old_path = runner.cache_dir / f"{target.display_symbol}_{target.timeframe}_{old_hash.hexdigest()[:24]}.json"

    assert new_path != old_path
