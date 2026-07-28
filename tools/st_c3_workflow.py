#!/usr/bin/env python3
"""Operational workflow reporter for the ST-C3 roadmap."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = ROOT / "config" / "st_c3_operating_workflow.yaml"
DEFAULT_GOVERNANCE = ROOT / "governance" / "st_c3_stage_status.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level mapping")
    return data


def _accepted_gates(governance: dict[str, Any]) -> set[str]:
    a2 = governance.get("a2_signal_conformance", {})
    accepted: set[str] = set()
    for gate_name in ("s1_g2_gate", "s1_g3_gate", "s1_g4_gate"):
        gate = a2.get(gate_name)
        if isinstance(gate, dict) and gate.get("status") == "accepted":
            parts = gate_name.split("_")
            accepted.add(f"{parts[0].upper()}-{parts[1].upper()}")
    return accepted


def _gate_status(workflow_gate: dict[str, Any], accepted: set[str], gate_id: str) -> str:
    if gate_id in accepted:
        return "accepted"
    return str(workflow_gate.get("status", "unknown"))


def _scaffold(paths: list[str]) -> list[dict[str, Any]]:
    rows = []
    for rel_path in paths:
        path = ROOT / rel_path
        rows.append(
            {
                "path": rel_path,
                "exists": path.exists(),
                "kind": "directory" if path.is_dir() else "file",
            }
        )
    return rows


def build_operating_report(
    workflow_path: Path = DEFAULT_WORKFLOW,
    governance_path: Path = DEFAULT_GOVERNANCE,
) -> dict[str, Any]:
    workflow = _load_yaml(workflow_path)
    governance = _load_yaml(governance_path)

    gates = workflow["gates"]
    focus_gate = workflow["focus_gate"]
    focus = gates[focus_gate]
    accepted = _accepted_gates(governance.get("stage_a_strategy_validation", {}))
    accepted.update(_accepted_gates(governance))

    blocked_by = list(focus.get("blocked_by", []))
    gate_is_unblocked = all(dep in accepted for dep in blocked_by)
    focus_status = _gate_status(focus, accepted, focus_gate)

    downstream = []
    for gate_id, gate in gates.items():
        if gate_id == focus_gate:
            continue
        dependencies = list(gate.get("blocked_by", []))
        downstream.append(
            {
                "gate": gate_id,
                "stage": gate["stage"],
                "title": gate["title"],
                "status": _gate_status(gate, accepted, gate_id),
                "blocked_by": dependencies,
                "unblocked": all(dep in accepted for dep in dependencies),
            }
        )

    report = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "strategy": workflow["strategy"],
        "spec": workflow["spec"],
        "focus_gate": {
            "gate": focus_gate,
            "stage": focus["stage"],
            "title": focus["title"],
            "status": focus_status,
            "blocked_by": blocked_by,
            "unblocked": gate_is_unblocked,
            "tasks": focus["tasks"],
            "commands": list(focus.get("commands", [])),
            "required_paths": _scaffold(list(focus.get("required_paths", []))),
        },
        "accepted_gates": sorted(accepted),
        "authorized_scope": governance.get("stage_a_strategy_validation", {})
        .get("a2_signal_conformance", {})
        .get("opened", {})
        .get("authorized_scope", []),
        "forbidden_until_authorized": governance.get("forbidden_until_authorized", []),
        "downstream_gates": downstream,
    }
    return report


def write_operating_report(report: dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    return out_path


def _print_summary(report: dict[str, Any]) -> None:
    focus = report["focus_gate"]
    print(f"{report['strategy']} {focus['gate']} - {focus['title']}")
    print(f"Status: {focus['status']}")
    print(f"Unblocked: {'yes' if focus['unblocked'] else 'no'}")
    print("Tasks:")
    for task in focus["tasks"]:
        print(f"- {task['title']}")
    print("Required paths:")
    for row in focus["required_paths"]:
        status = "OK" if row["exists"] else "MISSING"
        print(f"- {status} {row['path']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", default=str(DEFAULT_WORKFLOW))
    parser.add_argument("--governance", default=str(DEFAULT_GOVERNANCE))
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    workflow_path = Path(args.workflow)
    governance_path = Path(args.governance)
    report = build_operating_report(workflow_path=workflow_path, governance_path=governance_path)
    out_path = Path(args.out) if args.out else ROOT / _load_yaml(workflow_path)["report_path"]
    write_operating_report(report, out_path)
    _print_summary(report)


if __name__ == "__main__":
    main()
