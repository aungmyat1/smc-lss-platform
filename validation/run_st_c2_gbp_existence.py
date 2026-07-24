"""Run the ST-C2 v1.2 GBPUSD existence-check preflight.

This is Stage 1 research tooling only. It writes a Markdown report and never
imports broker/MT5 execution paths.
"""
from __future__ import annotations

from pathlib import Path

from validation.st_c2_reference import REQUIRED_DATA, data_availability, missing_data, scan_history


REPORT_PATH = Path("reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md")


def build_report() -> str:
    availability = data_availability()
    missing = missing_data()
    scan = None if missing else scan_history()
    lines = [
        "# ST-C2 v1.2 GBPUSD Existence Check",
        "",
        "**Scope:** S1-G2 reference implementation existence scan for frozen `specs/st-c2_v1.2.0.yaml`.",
        "",
        "## Data Availability",
        "",
    ]
    for key, path in REQUIRED_DATA.items():
        status = "present" if availability[key] else "missing"
        lines.append(f"- {key}: `{path}` - {status}")
    lines += [
        "",
        "## Verdict",
        "",
    ]
    if missing:
        lines += [
            "**BLOCKED_DATA_MISSING**",
            "",
            "The GBPUSD existence-check run cannot produce valid strategy evidence because the frozen ST-C2 timeframe triple requires H4/M15/M3 data and at least one required file is missing.",
            "",
            f"Missing timeframes: `{', '.join(missing)}`",
            "",
            "No proxy timeframe substitution was used. In particular, M5 was not treated as M3.",
        ]
    else:
        lines += [
            f"**{scan.decision}**",
            "",
            f"Checked windows: `{scan.checked_windows}`",
            "",
        ]
        if scan.first_signal is not None:
            lines += [
                f"First signal time: `{scan.first_signal.signal_time}`",
                f"Direction: `{scan.first_signal.direction}`",
                "",
                "The S1-G2 minimum existence floor (`>=1`) is satisfied by the reference scan.",
            ]
        else:
            lines += [
                "No qualifying GBPUSD signal was found by the current reference scan.",
                "",
                "Rejection counts:",
                "",
            ]
            for code, count in sorted(scan.rejection_counts.items()):
                lines.append(f"- `{code}`: {count}")
    lines += [
        "",
        "## Data Provenance",
        "",
        "- `data/GBPUSD_H4.csv`: exported from the local MT5 terminal via `src/load_history.py`.",
        "- `data/GBPUSD_M15.csv`: exported from the local MT5 terminal via `src/load_history.py`.",
        "- `data/GBPUSD_M3.csv`: derived from complete contiguous `GBPUSD_M1` groups because the terminal rejected native `TIMEFRAME_M3` with invalid params.",
        "- Temporary `GBPUSD_M1.csv` and `GBPUSD_M30.csv` helper files were removed after derivation.",
        "",
        "## Authorization Boundary",
        "",
        "This report does not authorize execution, demo trading, live trading, broker integration, or production promotion.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(REPORT_PATH)


if __name__ == "__main__":
    print(build_report())
