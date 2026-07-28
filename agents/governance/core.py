from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level mapping")
    return data


@dataclass(frozen=True)
class GovernanceContext:
    strategy: str
    spec: str
    active_stage: str
    focus_gate: str
    current_gate: str
    current_gate_status: str
    forbidden_until_authorized: tuple[str, ...]
    authorized_scope: tuple[str, ...]


class MasterGovernanceAgent:
    def __init__(self, governance_path: Path, workflow_path: Path) -> None:
        self.governance_path = governance_path
        self.workflow_path = workflow_path

    def get_context(self) -> GovernanceContext:
        governance = _load_yaml(self.governance_path)
        workflow = _load_yaml(self.workflow_path)

        signal = governance["stage_a_strategy_validation"]["a2_signal_conformance"]
        focus_gate = workflow["focus_gate"]
        current_gate = str(signal.get("current_gate", focus_gate))
        current_gate_status = str(workflow["gates"][focus_gate]["status"])
        active_stage = "A2"
        if current_gate.startswith("S2-"):
            active_stage = "B"
        elif current_gate.startswith("S1-G7") or governance["stage_a_strategy_validation"]["a3_statistical_validation"]["status"] == "in_progress":
            active_stage = "A3"

        return GovernanceContext(
            strategy=str(workflow["strategy"]),
            spec=str(workflow["spec"]),
            active_stage=active_stage,
            focus_gate=focus_gate,
            current_gate=current_gate,
            current_gate_status=current_gate_status,
            forbidden_until_authorized=tuple(governance.get("forbidden_until_authorized", [])),
            authorized_scope=tuple(signal.get("opened", {}).get("authorized_scope", [])),
        )

    def allow_stage(self, requested_stage: str) -> tuple[bool, str]:
        context = self.get_context()
        if requested_stage == context.active_stage:
            return True, "stage is active in governance"
        if requested_stage == "A3":
            return False, "A3 is blocked until A2/S1-G6 passes and a separate owner decision opens A3"
        if requested_stage in {"B", "C", "D"}:
            return False, "execution/demo/production stages remain forbidden until Stage A passes and Stage B is authorized"
        return False, f"{requested_stage} is not the active governance stage"


class StrategyGovernanceAgent:
    def __init__(self, workflow_path: Path) -> None:
        self.workflow_path = workflow_path

    def expose_strategy(self) -> dict[str, Any]:
        workflow = _load_yaml(self.workflow_path)
        gate = workflow["focus_gate"]
        gate_data = workflow["gates"][gate]
        return {
            "strategy": workflow["strategy"],
            "spec": workflow["spec"],
            "focus_gate": gate,
            "stage": gate_data["stage"],
            "title": gate_data["title"],
            "status": gate_data["status"],
            "tasks": gate_data["tasks"],
        }


class ConformanceGovernanceAgent:
    def evaluate_a2_gate(self, conformance_report: dict[str, Any]) -> dict[str, Any]:
        focus = conformance_report["focus_gate"]
        missing = [row["path"] for row in focus["required_paths"] if not row["exists"]]
        return {
            "gate": focus["gate"],
            "status": "ready_for_owner_review" if not missing else "artifact_gaps_remaining",
            "missing_paths": missing,
            "tasks": [task["title"] for task in focus["tasks"]],
        }
