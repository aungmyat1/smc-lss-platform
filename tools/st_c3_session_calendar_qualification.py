#!/usr/bin/env python3
"""Generate ST-C3 provider session-calendar qualification evidence.

This report compares provider session behavior with the current ST-C3 Dataset
Contract assumptions. It does not change the contract, validators, approval
state, replay state, or historical prices.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FRIDAY_REPORT = Path("reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.json")
CROSS_PROVIDER_REPORT = Path("reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.json")
REPORT_JSON = Path("reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.json")
REPORT_MD = Path("reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.md")
GUARDRAIL = "Session calendar qualification is evidence only; it does not change ST-C3 contracts, validators, approval, replay, or prices."

SOURCES = {
    "st_c3_contract": "contracts/DATASET_CONTRACT.yaml and validation/st_c3/dataset_loader.py",
    "dukascopy_dst": "https://www.dukascopy.com/swiss/english/about/ournews/daylight-saving-time-2025-in-the-us",
    "dukascopy_hours": "https://www.dukascopy.com/swiss/english/fx-market-tools/forex-market-hours/",
    "histdata_timezone": "https://www.histdata.com/f-a-q/",
}


def generate_session_calendar_qualification(
    *,
    friday_report: str | Path = FRIDAY_REPORT,
    cross_provider_report: str | Path = CROSS_PROVIDER_REPORT,
    report_json: str | Path = REPORT_JSON,
    report_md: str | Path = REPORT_MD,
    write_report: bool = True,
) -> dict[str, Any]:
    friday = _load_json(Path(friday_report))
    cross_provider = _load_json(Path(cross_provider_report))
    profiles = _profiles(friday, cross_provider)
    result = {
        "stage": "session_calendar_qualification",
        "status": "BLOCKED",
        "reason": "session-calendar compatibility is not yet qualified; source-integrity sample remains incomplete",
        "next_action": "Continue evidence collection and perform governed calendar/source-policy review before provider decision.",
        "recommendation": "CONTINUE_EVIDENCE_COLLECTION",
        "guardrail": GUARDRAIL,
        "details": {
            "research_question": "Which provider's trading calendar matches the assumptions encoded in the ST-C3 Dataset Contract?",
            "sources": SOURCES,
            "profiles": profiles,
            "comparison_matrix": _comparison_matrix(profiles),
            "decision_layer": {
                "data_completeness": "not final until 100-day deterministic source-integrity sample completes",
                "session_compatibility": "not final until provider calendars are reviewed against ST-C3 replay assumptions",
                "provider_freeze_rule": "after provider selection, use one canonical data source and session calendar for all ST-C3 v1.x validation stages",
            },
        },
    }
    if write_report:
        json_path = Path(report_json)
        md_path = Path(report_md)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(_markdown(result), encoding="utf-8")
    return result


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _profiles(friday: dict[str, Any], cross_provider: dict[str, Any]) -> dict[str, dict[str, Any]]:
    friday_details = friday.get("details") or {}
    friday_summary = friday_details.get("summary") or {}
    friday_classification = friday_details.get("classification") or {}
    cross_summary = ((cross_provider.get("details") or {}).get("summary") or {})
    return {
        "ST-C3 Dataset Contract": {
            "basis": "contract/loader",
            "trading_week_close_utc": "Friday 22:00 UTC year-round by current loader",
            "dst_behavior": "no DST adjustment encoded",
            "daily_rollover_time": "22:00 UTC treated as rollover evidence bucket in source-integrity tooling",
            "holiday_handling": "weekends plus fixed Jan 1 and Dec 25 closures",
            "expected_zero_tick_periods": "weekend/fixed-holiday closure only; market-open missing timestamps block approval",
            "bar_generation_policy": "all required fixed-timeframe candles must exist; no fabrication/interpolation",
            "session_boundary_conventions": "UTC-only fixed boundaries",
            "compatibility_assessment": "baseline contract, not a provider",
        },
        "Dukascopy": {
            "basis": "official DST notice plus live probes",
            "trading_week_close_utc": "observed Friday 22:00 UTC in winter and Friday 21:00 UTC during DST",
            "dst_behavior": "official Dukascopy notice says FX trading day/opening/settlement changes from 22:00 GMT to 21:00 GMT during US DST",
            "daily_rollover_time": "provider opening/settlement shifts with US DST per official notice",
            "holiday_handling": "not fully qualified for ST-C3 sample",
            "expected_zero_tick_periods": friday_summary.get("by_weekday_hour_status", {}),
            "bar_generation_policy": "tick source; zero-byte source hours observed at DST Friday 21:00 UTC",
            "session_boundary_conventions": friday_classification.get("root_cause", "UNRESOLVED"),
            "compatibility_assessment": "session mismatch with current fixed-UTC ST-C3 Friday close assumption",
        },
        "HistData": {
            "basis": "FAQ plus cached M1 reference comparison",
            "trading_week_close_utc": "cached reference shows many DST Friday 21:00 UTC rows and zero Friday 22:00 UTC rows in the focused probes",
            "dst_behavior": "official FAQ says CSV timestamps use EST without daylight-saving adjustments",
            "daily_rollover_time": "not fully qualified for ST-C3 sample",
            "holiday_handling": "not fully qualified for ST-C3 sample",
            "expected_zero_tick_periods": cross_summary.get("by_conclusion", {}),
            "bar_generation_policy": "M1 bar files; methodology for zero-volume/carry-forward bars remains unqualified",
            "session_boundary_conventions": "fixed EST timestamp convention converted to UTC in current reference tooling",
            "compatibility_assessment": "closer to current fixed Friday 22:00 UTC assumption for probed DST Friday close, but full suitability remains unqualified",
        },
    }


def _comparison_matrix(profiles: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    fields = [
        "trading_week_close_utc",
        "dst_behavior",
        "daily_rollover_time",
        "holiday_handling",
        "expected_zero_tick_periods",
        "bar_generation_policy",
        "session_boundary_conventions",
        "compatibility_assessment",
    ]
    return [
        {
            "criterion": field,
            **{provider: str(profile[field]) for provider, profile in profiles.items()},
        }
        for field in fields
    ]


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    profiles = details["profiles"]
    lines = [
        "# ST-C3 Session Calendar Qualification Report",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Research Question",
        "",
        details["research_question"],
        "",
        "## Sources",
        "",
        f"- ST-C3 contract/loader: `{details['sources']['st_c3_contract']}`",
        f"- Dukascopy DST notice: {details['sources']['dukascopy_dst']}",
        f"- Dukascopy FX market hours: {details['sources']['dukascopy_hours']}",
        f"- HistData timezone FAQ: {details['sources']['histdata_timezone']}",
        "",
        "## Provider Profiles",
        "",
    ]
    for provider, profile in profiles.items():
        lines += [
            f"### {provider}",
            "",
            f"- Basis: {profile['basis']}",
            f"- Trading week close UTC: {profile['trading_week_close_utc']}",
            f"- DST behavior: {profile['dst_behavior']}",
            f"- Daily rollover time: {profile['daily_rollover_time']}",
            f"- Holiday handling: {profile['holiday_handling']}",
            f"- Expected zero-tick periods: `{profile['expected_zero_tick_periods']}`",
            f"- Bar-generation policy: {profile['bar_generation_policy']}",
            f"- Session-boundary conventions: {profile['session_boundary_conventions']}",
            f"- Compatibility assessment: {profile['compatibility_assessment']}",
            "",
        ]
    lines += [
        "## Comparison Matrix",
        "",
        "| Criterion | ST-C3 Dataset Contract | Dukascopy | HistData |",
        "|---|---|---|---|",
    ]
    for row in details["comparison_matrix"]:
        lines.append(
            f"| `{row['criterion']}` | {row['ST-C3 Dataset Contract']} | {row['Dukascopy']} | {row['HistData']} |"
        )
    lines += [
        "",
        "## Decision Layer",
        "",
        f"- Data completeness: {details['decision_layer']['data_completeness']}",
        f"- Session compatibility: {details['decision_layer']['session_compatibility']}",
        f"- Provider freeze rule: {details['decision_layer']['provider_freeze_rule']}",
        "",
        "## Decision",
        "",
        "No provider is accepted or rejected by this report. The Dataset Contract remains unchanged, dataset approval remains blocked, and replay remains blocked.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    result = generate_session_calendar_qualification()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
