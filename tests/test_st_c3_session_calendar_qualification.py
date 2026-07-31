from __future__ import annotations

import json
from pathlib import Path

from tools.st_c3_session_calendar_qualification import generate_session_calendar_qualification


def test_session_calendar_qualification_reports_provider_compatibility(tmp_path: Path):
    friday = tmp_path / "friday.json"
    friday.write_text(
        json.dumps(
            {
                "details": {
                    "classification": {"root_cause": "DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH"},
                    "summary": {"by_weekday_hour_status": {"Friday 21:00 EMPTY_PAYLOAD": 2}},
                }
            }
        ),
        encoding="utf-8",
    )
    cross = tmp_path / "cross.json"
    cross.write_text(
        json.dumps(
            {
                "details": {
                    "summary": {
                        "by_conclusion": {
                            "DUKASCOPY_AND_REFERENCE_ABSENT": 1,
                            "DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT": 2,
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = generate_session_calendar_qualification(
        friday_report=friday,
        cross_provider_report=cross,
        report_json=tmp_path / "report.json",
        report_md=tmp_path / "report.md",
    )

    assert result["status"] == "BLOCKED"
    assert result["recommendation"] == "CONTINUE_EVIDENCE_COLLECTION"
    dukascopy = result["details"]["profiles"]["Dukascopy"]
    assert dukascopy["session_boundary_conventions"] == "DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH"
    assert "session mismatch" in dukascopy["compatibility_assessment"]
    assert (tmp_path / "report.md").exists()
