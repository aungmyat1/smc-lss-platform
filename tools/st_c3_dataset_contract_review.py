#!/usr/bin/env python3
"""Review ST-C3 Dataset Contract compatibility with zero-tick source minutes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

SOURCE_INTEGRITY_REPORT = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_INVESTIGATION.json")
AGGREGATION_REPORT = Path("reports/validation/st_c3/data_integrity/AGGREGATION_VALIDATION_REPORT.json")
STATISTICAL_REPORT = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.json")
OUTPUT_JSON = Path("reports/validation/st_c3/data_integrity/DATASET_CONTRACT_REVIEW.json")
OUTPUT_MD = Path("reports/validation/st_c3/data_integrity/DATASET_CONTRACT_REVIEW.md")
GUARDRAIL = "Dataset Contract Review does not change the contract, approve data, fill candles, or open replay."


def review_dataset_contract(
    *,
    contract_path: str | Path = Path("contracts/DATASET_CONTRACT.yaml"),
    source_report_path: str | Path = SOURCE_INTEGRITY_REPORT,
    aggregation_report_path: str | Path = AGGREGATION_REPORT,
    statistical_report_path: str | Path = STATISTICAL_REPORT,
    write_report: bool = True,
) -> dict[str, Any]:
    contract = _load_yaml(Path(contract_path))
    source_report = _load_json(Path(source_report_path))
    aggregation_report = _load_json(Path(aggregation_report_path))
    statistical_report = _load_json_if_exists(Path(statistical_report_path))
    zero_tick_probes = [
        item
        for item in (source_report.get("details") or {}).get("probes", [])
        if item.get("verdict") == "DUKASCOPY_AND_REFERENCE_ABSENT"
    ]
    aggregation_mismatches = _aggregation_mismatch_count(aggregation_report)
    missing_required = ((contract.get("checks") or {}).get("missing_timestamps") == "required")
    current_policy = (
        "strict_market_open_candle_continuity"
        if missing_required
        else "ambiguous_or_not_strict"
    )
    status = "BLOCKED"
    statistical_sufficient = bool((statistical_report.get("details") or {}).get("statistically_sufficient"))
    recommendation = "OPEN_GOVERNANCE_CHANGE_REQUEST" if statistical_sufficient else "CONTINUE_EVIDENCE_COLLECTION"
    result = {
        "stage": "dataset_contract_review",
        "status": status,
        "reason": _reason(missing_required, zero_tick_probes, aggregation_mismatches),
        "next_action": "Owner must decide contract policy for market-open zero-tick minutes before full dataset production.",
        "details": {
            "contract": str(contract_path),
            "dataset_version": contract.get("dataset_version"),
            "approval_status": contract.get("approval_status"),
            "replay_status": contract.get("replay_status"),
            "current_policy": current_policy,
            "missing_timestamps_check": (contract.get("checks") or {}).get("missing_timestamps"),
            "allowed_gap_policy": "weekend_and_fixed_holiday_only",
            "zero_tick_probe_count": len(zero_tick_probes),
            "zero_tick_probes": [
                {
                    "symbol": item.get("symbol"),
                    "timestamp_utc": item.get("timestamp_utc"),
                    "verdict": item.get("verdict"),
                    "fresh_dukascopy": (item.get("dukascopy_fresh") or {}).get("status"),
                    "histdata_present": (item.get("histdata_reference") or {}).get("present"),
                }
                for item in zero_tick_probes
            ],
            "aggregation_mismatch_count": aggregation_mismatches,
            "statistical_evidence": _statistical_summary(statistical_report),
            "options": _options(),
            "recommended_option": "collect_statistical_evidence_before_governance" if not statistical_sufficient else "contract_governance_review_before_acquisition",
        },
        "guardrail": GUARDRAIL,
        "recommendation": recommendation,
    }
    if write_report:
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        OUTPUT_MD.write_text(_markdown(result), encoding="utf-8")
    return result


def _reason(missing_required: bool, zero_tick_probes: list[dict[str, Any]], aggregation_mismatches: int) -> str:
    if aggregation_mismatches:
        return "aggregation mismatches remain; contract review cannot proceed to policy decision"
    if missing_required and zero_tick_probes:
        return "current contract requires missing timestamps to block approval, but source evidence shows market-open zero-tick minutes"
    if zero_tick_probes:
        return "source evidence shows zero-tick minutes and contract policy is ambiguous"
    return "no zero-tick source minute blocker found in current evidence"


def _aggregation_mismatch_count(report: dict[str, Any]) -> int:
    total = 0
    for symbol in (report.get("details") or {}).get("symbols", []):
        for timeframe in symbol.get("timeframes", []):
            total += int(timeframe.get("mismatch_count") or 0)
    return total


def _options() -> list[dict[str, str]]:
    return [
        {
            "id": "retain_strict_contract",
            "description": "Keep requiring every market-open timeframe candle. Dukascopy tick-derived data remains unsuitable unless a provider supplies complete bars.",
            "governance_impact": "no rule change",
        },
        {
            "id": "define_zero_tick_candle_policy",
            "description": "Open a governance change to define deterministic candles for zero-tick minutes, with explicit evidence and owner approval.",
            "governance_impact": "contract and validator change required",
        },
        {
            "id": "select_bar_provider",
            "description": "Use an authoritative M1/bar provider that emits complete zero-volume or carry-forward bars under a documented methodology.",
            "governance_impact": "provider qualification and dataset contract evidence required",
        },
    ]


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} must contain a mapping")
    return loaded


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} must contain an object")
    return loaded


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _load_json(path)


def _statistical_summary(report: dict[str, Any]) -> dict[str, Any]:
    details = report.get("details") or {}
    return {
        "present": bool(report),
        "statistically_sufficient": bool(details.get("statistically_sufficient")),
        "target_sample_days": details.get("target_sample_days"),
        "sample_days_cached_complete": details.get("sample_days_cached_complete"),
        "audited_cached_day_count": details.get("audited_cached_day_count"),
        "total_missing_minutes": details.get("total_missing_minutes"),
        "recommendation": details.get("recommendation"),
    }


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    lines = [
        "# ST-C3 Dataset Contract Review",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Current Contract Policy",
        "",
        f"- Dataset version: `{details['dataset_version']}`",
        f"- Approval status: `{details['approval_status']}`",
        f"- Replay status: `{details['replay_status']}`",
        f"- Missing timestamps check: `{details['missing_timestamps_check']}`",
        f"- Allowed gap policy: `{details['allowed_gap_policy']}`",
        "",
        "## Evidence",
        "",
        f"- Zero-tick probe count: `{details['zero_tick_probe_count']}`",
        f"- Aggregation mismatch count: `{details['aggregation_mismatch_count']}`",
        f"- Statistical evidence sufficient: `{details['statistical_evidence']['statistically_sufficient']}`",
        f"- Statistical audited cached days: `{details['statistical_evidence']['audited_cached_day_count']}`",
        f"- Statistical target cached days: `{details['statistical_evidence']['sample_days_cached_complete']}` of `{details['statistical_evidence']['target_sample_days']}`",
        "",
        "| Symbol | Timestamp | Verdict | Fresh Dukascopy | HistData Present |",
        "|---|---|---|---|---|",
    ]
    for item in details["zero_tick_probes"]:
        lines.append(
            f"| `{item['symbol']}` | `{item['timestamp_utc']}` | `{item['verdict']}` | "
            f"`{item['fresh_dukascopy']}` | `{item['histdata_present']}` |"
        )
    lines += ["", "## Options", ""]
    for option in details["options"]:
        lines.append(f"- `{option['id']}`: {option['description']} Governance impact: {option['governance_impact']}.")
    lines += [
        "",
        "## Required Decision",
        "",
        "Owner/governance must not change policy until the statistical source-integrity evidence gate is sufficient.",
        "No candles were fabricated, interpolated, or manually inserted.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=Path("contracts/DATASET_CONTRACT.yaml"))
    parser.add_argument("--source-report", type=Path, default=SOURCE_INTEGRITY_REPORT)
    parser.add_argument("--aggregation-report", type=Path, default=AGGREGATION_REPORT)
    parser.add_argument("--statistical-report", type=Path, default=STATISTICAL_REPORT)
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = review_dataset_contract(
        contract_path=args.contract,
        source_report_path=args.source_report,
        aggregation_report_path=args.aggregation_report,
        statistical_report_path=args.statistical_report,
        write_report=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
