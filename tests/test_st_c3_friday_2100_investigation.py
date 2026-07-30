from __future__ import annotations

from tools.st_c3_investigate_friday_2100 import _classify


def _row(weekday: str, hour: int, month: str, status: str) -> dict[str, object]:
    return {
        "weekday": weekday,
        "hour_of_day_utc": hour,
        "month": month,
        "dukascopy_status": status,
    }


def test_friday_2100_classifies_dst_close_pattern():
    rows = [
        _row("Friday", 20, "04", "PARSED"),
        _row("Friday", 20, "04", "PARSED"),
        _row("Friday", 21, "04", "EMPTY_PAYLOAD"),
        _row("Friday", 21, "04", "EMPTY_PAYLOAD"),
        _row("Friday", 21, "01", "PARSED"),
        _row("Friday", 21, "01", "PARSED"),
    ]

    result = _classify(rows)

    assert result["root_cause"] == "DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH"


def test_friday_2100_keeps_unresolved_when_controls_fail():
    rows = [
        _row("Friday", 20, "04", "PARSED"),
        _row("Friday", 21, "04", "EMPTY_PAYLOAD"),
        _row("Friday", 21, "01", "EMPTY_PAYLOAD"),
    ]

    result = _classify(rows)

    assert result["root_cause"] == "UNRESOLVED_FRIDAY_2100_SOURCE_BEHAVIOR"
