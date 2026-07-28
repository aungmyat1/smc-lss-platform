from __future__ import annotations

import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, ROOT)

from tools.st_c3_workflow import build_operating_report  # noqa: E402


def test_workflow_report_targets_s1_g5_and_finds_scaffold():
    report = build_operating_report()

    assert report["strategy"] == "ST-C3"
    assert report["focus_gate"]["gate"] == "S1-G5"
    assert report["focus_gate"]["status"] == "in_progress"
    assert report["focus_gate"]["unblocked"] is True
    required_paths = {row["path"]: row["exists"] for row in report["focus_gate"]["required_paths"]}
    assert required_paths["strategy/st-c3/rejections.yaml"] is True
    assert required_paths["golden/bos"] is True
    assert required_paths["tests/funnel"] is True


def test_rejection_registry_covers_r1_through_r8():
    path = os.path.join(ROOT, "strategy", "st-c3", "rejections.yaml")
    with open(path, encoding="utf-8") as fh:
        registry = yaml.safe_load(fh)

    codes = registry["codes"]
    assert len(codes) == 8
    for index in range(1, 9):
        expected = f"R{index}_"
        assert any(code.startswith(expected) for code in codes), expected
