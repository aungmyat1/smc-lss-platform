from __future__ import annotations

import json
import subprocess
import sys

import pytest

from validation.st_c3.owner_packet_generator import build_owner_packet
from validation.st_c3.replay_engine import (
    build_ledger,
    read_ledger_hash,
    verify_ledger_hash,
    write_ledger,
    write_ledger_hash,
    TradeRecord,
)
from validation.st_c3.robustness_engine import run_robustness_matrix
from validation.st_c3.stats_engine import compute_stats_from_ledger
from validation.st_c3.walkforward_engine import run_fixed_year_walkforward


def _trade(
    trade_id: str,
    year: int,
    r: float,
    *,
    symbol: str = "GBPUSD",
    session: str = "LONDON",
) -> TradeRecord:
    return TradeRecord(
        id=trade_id,
        symbol=symbol,
        timestamp_entry=f"{year}-01-02T08:00:00Z",
        timestamp_exit=f"{year}-01-02T09:00:00Z",
        direction="LONG",
        entry_price=1.1000,
        exit_price=1.1010,
        size=1.0,
        r=r,
        mae_r=-0.2,
        mfe_r=max(r, 0.0) + 0.2,
        session=session,
        news_flag=False,
        rationale="synthetic deterministic replay fixture",
        win_loss="win" if r > 0 else "loss",
        chain_id=f"chain-{trade_id}",
        tags=("synthetic",),
    )


def test_replay_ledger_writes_byte_stable_hash(tmp_path):
    trades = [_trade("b", 2025, -1.0), _trade("a", 2024, 2.0)]
    ledger = build_ledger(trades, {"strategy_id": "ST-C3", "version": "1.0.7"})
    first = write_ledger(ledger, tmp_path / "ledger.json")
    first_hash = write_ledger_hash(first, tmp_path / "ledger.hash")

    second = write_ledger(ledger, tmp_path / "ledger_again.json")
    second_hash = write_ledger_hash(second, tmp_path / "ledger_again.hash")

    assert first.read_bytes() == second.read_bytes()
    assert first_hash == second_hash
    assert verify_ledger_hash(first, tmp_path / "ledger.hash") == first_hash
    data = json.loads(first.read_text(encoding="utf-8"))
    assert [trade["id"] for trade in data["trades"]] == ["a", "b"]


def test_stats_engine_requires_matching_hash_and_references_it(tmp_path):
    ledger_path, hash_path = _write_profitable_ledger(tmp_path)
    result = compute_stats_from_ledger(ledger_path, hash_path)

    assert result.ledger_sha256 == read_ledger_hash(hash_path)
    assert result.metrics["total_trades"] == 6
    assert result.threshold_results["profit_factor"] is True

    hash_path.write_text("st_c3_ledger_sha256=" + ("0" * 64) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="ledger hash mismatch"):
        compute_stats_from_ledger(ledger_path, hash_path)


def test_robustness_matrix_runs_from_same_immutable_hash(tmp_path):
    ledger_path, hash_path = _write_profitable_ledger(tmp_path)
    matrix = run_robustness_matrix(
        ledger_path,
        hash_path,
        "validation/st_c3/robustness_thresholds.yaml",
        max_workers=2,
    )

    assert matrix["ledger_sha256"] == read_ledger_hash(hash_path)
    assert {item["ledger_sha256"] for item in matrix["scenario_results"]} == {matrix["ledger_sha256"]}
    assert "spread_x2" in {item["scenario"] for item in matrix["scenario_results"]}


def test_walkforward_uses_fixed_year_windows_and_pass_criteria(tmp_path):
    ledger_path, hash_path = _write_profitable_ledger(tmp_path)
    result = run_fixed_year_walkforward(ledger_path, hash_path)

    assert result["ledger_sha256"] == read_ledger_hash(hash_path)
    assert result["window_method"] == "fixed_year_slices"
    assert result["status"] == "PASS"
    assert [window["window"] for window in result["windows"]] == ["2024", "2025", "2026"]


def test_owner_packet_preserves_guardrail(tmp_path):
    _, hash_path = _write_profitable_ledger(tmp_path)
    packet = build_owner_packet(
        ledger_hash_path=hash_path,
        stats_summary_path=None,
        robustness_matrix_path=None,
        walkforward_results_path=None,
        recommendation="defer",
    )

    assert packet["ledger_sha256"] == read_ledger_hash(hash_path)
    assert packet["recommendation"] == "defer"
    assert "Does not accept S1-G5 or S1-G6" in packet["guardrail"]


def test_run_replay_refuses_non_frozen_spec():
    from validation.st_c3.replay_engine import run_replay

    with pytest.raises(ValueError, match="locked to frozen spec version 1.0.7"):
        run_replay(
            spec_version="1.0.6",
            symbols=["GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            sample=True,
        )


def test_ultra_fast_pipeline_cli_sample_mode_writes_linked_outputs(tmp_path):
    out_dir = tmp_path / "replay"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "validation.st_c3.run_ultra_fast_pipeline",
            "--sample",
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASS"
    assert "does not mark S1-G5/S1-G6 accepted" in payload["guardrail"]
    ledger_hash = read_ledger_hash(out_dir / "ledger.hash")
    assert json.loads((out_dir / "stats_summary.json").read_text(encoding="utf-8"))["ledger_sha256"] == ledger_hash
    assert json.loads((out_dir / "robustness_matrix.json").read_text(encoding="utf-8"))["ledger_sha256"] == ledger_hash
    assert json.loads((out_dir / "walkforward_results.json").read_text(encoding="utf-8"))["ledger_sha256"] == ledger_hash
    packet = json.loads((out_dir / "OWNER_DECISION_PACKET_ST_C3_A2.json").read_text(encoding="utf-8"))
    assert packet["ledger_sha256"] == ledger_hash
    assert "Does not accept S1-G5 or S1-G6" in packet["guardrail"]


def _write_profitable_ledger(tmp_path):
    trades = [
        _trade("2024-a", 2024, 2.0),
        _trade("2024-b", 2024, -0.5),
        _trade("2025-a", 2025, 2.5, symbol="EURUSD", session="NY"),
        _trade("2025-b", 2025, -0.5, symbol="EURUSD", session="NY"),
        _trade("2026-a", 2026, 2.0),
        _trade("2026-b", 2026, -0.4),
    ]
    ledger = build_ledger(trades, {"strategy_id": "ST-C3", "version": "1.0.7"})
    ledger_path = write_ledger(ledger, tmp_path / "ledger.json")
    hash_path = tmp_path / "ledger.hash"
    write_ledger_hash(ledger_path, hash_path)
    return ledger_path, hash_path
