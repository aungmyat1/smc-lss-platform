#!/usr/bin/env python3
"""ST-C5 broker-first data qualification workflow.

This workflow prepares and evaluates broker-native MT5 historical data as a
candidate source for a fresh ST-C3 validation run. It does not approve data,
unlock replay, run strategy validation, or modify ST-C3 thresholds.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from tools.st_c3_data_integrity import run_integrity_check
from tools.st_c3_download_mt5_dataset import download_st_c3_mt5_dataset
from validation.st_c3.dataset_loader import MANIFEST_NAME

REPORT_DIR = Path("reports/st_c5")
DEFAULT_CANDIDATE_DIR = Path("research_data/canonical/st_c5_vantage_mt5_candidate")
SOURCE_MANIFEST = Path("data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml")
GUARDRAIL = "ST-C5 broker-data qualification only; dataset approval, replay, strategy validation, demo, and live remain blocked."


def run_broker_data_qualification(
    *,
    candidate_dir: str | Path = DEFAULT_CANDIDATE_DIR,
    broker: str = "Vantage MT5",
    acquire: bool = False,
    write_reports: bool = True,
) -> dict[str, Any]:
    candidate = Path(candidate_dir)
    candidate.mkdir(parents=True, exist_ok=True)
    _ensure_layout(candidate)
    manifest_path = _ensure_candidate_manifest(candidate, broker=broker)
    preflight = _mt5_preflight()
    acquisition: dict[str, Any]
    integrity: dict[str, Any] | None = None

    if not acquire:
        acquisition = {
            "status": "BLOCKED",
            "reason": "acquisition not requested; run with --acquire on a machine with the broker MT5 terminal open and authenticated",
        }
        decision = _decision(acquisition, None)
    elif not preflight["package_available"]:
        acquisition = {"status": "BLOCKED", "reason": "MetaTrader5 package is not installed"}
        decision = _decision(acquisition, None)
    else:
        acquisition = download_st_c3_mt5_dataset(candidate, write_manifest=True)
        if acquisition.get("status") == "PASS":
            integrity = run_integrity_check(candidate, recover=False, write_reports=False)
        decision = _decision(acquisition, integrity)

    result = {
        "stage": "st_c5_broker_data_qualification",
        "status": "COMPLETE",
        "broker": broker,
        "candidate_dir": str(candidate),
        "manifest": str(manifest_path),
        "preflight": preflight,
        "acquisition": acquisition,
        "integrity": integrity,
        "decision": decision,
        "guardrail": GUARDRAIL,
    }
    if write_reports:
        _write_reports(result)
    return result


def _ensure_layout(candidate: Path) -> None:
    for path in [
        Path("research_data/raw/mt5/vantage"),
        Path("research_data/normalized/mt5/vantage"),
        candidate,
        Path("research_data/metadata"),
        REPORT_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if path.is_dir() and not keep.exists():
            keep.write_text("", encoding="utf-8")


def _ensure_candidate_manifest(candidate: Path, *, broker: str) -> Path:
    manifest_path = candidate / MANIFEST_NAME
    if manifest_path.exists():
        return manifest_path
    if SOURCE_MANIFEST.exists():
        manifest = yaml.safe_load(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    else:
        manifest = {}
    if not isinstance(manifest, dict):
        manifest = {}
    manifest.update(
        {
            "strategy": "ST-C3",
            "spec_version": "1.0.7",
            "dataset_version": "ST-C5_Broker_MT5_Candidate_v0",
            "approved": False,
            "approval_status": "NOT_APPROVED",
            "approval_date": "",
            "approved_by": "",
            "provider": broker,
            "source": "broker_native_mt5_export",
            "guardrail": GUARDRAIL,
        }
    )
    manifest.setdefault("symbols", ["EURUSD", "GBPUSD"])
    manifest.setdefault("timeframes", ["H4", "M15", "M3"])
    manifest.setdefault("coverage", {"from": "2021-01-01", "to": "2025-12-31"})
    manifest["files"] = {
        "EURUSD_H4.csv": {"sha256": "<pending>"},
        "EURUSD_M15.csv": {"sha256": "<pending>"},
        "EURUSD_M3.csv": {"sha256": "<pending>"},
        "GBPUSD_H4.csv": {"sha256": "<pending>"},
        "GBPUSD_M15.csv": {"sha256": "<pending>"},
        "GBPUSD_M3.csv": {"sha256": "<pending>"},
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return manifest_path


def _mt5_preflight() -> dict[str, Any]:
    try:
        import MetaTrader5 as mt5  # noqa: F401
    except ImportError:
        return {
            "package_available": False,
            "terminal_initialized": False,
            "reason": "MetaTrader5 package is not installed",
        }
    return {
        "package_available": True,
        "terminal_initialized": None,
        "reason": "MetaTrader5 package is installed; terminal initialization is attempted only during --acquire",
    }


def _decision(acquisition: dict[str, Any], integrity: dict[str, Any] | None) -> dict[str, Any]:
    if acquisition.get("status") != "PASS":
        return {
            "recommendation": "BROKER_DATA_PENDING",
            "dataset_status": "NOT_APPROVED",
            "replay_status": "BLOCKED",
            "strategy_validation_status": "BLOCKED",
            "reason": acquisition.get("reason", "broker data acquisition is incomplete"),
            "next_action": "Acquire broker MT5 candidate data, then rerun unchanged ST-C3 integrity and governance checks.",
        }
    if integrity and integrity.get("status") == "PASS":
        return {
            "recommendation": "READY_FOR_ST_C3",
            "dataset_status": "CANDIDATE_READY_NOT_APPROVED",
            "replay_status": "BLOCKED",
            "strategy_validation_status": "BLOCKED",
            "reason": "broker candidate acquired and preliminary integrity passed; run full unchanged ST-C3 before approval",
            "next_action": "Run the existing ST-C3 validation pipeline against the broker candidate dataset.",
        }
    return {
        "recommendation": "BROKER_DATA_REJECTED",
        "dataset_status": "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "strategy_validation_status": "BLOCKED",
        "reason": "broker candidate acquisition completed but preliminary integrity did not pass",
        "next_action": "Inspect integrity report and either repair reproducibly from broker source or move to paid provider fallback.",
    }


def _write_reports(result: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "MT5_PREFLIGHT_REPORT.json").write_text(json.dumps(result["preflight"], indent=2, sort_keys=True), encoding="utf-8")
    (REPORT_DIR / "BROKER_DATA_QUALIFICATION_STATUS.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (REPORT_DIR / "ST_C5_BROKER_FIRST_PLAN.md").write_text(_plan_markdown(result), encoding="utf-8")
    (REPORT_DIR / "BROKER_DATA_QUALIFICATION_REPORT.md").write_text(_qualification_markdown(result), encoding="utf-8")
    (REPORT_DIR / "PAID_PROVIDER_FALLBACK_PLAN.md").write_text(_fallback_markdown(), encoding="utf-8")
    (REPORT_DIR / "ST_C3_REVALIDATION_HANDOFF.md").write_text(_handoff_markdown(result), encoding="utf-8")
    (Path("research_data/metadata") / "ST_C5_BROKER_CANDIDATE.json").write_text(
        json.dumps(
            {
                "broker": result["broker"],
                "candidate_dir": result["candidate_dir"],
                "manifest": result["manifest"],
                "created_at_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "approval_status": result["decision"]["dataset_status"],
                "guardrail": GUARDRAIL,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _plan_markdown(result: dict[str, Any]) -> str:
    return f"""# ST-C5 Broker-First Data Qualification Plan

Objective: qualify broker-native MT5 history as the next candidate data source
without changing ST-C3, strategy logic, or validation thresholds.

Broker candidate: **{result['broker']}**

Candidate directory: `{result['candidate_dir']}`

Workflow:

1. Open and authenticate the broker MT5 terminal.
2. Run `python -m tools.st_c5_broker_data_qualification --acquire`.
3. Let the guarded MT5 downloader export EURUSD/GBPUSD H4/M15/M3.
4. Run preliminary integrity checks.
5. If candidate integrity passes, run the unchanged ST-C3 pipeline in a separate sprint.

Guardrail: {GUARDRAIL}
"""


def _qualification_markdown(result: dict[str, Any]) -> str:
    decision = result["decision"]
    return f"""# ST-C5 Broker Data Qualification Report

Broker: **{result['broker']}**

Decision: **{decision['recommendation']}**

Dataset Status: **{decision['dataset_status']}**

Replay Status: **{decision['replay_status']}**

Reason: {decision['reason']}

Acquisition status: `{result['acquisition']['status']}`

Preflight: `{result['preflight']['reason']}`
"""


def _fallback_markdown() -> str:
    return """# ST-C5 Paid Provider Fallback Plan

If broker MT5 data fails or cannot be exported reproducibly, evaluate paid/API
providers in this priority order:

1. Tiingo FX: configure `TIINGO_API_TOKEN`, approve license, acquire 100 deterministic EURUSD/GBPUSD days.
2. TrueFX: create account/subscription, document terms, acquire 100 deterministic tick days.
3. Darwinex: obtain FTP/live-account access and terms approval, acquire 100 deterministic tick days.

No paid provider may become canonical without passing unchanged ST-C3 evidence gates.
"""


def _handoff_markdown(result: dict[str, Any]) -> str:
    return f"""# ST-C5 to ST-C3 Revalidation Handoff

Current ST-C5 recommendation: **{result['decision']['recommendation']}**

Candidate manifest: `{result['manifest']}`

Run ST-C3 only if the ST-C5 decision is `READY_FOR_ST_C3`. Until then:

- Dataset remains not approved.
- Replay remains blocked.
- Strategy validation remains blocked.
- Demo/live remain blocked.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--broker", default="Vantage MT5")
    parser.add_argument("--acquire", action="store_true")
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = run_broker_data_qualification(
        candidate_dir=args.candidate_dir,
        broker=args.broker,
        acquire=args.acquire,
        write_reports=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"]["recommendation"] == "READY_FOR_ST_C3" else 1)


if __name__ == "__main__":
    main()
