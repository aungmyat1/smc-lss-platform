from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta

import pytest
import yaml

from validation.st_c3.owner_packet_generator import build_owner_packet
from tools.st_c3_diff_owner_packet import diff_owner_packets
from tools.st_c3_prepare_dataset_manifest import prepare_dataset_manifest
from validation.st_c3.replay_engine import (
    build_ledger,
    read_ledger_hash,
    run_replay,
    verify_ledger_hash,
    write_ledger,
    write_ledger_hash,
    TradeRecord,
)
from validation.st_c3.dataset_loader import sha256_file
from validation.st_c3.replay_repro_auditor import audit_replay_reproducibility, run_and_audit_replay
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


def test_owner_packet_diff_reports_high_signal_changes(tmp_path):
    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    old_path.write_text(json.dumps({"ledger_sha256": "a", "recommendation": "defer"}), encoding="utf-8")
    new_path.write_text(json.dumps({"ledger_sha256": "b", "recommendation": "reject"}), encoding="utf-8")

    diff = diff_owner_packets(old_path, new_path)

    assert diff["changed"] is True
    assert {item["field"] for item in diff["changes"]} == {"ledger_sha256", "recommendation"}
    assert "Does not accept gates" in diff["guardrail"]


def test_replay_reproducibility_auditor_compares_hash_and_trade_ids(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    ledger = build_ledger([_trade("same", 2024, 1.0)], {"strategy_id": "ST-C3", "version": "1.0.7"})
    first_ledger = write_ledger(ledger, first / "ledger.json")
    second_ledger = write_ledger(ledger, second / "ledger.json")
    write_ledger_hash(first_ledger, first / "ledger.hash")
    write_ledger_hash(second_ledger, second / "ledger.hash")

    audit = audit_replay_reproducibility(first, second)

    assert audit["status"] == "PASS"
    assert audit["hash_match"] is True
    assert audit["trade_ids_match"] is True


def test_replay_reproducibility_auditor_can_run_sample_replay_twice(tmp_path):
    audit = run_and_audit_replay(
        first_dir=tmp_path / "first",
        second_dir=tmp_path / "second",
        sample=True,
    )

    assert audit["status"] == "PASS"
    assert audit["hash_match"] is True
    assert audit["trade_count_match"] is True


def test_run_replay_refuses_non_frozen_spec():
    with pytest.raises(ValueError, match="locked to frozen spec version 1.0.7"):
        run_replay(
            spec_version="1.0.6",
            symbols=["GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            sample=True,
        )


def test_run_replay_with_unapproved_data_manifest_refuses_to_run(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=False)

    with pytest.raises(ValueError, match="not approved"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_approved_data_validates_dataset_without_simulating_trades(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True)
    ledger = run_replay(
        spec_version="1.0.7",
        symbols=["EURUSD", "GBPUSD"],
        date_from="2024-01-01",
        date_to="2024-01-31",
        tf_set=["H4", "M15", "M3"],
        data_dir=data_dir,
    )
    data = ledger.to_dict()

    assert data["meta"]["dataset_approved"] is True
    assert data["meta"]["trade_generation_status"] == "blocked_until_owner_authorizes_A3_replay"
    assert len(data["meta"]["dataset_files"]) == 6
    assert data["trades"] == []


def test_run_replay_with_hash_mismatch_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True)
    manifest_path = data_dir / "DATASET_MANIFEST_ST_C3.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][0]["sha256"] = "0" * 64
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="sha256 mismatch"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_missing_candle_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, missing_candle=True)

    with pytest.raises(ValueError, match="missing or irregular candle"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_wrong_symbol_set_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, symbols=("GBPUSD",))

    with pytest.raises(ValueError, match="manifest symbols must be exactly"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_missing_sessions_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, omit_sessions=True)

    with pytest.raises(ValueError, match="missing required fields: \\['sessions'\\]"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_missing_symbol_metadata_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, omit_symbol_metadata=True)

    with pytest.raises(ValueError, match="missing required fields: \\['symbol_metadata'\\]"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_invalid_session_window_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, session_override={"london": {"start": "08:00"}})

    with pytest.raises(ValueError, match="sessions.london.start must be 07:00"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_with_invalid_symbol_metadata_blocks(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, metadata_override={"GBPUSD": {"lot_size": 1000}})

    with pytest.raises(ValueError, match="symbol metadata for GBPUSD.lot_size must be 100000"):
        run_replay(
            spec_version="1.0.7",
            symbols=["EURUSD", "GBPUSD"],
            date_from="2024-01-01",
            date_to="2024-01-31",
            tf_set=["H4", "M15", "M3"],
            data_dir=data_dir,
        )


def test_run_replay_accepts_filename_keyed_files_manifest(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True, files_as_mapping=True)
    ledger = run_replay(
        spec_version="1.0.7",
        symbols=["EURUSD", "GBPUSD"],
        date_from="2024-01-01",
        date_to="2024-01-31",
        tf_set=["H4", "M15", "M3"],
        data_dir=data_dir,
    )

    assert len(ledger.to_dict()["meta"]["dataset_files"]) == 6


def test_prepare_dataset_manifest_computes_and_writes_hashes(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True)
    manifest_path = data_dir / "DATASET_MANIFEST_ST_C3.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["files"] = {
        item["path"]: {"sha256": "<hash>"}
        for item in manifest["files"]
    }
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    result = prepare_dataset_manifest(data_dir, write=True)
    updated = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert result["status"] == "PASS"
    assert all(item["sha256"] != "<hash>" for item in result["files"])
    assert all(value["sha256"] != "<hash>" for value in updated["files"].values())


def test_prepare_dataset_manifest_blocks_when_csv_missing(tmp_path):
    data_dir = _write_dataset_dir(tmp_path, approved=True)
    (data_dir / "EURUSD_H4.csv").unlink()

    result = prepare_dataset_manifest(data_dir, write=True)

    assert result["status"] == "BLOCKED"
    assert "dataset file missing" in result["reason"]


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


def test_replay_cli_reports_blocked_when_approved_manifest_missing(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "validation.st_c3.run_st_c3_replay",
            "--data",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 2
    assert payload["status"] == "BLOCKED"
    assert "missing ST-C3 dataset manifest" in payload["reason"]


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


def _write_dataset_dir(
    tmp_path,
    *,
    approved: bool,
    symbols=("EURUSD", "GBPUSD"),
    missing_candle: bool = False,
    files_as_mapping: bool = False,
    omit_sessions: bool = False,
    omit_symbol_metadata: bool = False,
    session_override: dict | None = None,
    metadata_override: dict | None = None,
):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    files = []
    deltas = {"H4": timedelta(hours=4), "M15": timedelta(minutes=15), "M3": timedelta(minutes=3)}
    for symbol in symbols:
        for timeframe, delta in deltas.items():
            path = data_dir / f"{symbol}_{timeframe}.csv"
            start = datetime(2024, 1, 1, 0, 0)
            second = start + (delta * 2 if missing_candle and symbol == "EURUSD" and timeframe == "M15" else delta)
            path.write_text(
                "time,open,high,low,close,volume,session,news_flag\n"
                f"{start.isoformat()}Z,1.1000,1.1010,1.0990,1.1005,100,LONDON,false\n"
                f"{second.isoformat()}Z,1.1005,1.1020,1.1000,1.1015,120,NY,true\n",
                encoding="utf-8",
            )
            files.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "path": path.name,
                    "sha256": sha256_file(path),
                }
            )
    sessions = {
        "london": {"start": "07:00", "end": "10:00"},
        "new_york": {"start": "13:00", "end": "16:00"},
    }
    if session_override:
        for key, value in session_override.items():
            sessions.setdefault(key, {}).update(value)
    symbol_metadata = {
        symbol: {"pip_size": 0.0001, "min_tick": 0.00001, "lot_size": 100000}
        for symbol in symbols
    }
    if metadata_override:
        for symbol, fields in metadata_override.items():
            symbol_metadata.setdefault(symbol, {}).update(fields)
    manifest = {
        "strategy": "ST-C3",
        "spec_version": "1.0.7",
        "approved": approved,
        "approval_status": "APPROVED" if approved else "PENDING",
        "approval_date": "2026-07-29",
        "approved_by": "TEST_OWNER",
        "symbols": list(symbols),
        "timeframes": ["H4", "M15", "M3"],
        "coverage": {"from": "2024-01-01", "to": "2024-01-31"},
        "files": {
            item["path"]: {"sha256": item["sha256"]}
            for item in files
        } if files_as_mapping else files,
    }
    if not omit_sessions:
        manifest["sessions"] = sessions
    if not omit_symbol_metadata:
        manifest["symbol_metadata"] = symbol_metadata
    (data_dir / "DATASET_MANIFEST_ST_C3.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return data_dir
