from __future__ import annotations

from pathlib import Path

from validation.st_c3.golden_runner import ROOT, run_case_suite


NEGATIVE_ROOT = ROOT / "golden" / "st_c3" / "negative"


def run_negative_suite(root: Path = NEGATIVE_ROOT, scenario: str | None = None) -> dict:
    return run_case_suite(root=root, scenario=scenario)
