#!/usr/bin/env python3
"""Stage-aware multi-agent lifecycle orchestrator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.execution import (
    ExecutionLoggerAgent,
    KillSwitchAgent,
    MT5AdapterAgent,
    OrderManagerAgent,
    PositionManagerAgent,
    RiskManagerAgent,
    SignalIngestAgent,
)
from agents.governance import (
    ConformanceGovernanceAgent,
    MasterGovernanceAgent,
    StrategyGovernanceAgent,
)
from agents.monitoring import EvidenceBuilderAgent, JournalEngineAgent, ReconciliationEngineAgent
from agents.research import (
    ConformanceKernelAgent,
    FailureAnalysisAgent,
    ReplayEngineAgent,
    ScenarioClassifierAgent,
    StatValidationAgent,
)
from validation.st_c3.golden_runner import run_golden_suite
from validation.st_c3.negative_runner import run_negative_suite


DEFAULT_WORKFLOW = ROOT / "config" / "st_c3_operating_workflow.yaml"
DEFAULT_GOVERNANCE = ROOT / "governance" / "st_c3_stage_status.yaml"

PERMISSIONS = {
    "A2": {
        "MasterGovernanceAgent",
        "StrategyGovernanceAgent",
        "ConformanceGovernanceAgent",
        "ConformanceKernelAgent",
        "FailureAnalysisAgent",
        "EvidenceBuilderAgent",
        "JournalEngineAgent",
    },
    "A3": {
        "MasterGovernanceAgent",
        "StrategyGovernanceAgent",
        "ConformanceGovernanceAgent",
        "ScenarioClassifierAgent",
        "ReplayEngineAgent",
        "StatValidationAgent",
        "FailureAnalysisAgent",
        "EvidenceBuilderAgent",
        "JournalEngineAgent",
    },
    "B": {
        "MasterGovernanceAgent",
        "StrategyGovernanceAgent",
        "ConformanceGovernanceAgent",
        "SignalIngestAgent",
        "RiskManagerAgent",
        "OrderManagerAgent",
        "MT5AdapterAgent",
        "PositionManagerAgent",
        "ExecutionLoggerAgent",
        "KillSwitchAgent",
        "EvidenceBuilderAgent",
        "JournalEngineAgent",
        "ReconciliationEngineAgent",
    },
    "C": {
        "MasterGovernanceAgent",
        "StrategyGovernanceAgent",
        "ConformanceGovernanceAgent",
        "SignalIngestAgent",
        "RiskManagerAgent",
        "OrderManagerAgent",
        "MT5AdapterAgent",
        "PositionManagerAgent",
        "ExecutionLoggerAgent",
        "KillSwitchAgent",
        "EvidenceBuilderAgent",
        "JournalEngineAgent",
        "ReconciliationEngineAgent",
    },
    "D": {
        "MasterGovernanceAgent",
        "StrategyGovernanceAgent",
        "ConformanceGovernanceAgent",
        "SignalIngestAgent",
        "RiskManagerAgent",
        "OrderManagerAgent",
        "MT5AdapterAgent",
        "PositionManagerAgent",
        "ExecutionLoggerAgent",
        "KillSwitchAgent",
        "EvidenceBuilderAgent",
        "JournalEngineAgent",
        "ReconciliationEngineAgent",
    },
}


class MultiAgentSMCOrchestrator:
    def __init__(
        self,
        stage: str | None = None,
        workflow_path: Path = DEFAULT_WORKFLOW,
        governance_path: Path = DEFAULT_GOVERNANCE,
    ) -> None:
        self.workflow_path = workflow_path
        self.governance_path = governance_path
        self.master = MasterGovernanceAgent(governance_path, workflow_path)
        self.strategy = StrategyGovernanceAgent(workflow_path)
        self.conformance_governance = ConformanceGovernanceAgent()
        self.conformance_kernel = ConformanceKernelAgent(workflow_path, governance_path)
        self.scenario_classifier = ScenarioClassifierAgent()
        self.replay = ReplayEngineAgent()
        self.stat_validation = StatValidationAgent()
        self.failure_analysis = FailureAnalysisAgent()
        self.signal_ingest = SignalIngestAgent()
        self.risk_manager = RiskManagerAgent()
        self.order_manager = OrderManagerAgent()
        self.mt5_adapter = MT5AdapterAgent()
        self.position_manager = PositionManagerAgent()
        self.execution_logger = ExecutionLoggerAgent()
        self.kill_switch = KillSwitchAgent()
        self.evidence_builder = EvidenceBuilderAgent()
        self.journal = JournalEngineAgent()
        self.reconciliation = ReconciliationEngineAgent()
        self.context = self.master.get_context()
        self.stage = stage or self.context.active_stage

    def _blocked_result(self, reason: str) -> dict[str, Any]:
        result = {
            "stage": self.stage,
            "status": "blocked",
            "reason": reason,
            "active_stage": self.context.active_stage,
            "allowed_agents": sorted(PERMISSIONS.get(self.context.active_stage, set())),
        }
        out_path = ROOT / "evidence" / "operations" / f"orchestrator_{self.stage.lower()}_blocked.json"
        result["evidence_path"] = self.evidence_builder.write(result, out_path)
        return result

    def _agent_names(self) -> list[str]:
        return sorted(PERMISSIONS.get(self.stage, set()))

    def run(self) -> dict[str, Any]:
        allowed, reason = self.master.allow_stage(self.stage)
        if not allowed:
            return self._blocked_result(reason)
        if self.stage == "A2":
            return self._run_stage_a2()
        if self.stage == "A3":
            return self._run_stage_a3()
        if self.stage in {"B", "C", "D"}:
            return self._run_execution_like_stage()
        return self._blocked_result(f"Unsupported stage {self.stage!r}")

    def _run_stage_a2(self) -> dict[str, Any]:
        strategy = self.strategy.expose_strategy()
        conformance = self.conformance_kernel.run_a2_conformance()
        gate = self.conformance_governance.evaluate_a2_gate(conformance)
        failure = self.failure_analysis.summarize(conformance)
        negative_summary = run_negative_suite()
        negative_path = ROOT / "evidence" / "conformance" / "st_c3_s1_g5_negative_summary.json"
        self.evidence_builder.write(negative_summary, negative_path)
        golden_summary = run_golden_suite()
        golden_path = ROOT / "evidence" / "conformance" / "st_c3_s1_g6_golden_summary.json"
        self.evidence_builder.write(golden_summary, golden_path)
        s1_g6_status = "PASS" if golden_summary["failed_cases"] == 0 else "FAIL"
        s1_g5_accepted = "S1-G5" in conformance.get("accepted_gates", [])
        result = {
            "stage": "A2",
            "status": "ok",
            "summary": "Ran the A2 conformance orchestration cycle for the current ST-C3 gate.",
            "agents_used": self._agent_names(),
            "governance": {
                "strategy": self.context.strategy,
                "spec": self.context.spec,
                "current_gate": self.context.current_gate,
                "focus_gate": self.context.focus_gate,
                "authorized_scope": list(self.context.authorized_scope),
            },
            "strategy_package": strategy,
            "conformance_report": conformance,
            "gate_evaluation": gate,
            "failure_analysis": failure,
            "s1_g5_negative_summary": negative_summary,
            "s1_g6_golden_summary": golden_summary,
            "gate_checks": [
                {
                    "stage": "A2",
                    "gate": "S1-G5",
                    "status": "PASS" if negative_summary["failed_cases"] == 0 else "FAIL",
                    "governance_accepted": s1_g5_accepted,
                    "reason": (
                        "Mechanical negative-case suite passed; owner acceptance of S1-G5 remains a separate governance act."
                        if negative_summary["failed_cases"] == 0
                        else "Negative-case suite contains failing deterministic rejection paths."
                    ),
                    "evidence_path": str(negative_path),
                },
                {
                    "stage": "A2",
                    "gate": "S1-G6",
                    "status": s1_g6_status,
                    "governance_eligible": s1_g5_accepted,
                    "reason": (
                        "Mechanical golden-case suite passed, but S1-G6 is not governance-eligible until S1-G5 is accepted."
                        if not s1_g5_accepted and s1_g6_status == "PASS"
                        else "Golden-case suite contains failing cases."
                        if s1_g6_status == "FAIL"
                        else "Mechanical golden-case suite passed and prior gate acceptance is recorded."
                    ),
                    "evidence_path": str(golden_path),
                }
            ],
        }
        out_path = ROOT / "evidence" / "conformance" / "st_c3_a2_orchestration_cycle.json"
        result["evidence_path"] = self.evidence_builder.write(result, out_path)
        result["journal"] = self.journal.summarize("A2", result)
        return result

    def _run_stage_a3(self) -> dict[str, Any]:
        result = {
            "stage": "A3",
            "status": "ok",
            "summary": "Prepared the A3 orchestration sequence without running blocked replay work.",
            "agents_used": self._agent_names(),
            "scenario_classifier": self.scenario_classifier.classify(),
            "replay": self.replay.run(),
            "stat_validation": self.stat_validation.compute(),
        }
        out_path = ROOT / "evidence" / "statistical" / "st_c3_a3_orchestration_cycle.json"
        result["evidence_path"] = self.evidence_builder.write(result, out_path)
        result["journal"] = self.journal.summarize("A3", result)
        return result

    def _run_execution_like_stage(self) -> dict[str, Any]:
        result = {
            "stage": self.stage,
            "status": "ok",
            "summary": "Prepared the execution/demo/production orchestration sequence.",
            "agents_used": self._agent_names(),
            "signal_ingest": self.signal_ingest.load(),
            "risk_manager": self.risk_manager.check(),
            "order_manager": self.order_manager.execute(),
            "mt5_adapter": self.mt5_adapter.send(),
            "position_manager": self.position_manager.update(),
            "execution_logger": self.execution_logger.log(),
            "kill_switch": self.kill_switch.monitor(),
            "reconciliation": self.reconciliation.sync(),
        }
        out_path = ROOT / "evidence" / "execution" / f"st_c3_{self.stage.lower()}_orchestration_cycle.json"
        result["evidence_path"] = self.evidence_builder.write(result, out_path)
        result["journal"] = self.journal.summarize(self.stage, result)
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default=None, choices=["A2", "A3", "B", "C", "D"])
    args = parser.parse_args()
    orchestrator = MultiAgentSMCOrchestrator(stage=args.stage)
    print(json.dumps(orchestrator.run(), indent=2))


if __name__ == "__main__":
    main()
