from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from orchestrator.multi_agent_orchestrator import MultiAgentSMCOrchestrator, PERMISSIONS  # noqa: E402


def test_a2_orchestrator_runs_current_conformance_cycle():
    orchestrator = MultiAgentSMCOrchestrator(stage="A2")
    result = orchestrator.run()

    assert result["stage"] == "A2"
    assert result["status"] == "ok"
    assert result["governance"]["focus_gate"] == "S1-G5"
    assert "ConformanceKernelAgent" in result["agents_used"]
    assert "OrderManagerAgent" not in result["agents_used"]
    assert os.path.exists(result["evidence_path"])

    with open(result["evidence_path"], encoding="utf-8") as fh:
        persisted = json.load(fh)
    assert persisted["stage"] == "A2"
    assert persisted["gate_evaluation"]["gate"] == "S1-G5"


def test_b_stage_is_blocked_by_governance_right_now():
    orchestrator = MultiAgentSMCOrchestrator(stage="B")
    result = orchestrator.run()

    assert result["status"] == "blocked"
    assert result["active_stage"] == "A2"
    assert "Stage A passes" in result["reason"]
    assert "SignalIngestAgent" not in result["allowed_agents"]


def test_permissions_matrix_keeps_execution_agents_out_of_a2():
    assert "OrderManagerAgent" not in PERMISSIONS["A2"]
    assert "OrderManagerAgent" in PERMISSIONS["B"]
