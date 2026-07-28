from __future__ import annotations

from validation.st_c3.golden_runner import run_golden_suite


def test_st_c3_golden_liquidity_cases_pass():
    summary = run_golden_suite(scenario="liquidity")
    assert summary["status"] == "PASS"
    assert summary["failed_cases"] == 0
