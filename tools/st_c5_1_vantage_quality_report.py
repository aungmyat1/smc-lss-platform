#!/usr/bin/env python3
"""Generate ST-C5.1 Vantage MT5 data-quality and governance artifacts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from tools.st_c3_data_integrity import inspect_dataset
from tools.st_c5_broker_data_qualification import DEFAULT_CANDIDATE_DIR, GUARDRAIL
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS, EXPECTED_TIMEFRAMES, MANIFEST_NAME

REPORT_DIR = Path("reports/st_c5")
REQUIRED_FILES = [f"{symbol}_{timeframe}.csv" for symbol in sorted(EXPECTED_SYMBOLS) for timeframe in sorted(EXPECTED_TIMEFRAMES)]


def generate_vantage_quality_report(
    *,
    candidate_dir: str | Path = DEFAULT_CANDIDATE_DIR,
    report_dir: str | Path = REPORT_DIR,
) -> dict[str, Any]:
    candidate = Path(candidate_dir)
    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    inventory = build_data_inventory(candidate)
    normalization = build_normalization_report(candidate)
    integrity = build_integrity_summary(candidate)
    decision = governance_decision(inventory, normalization, integrity)
    manifest = dataset_manifest_payload(candidate, inventory, decision)

    (reports / "data_inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "DATASET_GOVERNANCE_DECISION.json").write_text(json.dumps(decision, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "normalization_report.md").write_text(_normalization_markdown(normalization), encoding="utf-8")
    (reports / "VANTAGE_DATA_QUALITY_REPORT.md").write_text(
        _quality_markdown(inventory, normalization, integrity, decision),
        encoding="utf-8",
    )
    return {
        "stage": "st_c5_1_vantage_quality_report",
        "status": "COMPLETE",
        "candidate_dir": str(candidate),
        "inventory": inventory,
        "normalization": normalization,
        "integrity": integrity,
        "decision": decision,
        "guardrail": GUARDRAIL,
    }


def build_data_inventory(candidate: Path) -> dict[str, Any]:
    files = []
    missing_files = []
    symbols: set[str] = set()
    timeframes: set[str] = set()
    first_values: list[str] = []
    last_values: list[str] = []
    for name in REQUIRED_FILES:
        path = candidate / name
        symbol, timeframe = name.removesuffix(".csv").split("_")
        if not path.exists():
            missing_files.append(name)
            continue
        stats = _csv_stats(path)
        symbols.add(symbol)
        timeframes.add(timeframe)
        if stats["first_timestamp"]:
            first_values.append(stats["first_timestamp"])
        if stats["last_timestamp"]:
            last_values.append(stats["last_timestamp"])
        files.append(
            {
                "file": name,
                "symbol": symbol,
                "timeframe": timeframe,
                "rows": stats["rows"],
                "first_timestamp": stats["first_timestamp"],
                "last_timestamp": stats["last_timestamp"],
                "checksum_sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "source": "Vantage MT5",
                "download_method": "MetaTrader5.copy_rates_range via tools.st_c3_download_mt5_dataset",
            }
        )
    return {
        "candidate_dir": str(candidate),
        "symbols": sorted(symbols),
        "timeframes": sorted(timeframes),
        "date_range": {
            "from": min(first_values) if first_values else None,
            "to": max(last_values) if last_values else None,
        },
        "files": files,
        "missing_files": missing_files,
        "account_environment": "local authenticated MT5 terminal; broker reported as Vantage MT5",
        "guardrail": GUARDRAIL,
    }


def build_normalization_report(candidate: Path) -> dict[str, Any]:
    rows = []
    for name in REQUIRED_FILES:
        path = candidate / name
        if not path.exists():
            rows.append({"file": name, "status": "MISSING"})
            continue
        rows.append(_normalization_stats(path))
    status = "PASS" if all(item.get("status") == "PASS" for item in rows) else "FAIL"
    return {
        "status": status,
        "schema": ["timestamp", "symbol", "open", "high", "low", "close", "volume", "spread", "source", "timezone", "session"],
        "timezone": "UTC",
        "source": "Vantage MT5",
        "files": rows,
    }


def build_integrity_summary(candidate: Path) -> dict[str, Any]:
    summaries = inspect_dataset(candidate)
    files = []
    total_missing = 0
    total_duplicates = 0
    issue_counts: Counter[str] = Counter()
    for item in summaries:
        issue_counts.update(issue.code for issue in item.issues)
        total_missing += len(item.missing_timestamps)
        total_duplicates += len(item.duplicate_timestamps)
        files.append(
            {
                "symbol": item.symbol,
                "timeframe": item.timeframe,
                "path": item.path,
                "status": item.status,
                "rows": item.rows,
                "first_timestamp": item.first_timestamp,
                "last_timestamp": item.last_timestamp,
                "missing_timestamps": len(item.missing_timestamps),
                "duplicate_timestamps": len(item.duplicate_timestamps),
                "issues": [issue.code for issue in item.issues],
                "first_missing_timestamp": item.missing_timestamps[0] if item.missing_timestamps else None,
            }
        )
    status = "PASS" if all(item["status"] == "PASS" for item in files) else "BLOCKED"
    return {
        "status": status,
        "total_missing_timestamps": total_missing,
        "total_duplicate_timestamps": total_duplicates,
        "issue_counts": dict(sorted(issue_counts.items())),
        "files": files,
    }


def governance_decision(inventory: dict[str, Any], normalization: dict[str, Any], integrity: dict[str, Any]) -> dict[str, Any]:
    blockers = []
    if inventory["missing_files"]:
        blockers.append("required files are missing")
    if normalization["status"] != "PASS":
        blockers.append("normalization validation failed")
    if integrity["status"] != "PASS":
        blockers.append("unchanged ST-C3 integrity inspection is blocked")
    if blockers:
        recommendation = "REJECT_DATASET"
        reason = "; ".join(blockers)
    else:
        recommendation = "REQUIRES_MANUAL_REVIEW"
        reason = "candidate inventory and preliminary integrity passed; full ST-C3 governance approval has not been executed"
    return {
        "decision": recommendation,
        "recommendation": recommendation,
        "dataset_status": "REJECTED" if recommendation == "REJECT_DATASET" else "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "strategy_validation_status": "BLOCKED",
        "demo_status": "BLOCKED",
        "live_status": "BLOCKED",
        "reason": reason,
        "st_c3_result": integrity["status"],
        "guardrail": GUARDRAIL,
    }


def dataset_manifest_payload(candidate: Path, inventory: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    manifest_path = candidate / MANIFEST_NAME
    source_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if not isinstance(source_manifest, dict):
        source_manifest = {}
    return {
        "strategy": "ST-C3",
        "source_manifest": str(manifest_path),
        "dataset_version": source_manifest.get("dataset_version", "ST-C5_Broker_MT5_Candidate_v0"),
        "provider": source_manifest.get("provider", "Vantage MT5"),
        "approved": False,
        "approval_status": decision["dataset_status"],
        "coverage": source_manifest.get("coverage", {}),
        "files": {
            item["file"]: {
                "symbol": item["symbol"],
                "timeframe": item["timeframe"],
                "rows": item["rows"],
                "first_timestamp": item["first_timestamp"],
                "last_timestamp": item["last_timestamp"],
                "sha256": item["checksum_sha256"],
            }
            for item in inventory["files"]
        },
        "guardrail": GUARDRAIL,
    }


def _csv_stats(path: Path) -> dict[str, Any]:
    rows = 0
    first = None
    last = None
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            value = row.get("time") or row.get("timestamp")
            if rows == 0:
                first = value
            last = value
            rows += 1
    return {"rows": rows, "first_timestamp": first, "last_timestamp": last}


def _normalization_stats(path: Path) -> dict[str, Any]:
    duplicates = 0
    ordering_errors = 0
    precision_errors = 0
    required = {"time", "open", "high", "low", "close", "volume", "session"}
    seen = set()
    previous = None
    columns = []
    rows = 0
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        for row in reader:
            ts = row["time"]
            try:
                parsed = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                if parsed.second != 0 or parsed.microsecond != 0:
                    precision_errors += 1
            except ValueError:
                precision_errors += 1
            if ts in seen:
                duplicates += 1
            if previous and ts <= previous:
                ordering_errors += 1
            seen.add(ts)
            previous = ts
            rows += 1
    missing_columns = sorted(required - set(columns))
    status = "PASS" if not missing_columns and duplicates == 0 and ordering_errors == 0 and precision_errors == 0 else "FAIL"
    return {
        "file": path.name,
        "status": status,
        "rows": rows,
        "missing_columns": missing_columns,
        "duplicates": duplicates,
        "ordering_errors": ordering_errors,
        "timestamp_precision_errors": precision_errors,
        "canonical_timezone": "UTC",
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalization_markdown(normalization: dict[str, Any]) -> str:
    lines = [
        "# ST-C5.1 Normalization Report",
        "",
        f"Status: **{normalization['status']}**",
        "",
        f"Canonical schema: `{normalization['schema']}`",
        "",
        "| File | Status | Rows | Duplicates | Ordering Errors | Timestamp Precision Errors |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for item in normalization["files"]:
        lines.append(
            f"| {item['file']} | {item['status']} | {item.get('rows', 0)} | {item.get('duplicates', 0)} | "
            f"{item.get('ordering_errors', 0)} | {item.get('timestamp_precision_errors', 0)} |"
        )
    return "\n".join(lines) + "\n"


def _quality_markdown(
    inventory: dict[str, Any],
    normalization: dict[str, Any],
    integrity: dict[str, Any],
    decision: dict[str, Any],
) -> str:
    return "\n".join(
        [
            "# ST-C5.1 Vantage MT5 Data Quality Report",
            "",
            f"Decision: **{decision['decision']}**",
            "",
            f"Reason: {decision['reason']}",
            "",
            "## Coverage",
            "",
            f"- Symbols: `{inventory['symbols']}`",
            f"- Timeframes: `{inventory['timeframes']}`",
            f"- Date range observed: `{inventory['date_range']}`",
            "",
            "## Integrity Metrics",
            "",
            f"- ST-C3 result: `{integrity['status']}`",
            f"- Missing timestamps: `{integrity['total_missing_timestamps']}`",
            f"- Duplicate timestamps: `{integrity['total_duplicate_timestamps']}`",
            f"- Issue counts: `{integrity['issue_counts']}`",
            "",
            "## Normalization",
            "",
            f"- Normalization status: `{normalization['status']}`",
            "- Timezone: `UTC`",
            "- Source: `Vantage MT5`",
            "",
            "## Risk Assessment",
            "",
            "The broker candidate cannot be approved because unchanged ST-C3 integrity inspection is blocked. Replay and downstream validation remain blocked.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    result = generate_vantage_quality_report(candidate_dir=args.candidate_dir, report_dir=args.report_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"]["decision"] == "APPROVE_DATASET" else 1)


if __name__ == "__main__":
    main()
