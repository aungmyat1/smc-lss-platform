from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.st_c3_a2_audit_package import build_a2_audit_package  # noqa: E402


def test_a2_audit_package_summarizes_current_mechanical_evidence():
    package = build_a2_audit_package()

    assert package["strategy"] == "ST-C3"
    assert package["stage"] == "A2"
    assert package["s1_g5"]["mechanical_status"] == "PASS"
    assert package["s1_g5"]["governance_accepted"] is False
    assert package["s1_g6"]["mechanical_status"] == "PASS"
    assert package["s1_g6"]["governance_eligible"] is False
    assert package["fast_track_validation_plan"]["status"] == "planning_material_not_acceptance"
    assert package["fast_track_validation_plan"]["review"]["decision_window_hours"] == 48
    assert package["fast_track_validation_plan"]["future_a3_standard"]["hash_algorithm"] == "SHA-256"
    assert package["recommendation"] == "ready_for_owner_review_only"
