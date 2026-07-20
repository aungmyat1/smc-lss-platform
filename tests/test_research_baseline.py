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


def _build_xau_fixture(tmp_path: Path) -> tuple[str, str]:
    m5_path = tmp_path / "XAUUSD-VIP_M5.csv"
    h1_path = tmp_path / "XAUUSD-VIP_H1.csv"
    _write_series(
        m5_path,
        [2000.0, 1999.6, 1999.2, 1999.0, 1998.8, 1999.0, 1999.2, 1999.4, 1999.6, 1999.8, 2000.0, 2000.2, 2000.0, 1999.8, 1999.6, 1999.8, 2000.0, 2000.1, 1999.9, 1999.7, 1999.9, 2000.1, 2000.2, 2000.3, 1999.7, 1999.4, 2000.6, 2001.2, 2001.8, 2002.4, 2003.0, 2003.6, 2004.2, 2004.8, 2005.4, 2006.0],
        "2026-07-17T06:00:00Z",
        5,
        overrides={
            24: {"open": 2000.3, "close": 1999.7, "high": 2000.4, "low": 1998.2},
            25: {"open": 1999.7, "close": 1999.4, "high": 2004.0, "low": 1999.1},
        },
    )
    _write_series(
        h1_path,
        [2000.0, 2000.8, 2001.6],
        "2026-07-17T06:00:00Z",
        60,
        overrides={
            0: {"open": 1999.8, "close": 2000.0, "high": 2000.2, "low": 1999.6},
            1: {"open": 2000.0, "close": 2000.8, "high": 2001.0, "low": 1999.9},
            2: {"open": 2000.8, "close": 2001.6, "high": 2001.8, "low": 2000.7},
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
    assert eur_cost["commission_usd_round_turn"] == pytest.approx(0.0)
    assert eur_cost["total_cost_r"] == pytest.approx(0.31)
    assert (2.0 - eur_cost["total_cost_r"]) == pytest.approx(1.69)

    xau_meta, xau_cost = engine._cost_to_r("XAUUSD-VIP", 2000.0, 1990.0)
    assert xau_meta.canonical_symbol == "XAUUSD"
    assert xau_cost["spread_price"] == pytest.approx(0.25)
    assert xau_cost["entry_slippage_price"] == pytest.approx(0.05)
    assert xau_cost["slippage_price_round_trip"] == pytest.approx(0.1)
    assert xau_cost["commission_usd_round_turn"] == pytest.approx(0.0)
    assert xau_cost["total_cost_r"] == pytest.approx(0.035)
    assert (2.0 - xau_cost["total_cost_r"]) == pytest.approx(1.965)


def test_baseline_runner_smoke(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    result = run_baseline(
        BASELINE_SPEC_PATH,
        data_dir,
        output_dir,
        cache_dir=tmp_path / "cache",
        resume=False,
        symbols=["EURUSD"],
    )

    run_dir = Path(result["run_dir"])
    manifest_path = run_dir / "baseline_manifest.json"
    latest_path = output_dir / "LATEST.json"
    assert manifest_path.exists()
    assert (run_dir / "baseline_report.md").exists()
    assert latest_path.exists()
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    assert latest["run_id"] == result["run_id"]
    assert Path(output_dir / latest["run_dir"]).exists()
    assert "combined" in result
    assert result["combined"]["total_trades"] >= 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["strategy_version"] == "1.0.0"
    assert manifest["runner_fingerprint"]


def test_batch_runner_persists_management_events_and_funnel_counts(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, h1_path = _build_fixture(data_dir)
    runner = BatchValidationRunner(cache_dir=tmp_path / "cache", report_path=tmp_path / "report.md", warmup_bars=20)
    target = ValidationTarget(
        symbol="EURUSD",
        timeframe="M5",
        m5_path=m5_path,
        h1_path=h1_path,
        source_symbol="EURUSD",
    )
    signal = SignalRecord(
        index=24,
        time="2026-07-17T08:00:00Z",
        direction="long",
        entry=95.0,
        stop=94.0,
        target=97.0,
        structure_key="fixture:signal",
        reason_codes=("TEST",),
    )
    def fake_generate_signal(i, m5, h1=None, d1=None, symbol=None, rejected_candidates=None, funnel_counts=None):
        if i == 24:
            if funnel_counts is not None:
                funnel_counts["candidate_ready"] = int(funnel_counts.get("candidate_ready", 0)) + 1
            return signal
        return None

    runner.engine.generate_signal = fake_generate_signal  # type: ignore[method-assign]

    result = runner.run_job(target, resume=False)

    assert result.result.management_events == tuple(event for trade in result.result.trades for event in trade.management_events)
    assert result.result.funnel_counts["executed_trade"] == len(result.result.trades)
    assert result.result.funnel_counts["candidate_ready"] >= result.result.funnel_counts["executed_trade"]


def test_batch_runner_alias_costs_propagate_through_source_symbol(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, h1_path = _build_xau_fixture(data_dir)
    runner = BatchValidationRunner(cache_dir=tmp_path / "cache", report_path=tmp_path / "report.md", warmup_bars=20)
    target = ValidationTarget(
        symbol="XAUUSD",
        timeframe="M5",
        m5_path=m5_path,
        h1_path=h1_path,
        source_symbol="XAUUSD-VIP",
    )
    signal = SignalRecord(
        index=24,
        time="2026-07-17T08:00:00Z",
        direction="long",
        entry=2000.0,
        stop=1990.0,
        target=2020.0,
        structure_key="alias:signal",
        reason_codes=("TEST",),
    )
    runner.engine.generate_signal = lambda i, m5, h1=None, d1=None, symbol=None, rejected_candidates=None, funnel_counts=None: signal if i == 24 else None  # type: ignore[method-assign]

    result = runner.run_job(target, resume=False)

    assert result.result.symbol_metadata["canonical_symbol"] == "XAUUSD"
    assert result.result.assumptions["source_symbol"] == "XAUUSD-VIP"
    assert result.result.trades
    trade = result.result.trades[0]
    assert trade.spread_price == pytest.approx(0.25)
    assert trade.entry_slippage_price == pytest.approx(0.05)
    assert trade.slippage_price_round_trip == pytest.approx(0.1)
    assert trade.total_cost_r == pytest.approx(0.035)


def test_clean_no_resume_runs_skip_cache_hits(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, h1_path = _build_fixture(data_dir)
    runner = BatchValidationRunner(cache_dir=tmp_path / "cache", report_path=tmp_path / "report.md", warmup_bars=20)
    target = ValidationTarget(
        symbol="EURUSD",
        timeframe="M5",
        m5_path=m5_path,
        h1_path=h1_path,
        source_symbol="EURUSD",
    )
    signal = SignalRecord(
        index=24,
        time="2026-07-17T08:00:00Z",
        direction="long",
        entry=95.0,
        stop=94.0,
        target=97.0,
        structure_key="no_resume:signal",
        reason_codes=("TEST",),
    )
    runner.engine.generate_signal = lambda i, m5, h1=None, d1=None, symbol=None, rejected_candidates=None, funnel_counts=None: signal if i == 24 else None  # type: ignore[method-assign]

    first = runner.run_job(target, resume=False)
    second = runner.run_job(target, resume=False)

    assert first.cache_hit is False
    assert second.cache_hit is False
    assert first.resumed is False
    assert second.resumed is False


def test_cache_invalidation_after_engine_changes(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, h1_path = _build_fixture(data_dir)
    target = ValidationTarget(
        symbol="XAUUSD",
        timeframe="M5",
        m5_path=m5_path,
        h1_path=h1_path,
        source_symbol="XAUUSD-VIP",
    )

    runner_one = BatchValidationRunner(cache_dir=tmp_path / "cache_one", warmup_bars=20)
    hash_one = runner_one._dataset_hash(target)
    path_one = runner_one._cache_path(target, hash_one)

    monkeypatch.setattr(BatchValidationRunner, "_runner_fingerprint", lambda self: "changed-fingerprint")
    runner_two = BatchValidationRunner(cache_dir=tmp_path / "cache_two", warmup_bars=20)
    hash_two = runner_two._dataset_hash(target)
    path_two = runner_two._cache_path(target, hash_two)

    assert runner_one.runner_fingerprint != runner_two.runner_fingerprint
    assert path_one != path_two


def test_atomic_publication_and_latest_pointer(tmp_path):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "baseline_out"
    data_dir.mkdir()
    _build_fixture(data_dir)

    result = run_baseline(
        BASELINE_SPEC_PATH,
        data_dir,
        output_dir,
        cache_dir=tmp_path / "cache",
        resume=False,
        symbols=["EURUSD"],
    )

    run_dir = Path(result["run_dir"])
    latest_path = output_dir / "LATEST.json"
    assert run_dir.exists()
    assert latest_path.exists()
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    assert latest["run_id"] == result["run_id"]
    assert Path(output_dir / latest["run_dir"]).resolve() == run_dir.resolve()
    assert not any(path.is_dir() and path.name.startswith(f"{output_dir.name}.staging.") for path in tmp_path.iterdir())


def test_dirty_worktree_identity_is_recorded(tmp_path, monkeypatch):
    from src.research import dataset_manifest as dataset_manifest_module  # noqa: E402

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    m5_path, _ = _build_fixture(data_dir)
    monkeypatch.setattr(dataset_manifest_module, "_git_dirty_worktree", lambda: True)

    manifest = dataset_manifest_module.build_dataset_manifest(
        strategy_id="ST-C1",
        strategy_version="1.0.0",
        git_sha="deadbeef",
        generated_utc="2026-07-20T00:00:00Z",
        random_seed=7,
        spec_path=BASELINE_SPEC_PATH,
        cost_profile_path=str(Path(ROOT) / "config" / "research_costs.yaml"),
        runner_fingerprint="fingerprint",
        dataset_paths=[m5_path],
        symbols=["EURUSD"],
        timeframes=["M5"],
        date_ranges={"EURUSD": {"start": None, "end": None}},
        execution_assumptions={"entry": "next-bar-open"},
    )

    assert manifest.dirty_worktree is True


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
