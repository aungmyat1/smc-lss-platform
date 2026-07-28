from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.st_c3_workflow import build_operating_report


class ConformanceKernelAgent:
    def __init__(self, workflow_path: Path, governance_path: Path) -> None:
        self.workflow_path = workflow_path
        self.governance_path = governance_path

    def run_a2_conformance(self) -> dict[str, Any]:
        return build_operating_report(
            workflow_path=self.workflow_path,
            governance_path=self.governance_path,
        )


class ScenarioClassifierAgent:
    def classify(self) -> dict[str, Any]:
        return {
            "status": "not_run",
            "reason": "Scenario classification is reserved for A3 statistical validation cycles.",
        }


class ReplayEngineAgent:
    def run(self) -> dict[str, Any]:
        return {
            "status": "blocked",
            "reason": "Historical replay is blocked until A2 passes and A3 is explicitly authorized.",
        }


class StatValidationAgent:
    def compute(self) -> dict[str, Any]:
        return {
            "status": "blocked",
            "reason": "Statistical validation is blocked until replay output exists under an authorized A3 cycle.",
        }


class FailureAnalysisAgent:
    def summarize(self, payload: dict[str, Any]) -> dict[str, Any]:
        focus = payload.get("focus_gate", {})
        missing = [row["path"] for row in focus.get("required_paths", []) if not row["exists"]]
        return {
            "status": "open_items" if missing else "no_artifact_gaps_detected",
            "missing_paths": missing,
            "next_tasks": [task["title"] for task in focus.get("tasks", [])],
        }
