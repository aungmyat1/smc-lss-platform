from __future__ import annotations

from tools.st_c3_root_cause_analysis import assign_root_cause, root_cause_decision


def test_assign_root_cause_maps_expected_maintenance():
    cluster = {
        "start": "2021-01-04T22:45:00Z",
        "calendar_event": "Daily Maintenance",
    }
    validation = {"calendar_event": "Daily Maintenance", "classification": "EXPECTED"}

    assert assign_root_cause(cluster, validation, []) == "EXPECTED_MAINTENANCE"


def test_assign_root_cause_maps_reference_present_to_provider_data_missing():
    cluster = {"start": "2021-01-04T09:31:00Z"}
    validation = {"calendar_event": "Unexpected market-open period", "classification": "UNEXPECTED"}
    references = [{"checked": True, "present": True}]

    assert assign_root_cause(cluster, validation, references) == "PROVIDER_DATA_MISSING"


def test_assign_root_cause_keeps_insufficient_evidence_unknown():
    cluster = {"start": "2021-01-04T09:31:00Z"}
    validation = {"calendar_event": "Unexpected market-open period", "classification": "UNKNOWN"}
    references = [{"checked": False, "present": False}]

    assert assign_root_cause(cluster, validation, references) == "UNKNOWN"


def test_root_cause_decision_rejects_when_unknown_clusters_remain():
    metrics = {"effective_missing_rate": 0.003, "threshold": 0.001}
    rows = [{"suspected_root_cause": "UNKNOWN"}]

    decision = root_cause_decision(metrics, rows, 0.001)

    assert decision["recommendation"] == "REJECT_DATASET"
    assert decision["dataset_status"] == "REJECTED"
    assert decision["replay_status"] == "BLOCKED"


def test_root_cause_decision_requires_exception_for_documented_provider_limits():
    metrics = {"effective_missing_rate": 0.003, "threshold": 0.001}
    rows = [{"suspected_root_cause": "PROVIDER_DATA_MISSING"}]

    decision = root_cause_decision(metrics, rows, 0.001)

    assert decision["recommendation"] == "REQUIRES_GOVERNANCE_EXCEPTION"
    assert decision["dataset_status"] == "NOT_APPROVED"


def test_root_cause_decision_approves_only_when_clean_below_threshold():
    metrics = {"effective_missing_rate": 0.0005, "threshold": 0.001}
    rows = [{"suspected_root_cause": "EXPECTED_MAINTENANCE"}]

    decision = root_cause_decision(metrics, rows, 0.001)

    assert decision["recommendation"] == "APPROVE_DATASET"
    assert decision["dataset_status"] == "APPROVED"
    assert decision["replay_status"] == "READY"
