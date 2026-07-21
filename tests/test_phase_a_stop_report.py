"""Tests for Phase A stop-report generation."""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from src.research.dataset_manifest import build_dataset_manifest, sha256_file, write_manifest  # noqa: E402
from src.research.phase_a_stop_report import build_phase_a_stop_report  # noqa: E402
from src.research.run_phase_a_gate import run_phase_a_gate  # noqa: E402
from src.research.trade_recorder import write_csv  # noqa: E402


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _write_series(path: Path, start_time: str, step_minutes: int, closes: list[float]) -> None:
    rows = []
    current = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    prev_close = closes[0]
    for idx, close in enumerate(closes):
        open_ = prev_close if idx else close
        high = max(open_, close) + 0.25
        low = min(open_, close) - 0.25
        rows.append((_iso(current), open_, high, low, close))
        prev_close = close
        current += timedelta(minutes=step_minutes)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close"])
        writer.writerows(rows)


def _write_data_dir(root: Path, symbols: list[str]) -> None:
    closes = {
        "M5": [100.0, 100.2, 100.1, 100.4],
        "H1": [100.0, 100.5, 100.9],
        "D1": [100.0, 101.0, 101.5],
    }
    for symbol in symbols:
        _write_series(root / f"{symbol}_M5.csv", "2026-07-20T00:00:00Z", 5, closes["M5"])
        _write_series(root / f"{symbol}_H1.csv", "2026-07-20T00:00:00Z", 60, closes["H1"])
        _write_series(root / f"{symbol}_D1.csv", "2026-07-20T00:00:00Z", 1440, closes["D1"])


def _write_trade_rows(path: Path) -> None:
    row = {
        "signal_index": 1,
        "signal_time": "2026-07-20T00:00:00Z",
        "entry_index": 2,
        "entry_time": "2026-07-20T00:05:00Z",
        "exit_index": 3,
        "exit_time": "2026-07-20T00:10:00Z",
        "direction": "long",
        "entry": 100.0,
        "stop": 99.0,
        "target": 102.0,
        "exit_price": 101.7,
        "gross_r": 2.0,
        "cost_r": 0.3,
        "net_r": 1.7,
        "outcome": "TARGET",
        "structure_key": "fixture:1",
        "symbol_metadata_version": "symbol-metadata-v1",
        "spread_price": 0.1,
        "spread_points": 1.0,
        "spread_pips": 1.0,
        "entry_slippage_price": 0.01,
        "exit_slippage_price": 0.01,
        "slippage_price_round_trip": 0.02,
        "commission_usd_round_turn": 0.0,
        "commission": 0.0,
        "spread_r": 0.25,
        "slippage_r": 0.05,
        "commission_r": 0.0,
        "swap_r": 0.0,
        "price_cost_round_trip": 0.02,
        "total_cost": 0.3,
        "total_cost_r": 0.3,
        "partial_taken": False,
        "break_even_activated": False,
        "ambiguous_bar": False,
        "unresolved_open_position": False,
        "management_events": "[]",
        "experiment_id": "baseline",
        "strategy_id": "ST-C1",
        "strategy_version": "1.0.0",
        "symbol": "EURUSD",
    }
    write_csv(path, [row], fieldnames=list(row.keys()))


def _write_equity_rows(path: Path) -> None:
    write_csv(
        path,
        [{"entry_time": "2026-07-20T00:05:00Z", "cum_net_r": 1.7}],
        fieldnames=["entry_time", "cum_net_r"],
    )


def _write_empty_csv(path: Path, fieldnames: list[str]) -> None:
    write_csv(path, [], fieldnames=fieldnames)


def _write_run(
    output_root: Path,
    run_id: str,
    created_utc: str,
    generated_utc: str,
    manifest_symbols: list[str],
    data_dir: Path,
) -> Path:
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    dataset_paths = [data_dir / f"{symbol}_{timeframe}.csv" for symbol in manifest_symbols for timeframe in ("M5", "H1", "D1")]
    manifest = build_dataset_manifest(
        strategy_id="ST-C1",
        strategy_version="1.0.0",
        git_sha="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        generated_utc=generated_utc,
        random_seed=7,
        spec_path="specs/research/v1_baseline.yaml",
        cost_profile_path="config/research_costs.yaml",
        spec_sha256="spec-sha",
        cost_profile_sha256="cost-sha",
        runner_fingerprint="runner-fingerprint",
        dirty_worktree=False,
        dataset_paths=dataset_paths,
        symbols=manifest_symbols,
        timeframes=["M5", "H1", "D1"],
        date_ranges={symbol: {"start": "2026-07-20T00:00:00Z", "end": "2026-07-20T01:00:00Z"} for symbol in manifest_symbols},
        execution_assumptions={
            "entry": "next-bar-open",
            "breakeven": True,
            "managed_partial": True,
            "slippage_convention": "per_side",
            "commission_unit": "usd_round_turn",
            "stop_first": True,
        },
    )
    write_manifest(run_dir / "baseline_manifest.json", manifest)

    metrics = {
        "combined": {
            "total_trades": 1,
            "win_rate_pct": 100.0,
            "profit_factor": 2.0,
            "expectancy_r": 1.7,
            "maximum_drawdown_r": 0.0,
            "sharpe_ratio": 1.0,
        },
        "by_symbol": {
            "EURUSD": {
                "total_trades": 1,
                "win_rate_pct": 100.0,
                "profit_factor": 2.0,
                "expectancy_r": 1.7,
                "maximum_drawdown_r": 0.0,
                "sharpe_ratio": 1.0,
            }
        },
        "cost_breakdown": {
            "trade_count": 1,
            "gross_r": 2.0,
            "net_r": 1.7,
            "spread_r": 0.25,
            "slippage_r": 0.05,
            "commission_r": 0.0,
            "swap_r": 0.0,
            "total_cost_drag_r": 0.3,
        },
        "funnel_counts": {
            "evaluated": 4,
            "session_pass": 4,
            "rejected_session": 0,
            "signal_pass": 1,
            "rejected_signal": 0,
            "bias_pass": 1,
            "rejected_bias": 0,
            "sweep_pass": 1,
            "rejected_sweep": 0,
            "poi_pass": 1,
            "rejected_poi": 0,
            "candidate_ready": 1,
            "executed_trade": 1,
            "skipped_open_trade": 0,
            "duplicate_structure": 0,
            "rejected_risk": 0,
            "rejected_target": 0,
            "censored_end_of_data": 0,
        },
        "failure_counts": {"win": 1},
    }
    (run_dir / "baseline_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "baseline_report.md").write_text("# report\n", encoding="utf-8")
    _write_trade_rows(run_dir / "baseline_trades.csv")
    _write_equity_rows(run_dir / "baseline_equity.csv")
    _write_empty_csv(run_dir / "management_events.csv", ["experiment_id", "event"])
    _write_empty_csv(run_dir / "rejected_candidates.csv", ["signal_time", "stage", "direction", "structure_key", "rejection_reason", "symbol", "metadata", "experiment_id"])
    _write_empty_csv(run_dir / "censored_trades.csv", ["schema_version", "signal_index", "signal_time", "entry_index", "entry_time", "exit_index", "exit_time", "direction", "entry", "stop", "target", "exit_price", "gross_r", "cost_r", "net_r", "outcome", "structure_key", "symbol_metadata_version", "spread_price", "spread_points", "spread_pips", "entry_slippage_price", "exit_slippage_price", "slippage_price_round_trip", "commission_usd_round_turn", "commission", "spread_r", "slippage_r", "commission_r", "swap_r", "price_cost_round_trip", "total_cost", "total_cost_r", "partial_taken", "break_even_activated", "ambiguous_bar", "unresolved_open_position", "management_events", "experiment_id", "strategy_id", "strategy_version", "symbol"])
    write_csv(
        run_dir / "cost_legs.csv",
        [
            {"schema_version": 1, "trade_id": "fixture:1", "symbol": "EURUSD", "entry_time": "2026-07-20T00:05:00Z", "leg": "spread", "cost_r": 0.25, "source_column": "spread_r", "experiment_id": "baseline"},
            {"schema_version": 1, "trade_id": "fixture:1", "symbol": "EURUSD", "entry_time": "2026-07-20T00:05:00Z", "leg": "slippage", "cost_r": 0.05, "source_column": "slippage_r", "experiment_id": "baseline"},
            {"schema_version": 1, "trade_id": "fixture:1", "symbol": "EURUSD", "entry_time": "2026-07-20T00:05:00Z", "leg": "commission", "cost_r": 0.0, "source_column": "commission_r", "experiment_id": "baseline"},
            {"schema_version": 1, "trade_id": "fixture:1", "symbol": "EURUSD", "entry_time": "2026-07-20T00:05:00Z", "leg": "swap", "cost_r": 0.0, "source_column": "swap_r", "experiment_id": "baseline"},
        ],
        fieldnames=["schema_version", "trade_id", "symbol", "entry_time", "leg", "cost_r", "source_column", "experiment_id"],
    )
    write_csv(
        run_dir / "funnel_report.csv",
        [{"schema_version": 1, "metric": key, "count": value} for key, value in sorted(metrics["funnel_counts"].items())],
        fieldnames=["schema_version", "metric", "count"],
    )
    (run_dir / "artifact_schema.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "artifacts": {
                    "trades": {"path": "baseline_trades.csv"},
                    "equity": {"path": "baseline_equity.csv"},
                    "management_events": {"path": "management_events.csv"},
                    "rejected_candidates": {"path": "rejected_candidates.csv"},
                    "censored_trades": {"path": "censored_trades.csv"},
                    "cost_legs": {"path": "cost_legs.csv"},
                    "funnel_report": {"path": "funnel_report.csv"},
                    "manifest": {"path": "baseline_manifest.json"},
                    "metrics": {"path": "baseline_metrics.json"},
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    latest = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "report_path": str(run_dir / "baseline_report.md"),
        "manifest_path": str(run_dir / "baseline_manifest.json"),
        "metrics_path": str(run_dir / "baseline_metrics.json"),
        "created_utc": created_utc,
        "runner_fingerprint": "runner-fingerprint",
        "dirty_worktree": False,
        "spec_sha256": "spec-sha",
        "cost_profile_sha256": "cost-sha",
        "complete": True,
    }
    latest["artifact_hashes"] = {
        "manifest": sha256_file(run_dir / "baseline_manifest.json"),
        "metrics": sha256_file(run_dir / "baseline_metrics.json"),
        "report": sha256_file(run_dir / "baseline_report.md"),
        "trades": sha256_file(run_dir / "baseline_trades.csv"),
        "equity": sha256_file(run_dir / "baseline_equity.csv"),
        "management_events": sha256_file(run_dir / "management_events.csv"),
        "rejected_candidates": sha256_file(run_dir / "rejected_candidates.csv"),
        "censored_trades": sha256_file(run_dir / "censored_trades.csv"),
        "cost_legs": sha256_file(run_dir / "cost_legs.csv"),
        "funnel_report": sha256_file(run_dir / "funnel_report.csv"),
        "artifact_schema": sha256_file(run_dir / "artifact_schema.json"),
    }
    (output_root / "LATEST.json").write_text(json.dumps(latest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir


def test_phase_a_stop_report_blocks_when_gbpusd_data_is_missing(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_data_dir(data_dir, ["EURUSD", "XAUUSD"])

    clean_a_root = tmp_path / "clean_a"
    clean_b_root = tmp_path / "clean_b"
    resumed_root = tmp_path / "resumed"
    _write_run(clean_a_root, "20260720T190003Z-aaaa1111", "2026-07-20T19:00:03Z", "2026-07-20T19:00:03Z", ["EURUSD", "XAUUSD"], data_dir)
    _write_run(clean_b_root, "20260720T194014Z-bbbb2222", "2026-07-20T19:40:14Z", "2026-07-20T19:40:14Z", ["EURUSD", "XAUUSD"], data_dir)
    _write_run(resumed_root, "20260720T195500Z-cccc3333", "2026-07-20T19:55:00Z", "2026-07-20T19:55:00Z", ["EURUSD", "XAUUSD"], data_dir)

    report = build_phase_a_stop_report(
        clean_run_a=clean_a_root,
        clean_run_b=clean_b_root,
        resumed_run=resumed_root,
        data_dir=data_dir,
        suite_status="passed",
        ci_status="passed",
        ci_head="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        git_state={
            "branch": "research/st-c1-baseline-runner-v2-clean",
            "head": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "merge_base": "cafebabecafebabecafebabecafebabecafebabe",
            "merge_base_ref": "origin/main",
            "ahead": 3,
            "behind": 0,
            "changed_files": [
                "src/research/phase_a_stop_report.py",
                "tests/test_phase_a_stop_report.py",
                "reports/refinement/baseline_2sym_a/LATEST.json",
            ],
        },
    )

    assert report.decision == "BLOCKED"
    assert any("coverage" in reason.lower() for reason in report.reasons)
    assert report.comparison.clean_manifest_raw_match is False
    assert report.comparison.clean_manifest_normalized_match is True
    assert report.comparison.clean_metrics_match is True
    assert report.comparison.resumed_manifest_normalized_match is True
    assert report.coverage_complete is False
    assert any(row["status"] == "missing" and row["symbol"] == "GBPUSD" for row in report.coverage_rows)
    text = report.to_markdown()
    assert "No strategy parameters were optimized." in text
    assert "GBPUSD" in text
    assert "BLOCKED" in text


def test_phase_a_stop_report_can_pass_with_complete_coverage(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_data_dir(data_dir, ["EURUSD", "GBPUSD", "XAUUSD"])

    clean_a_root = tmp_path / "clean_a"
    clean_b_root = tmp_path / "clean_b"
    resumed_root = tmp_path / "resumed"
    _write_run(clean_a_root, "20260720T190003Z-aaaa1111", "2026-07-20T19:00:03Z", "2026-07-20T19:00:03Z", ["EURUSD", "GBPUSD", "XAUUSD"], data_dir)
    _write_run(clean_b_root, "20260720T194014Z-bbbb2222", "2026-07-20T19:40:14Z", "2026-07-20T19:40:14Z", ["EURUSD", "GBPUSD", "XAUUSD"], data_dir)
    _write_run(resumed_root, "20260720T195500Z-cccc3333", "2026-07-20T19:55:00Z", "2026-07-20T19:55:00Z", ["EURUSD", "GBPUSD", "XAUUSD"], data_dir)

    report = build_phase_a_stop_report(
        clean_run_a=clean_a_root,
        clean_run_b=clean_b_root,
        resumed_run=resumed_root,
        data_dir=data_dir,
        suite_status="passed",
        ci_status="passed",
        ci_head="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        git_state={
            "branch": "research/st-c1-baseline-runner-v2-clean",
            "head": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "merge_base": "cafebabecafebabecafebabecafebabecafebabe",
            "merge_base_ref": "origin/main",
            "ahead": 3,
            "behind": 0,
            "changed_files": ["src/research/phase_a_stop_report.py", "tests/test_phase_a_stop_report.py"],
        },
    )

    assert report.decision == "PASS_FOR_BASELINE_REVIEW"
    assert report.coverage_complete is True
    assert all(row["status"] == "valid" for row in report.coverage_rows)
    assert report.comparison.clean_manifest_normalized_match is True
    assert report.comparison.clean_metrics_match is True
    assert report.comparison.resumed_metrics_match is True
    assert report.comparison.trade_reconciliation["gross_minus_cost_minus_net_r"] == pytest.approx(0.0)
    assert report.comparison.trade_reconciliation["component_minus_cost_drag_r"] == pytest.approx(0.0)


def test_phase_a_gate_writes_blocked_preflight_report_for_missing_data(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_data_dir(data_dir, ["EURUSD", "XAUUSD"])

    result = run_phase_a_gate(
        data_dir=data_dir,
        gate_root=tmp_path / "gate",
        cache_root=tmp_path / "cache",
        required_symbols=("EURUSD", "GBPUSD", "XAUUSD"),
        required_timeframes=("M5", "H1", "D1"),
        test_command="",
        ci_status="passed",
    )

    reports = list((tmp_path / "gate").glob("*/phase_a_stop_report.md"))
    assert result == 2
    assert len(reports) == 1
    text = reports[0].read_text(encoding="utf-8")
    assert "Decision: `BLOCKED`" in text
    assert "GBPUSD" in text
    assert "Baseline replay was not started" in text


def test_phase_a_gate_blocks_when_full_suite_fails(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_data_dir(data_dir, ["EURUSD", "GBPUSD", "XAUUSD"])

    result = run_phase_a_gate(
        data_dir=data_dir,
        gate_root=tmp_path / "gate",
        cache_root=tmp_path / "cache",
        required_symbols=("EURUSD", "GBPUSD", "XAUUSD"),
        required_timeframes=("M5", "H1", "D1"),
        test_command="python -m pytest tests/does_not_exist.py -q",
        focused_test_command="python --version",
        ci_status="passed",
        ci_head="not-the-current-head",
    )

    reports = list((tmp_path / "gate").glob("*/phase_a_stop_report.md"))
    assert result == 2
    assert len(reports) == 1
    text = reports[0].read_text(encoding="utf-8")
    assert "Focused tests status: `passed`" in text
    assert "Full suite status: `blocked`" in text
    assert "Baseline replay was not started" in text


def test_phase_a_gate_blocks_unknown_ci_before_baseline(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_data_dir(data_dir, ["EURUSD", "GBPUSD", "XAUUSD"])

    result = run_phase_a_gate(
        data_dir=data_dir,
        gate_root=tmp_path / "gate",
        cache_root=tmp_path / "cache",
        required_symbols=("EURUSD", "GBPUSD", "XAUUSD"),
        required_timeframes=("M5", "H1", "D1"),
        test_command="python --version",
        ci_status="unknown",
    )

    reports = list((tmp_path / "gate").glob("*/phase_a_stop_report.md"))
    assert result == 2
    assert len(reports) == 1
    assert not (reports[0].parent / "clean_a").exists()
    text = reports[0].read_text(encoding="utf-8")
    assert "Full suite status: `passed`" in text
    assert "CI status: `unknown`" in text
    assert "exact-HEAD CI evidence is required" in text
