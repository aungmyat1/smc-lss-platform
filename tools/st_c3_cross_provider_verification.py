#!/usr/bin/env python3
"""Generate the ST-C3 anomalous-timestamp cross-provider evidence report."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

SOURCE_REPORT = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.json")
REPORT_MD = Path("reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.md")
REPORT_JSON = Path("reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.json")
GUARDRAIL = "Cross-provider verification is evidence only; it never replaces Dukascopy data or changes governance gates."


def generate_cross_provider_verification(
    *,
    source_report: str | Path = SOURCE_REPORT,
    report_md: str | Path = REPORT_MD,
    report_json: str | Path = REPORT_JSON,
    write_report: bool = True,
) -> dict[str, Any]:
    source_path = Path(source_report)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    observations = source["details"].get("missing_observations") or []
    rows = [_row(item) for item in observations]
    summary = _summary(rows)
    result = {
        "stage": "cross_provider_verification",
        "status": "BLOCKED",
        "reason": "source-integrity evidence sample is not complete; cross-provider findings are interim",
        "next_action": "Continue deterministic evidence collection before provider decision.",
        "recommendation": "CONTINUE_EVIDENCE_COLLECTION",
        "guardrail": GUARDRAIL,
        "details": {
            "source_report": str(source_path),
            "source_status": source.get("status"),
            "source_recommendation": source["details"].get("recommendation"),
            "observations": len(rows),
            "summary": summary,
            "rows": rows,
        },
    }
    if write_report:
        md_path = Path(report_md)
        json_path = Path(report_json)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(_markdown(result), encoding="utf-8")
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def _row(item: dict[str, Any]) -> dict[str, Any]:
    reference = item.get("cross_source_reference") or {}
    present = reference.get("present")
    if reference.get("checked") is not True:
        conclusion = "REFERENCE_NOT_CHECKED"
        reference_result = reference.get("reason", "not checked")
    elif present is True:
        conclusion = "DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT"
        reference_result = "timestamp present"
    elif present is False:
        conclusion = "DUKASCOPY_AND_REFERENCE_ABSENT"
        reference_result = "timestamp absent"
    else:
        conclusion = "REFERENCE_INDETERMINATE"
        reference_result = reference.get("reason", "indeterminate")
    return {
        "timestamp_utc": item["timestamp_utc"],
        "symbol": item["symbol"],
        "session": item["session"],
        "weekday": item["weekday"],
        "root_cause_category": item["root_cause_category"],
        "dukascopy_result": "zero ticks in reconstructed M1 source minute",
        "reference_provider": reference.get("provider", "UNKNOWN"),
        "reference_result": reference_result,
        "conclusion": conclusion,
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_conclusion": _counter(row["conclusion"] for row in rows),
        "by_symbol": _counter(row["symbol"] for row in rows),
        "by_session": _counter(row["session"] for row in rows),
        "by_root_cause_category": _counter(row["root_cause_category"] for row in rows),
    }


def _counter(values: Any) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    summary = details["summary"]
    lines = [
        "# ST-C3 Cross-Provider Verification Report",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Summary",
        "",
        f"- Source report: `{details['source_report']}`",
        f"- Source status: `{details['source_status']}`",
        f"- Observations checked: `{details['observations']}`",
        f"- By conclusion: `{summary['by_conclusion']}`",
        f"- By symbol: `{summary['by_symbol']}`",
        f"- By session: `{summary['by_session']}`",
        f"- By root-cause category: `{summary['by_root_cause_category']}`",
        "",
        "## Findings",
        "",
        "| Timestamp UTC | Symbol | Dukascopy Result | Reference Source Result | Conclusion |",
        "|---|---|---|---|---|",
    ]
    for row in details["rows"]:
        lines.append(
            f"| `{row['timestamp_utc']}` | `{row['symbol']}` | {row['dukascopy_result']} | "
            f"`{row['reference_provider']}`: {row['reference_result']} | `{row['conclusion']}` |"
        )
    lines += [
        "",
        "## Decision",
        "",
        "This interim report does not accept or reject Dukascopy because the deterministic source-integrity evidence sample is incomplete.",
        "No Dukascopy data was replaced with reference-provider data.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    result = generate_cross_provider_verification()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
