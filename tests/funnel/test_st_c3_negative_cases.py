from __future__ import annotations

from validation.st_c3.negative_runner import run_negative_suite


def test_st_c3_negative_cases_pass():
    summary = run_negative_suite()
    assert summary["status"] == "PASS"
    assert summary["failed_cases"] == 0
    assert summary["total_cases"] >= 4
