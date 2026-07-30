from __future__ import annotations

import json
from pathlib import Path

from tools.st_c3_cross_provider_verification import generate_cross_provider_verification


def test_cross_provider_verification_summarizes_anomalous_timestamps(tmp_path: Path):
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "status": "BLOCKED",
                "details": {
                    "recommendation": "CONTINUE_EVIDENCE_COLLECTION",
                    "missing_observations": [
                        {
                            "timestamp_utc": "2021-01-04T22:45:00Z",
                            "symbol": "EURUSD",
                            "session": "ROLLOVER",
                            "weekday": "Monday",
                            "root_cause_category": "ROLLOVER_ZERO_TICK",
                            "cross_source_reference": {
                                "checked": True,
                                "provider": "Reference",
                                "present": False,
                            },
                        },
                        {
                            "timestamp_utc": "2021-01-04T22:46:00Z",
                            "symbol": "EURUSD",
                            "session": "ROLLOVER",
                            "weekday": "Monday",
                            "root_cause_category": "ROLLOVER_ZERO_TICK",
                            "cross_source_reference": {
                                "checked": True,
                                "provider": "Reference",
                                "present": True,
                            },
                        },
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    result = generate_cross_provider_verification(
        source_report=source,
        report_md=tmp_path / "report.md",
        report_json=tmp_path / "report.json",
    )

    assert result["status"] == "BLOCKED"
    assert result["recommendation"] == "CONTINUE_EVIDENCE_COLLECTION"
    assert result["details"]["summary"]["by_conclusion"] == {
        "DUKASCOPY_AND_REFERENCE_ABSENT": 1,
        "DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT": 1,
    }
    assert (tmp_path / "report.md").exists()
