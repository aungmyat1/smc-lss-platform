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
    d1_path = tmp_path / "EURUSD_D1.csv"
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
    _write_series(
        d1_path,
        [93.0, 94.0, 95.0, 96.0, 97.0],
        "2026-07-13T00:00:00Z",
        1440,
        overrides={
            0: {"open": 92.8, "close": 93.0, "high": 93.3, "low": 92.6},
            1: {"open": 93.0, "close": 94.0, "high": 94.2, "low": 92.9},
            2: {"open": 94.0, "close": 95.0, "high": 95.3, "low": 93.8},
            3: {"open": 95.0, "close": 96.0, "high": 96.4, "low": 94.8},
            4: {"open": 96.0, "close": 97.0, "high": 97.2, "low": 95.9},
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
    assert eur_cost["slippage_price_round_trip"] == pytest.approx(0.00006)
    assert eur_cost["total_cost_r"] == pytest.approx(0.31)
    assert (2.0 - eur_cost["total_cost_r"]) == pytest.approx(1.69)

    xau_meta, xau_cost = engine._cost_to_r("XAUUSD-VIP", 2000.0, 1990.0)
    assert xau_meta.canonical_symbol == "XAUUSD"
    assert xau_cost["spread_price"] == pytest.approx(0.25)
    assert xau_cost["entry_slippage_price"] == pytest.approx(0.05)
    assert xau_cost["slippage_price_round_trip"] == pytest.approx(0.1)
    assert xau_cost["total_cost_r"] == pytest.approx(0.035)
    assert (2.0 - xau_cost["total_cost_r"]) == pytest.approx(1.965)


def test_higher_timeframe_is_not_visible_until_close(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, h1_path = _build_fixture(data_dir)
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20, point_size=None)
    _, h1, _ = engine.load_series(m5_path, h1_path=h1_path)

    before_close = engine._bounded_context_window(h1, "H1", "2026-07-17T07:30:00Z", 10)
    at_close = engine._bounded_context_window(h1, "H1", "2026-07-17T08:00:00Z", 10)

    assert [item["time"] for item in before_close] == ["2026-07-17T06:00:00Z"]
    assert [item["time"] for item in at_close] == ["2026-07-17T06:00:00Z", "2026-07-17T07:00:00Z"]


def test_baseline_runner_smoke(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    result = run_baseline(BASELINE_SPEC_PATH, data_dir, output_dir, symbols=["EURUSD"])

    manifest_path = output_dir / "baseline_manifest.json"
    assert manifest_path.exists()
    assert (output_dir / "baseline_report.md").exists()
    assert "combined" in result
    assert "funnel_counts" in result
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["strategy_version"] == "1.0.0"


def test_research_baseline_fails_closed_on_missing_datasets(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    with pytest.raises(ValueError, match="missing required baseline datasets"):
        run_baseline(BASELINE_SPEC_PATH, data_dir, output_dir, symbols=["EURUSD", "GBPUSD"])


def test_research_baseline_is_deterministic(tmp_path):
    data_dir = tmp_path / "data"
    out_one = tmp_path / "out_one"
    out_two = tmp_path / "out_two"
    data_dir.mkdir()
    _build_fixture(data_dir)

    run_one = run_baseline(BASELINE_SPEC_PATH, data_dir, out_one, symbols=["EURUSD"])
    run_two = run_baseline(BASELINE_SPEC_PATH, data_dir, out_two, symbols=["EURUSD"])

    manifest_one = dict(run_one["manifest"])
    manifest_two = dict(run_two["manifest"])
    manifest_one.pop("generated_utc", None)
    manifest_two.pop("generated_utc", None)
    assert manifest_one == manifest_two
    manifest_file_one = json.loads((out_one / "baseline_manifest.json").read_text(encoding="utf-8"))
    manifest_file_two = json.loads((out_two / "baseline_manifest.json").read_text(encoding="utf-8"))
    manifest_file_one.pop("generated_utc", None)
    manifest_file_two.pop("generated_utc", None)
    assert manifest_file_one == manifest_file_two
    assert (out_one / "baseline_trades.csv").read_text(encoding="utf-8") == (out_two / "baseline_trades.csv").read_text(encoding="utf-8")


def test_rejected_candidates_and_funnel_counts_persist(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    run_baseline(BASELINE_SPEC_PATH, data_dir, output_dir, symbols=["EURUSD"])

    rejected_path = output_dir / "rejected_candidates.csv"
    metrics_path = output_dir / "baseline_metrics.json"
    assert rejected_path.exists()
    assert metrics_path.exists()

    with rejected_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert {"signal_time", "stage", "rejection_reason", "symbol"} <= set(reader.fieldnames or [])

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert "funnel_counts" in metrics
    assert isinstance(metrics["funnel_counts"], dict)


def test_htf_context_uses_cached_bounded_lookups():
    engine = HistoricalReplayEngine(contract_path=CONTRACT_PATH, warmup_bars=20, point_size=None)
    h1 = [
        {"time": f"2026-07-17 {hour:02d}:00", "open": 100.0 + hour, "high": 100.5 + hour, "low": 99.5 + hour, "close": 100.25 + hour}
        for hour in range(24)
    ]
    calls = {"build": 0}
    original = engine._build_timeline

    def wrapped(series, timeframe):
        calls["build"] += 1
        return original(series, timeframe)

    engine._build_timeline = wrapped  # type: ignore[method-assign]
    for idx in range(200):
        hour = idx % 24
        engine._bounded_context_window(h1, "H1", f"2026-07-17 {hour:02d}:30", 12)

    assert calls["build"] == 1


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
