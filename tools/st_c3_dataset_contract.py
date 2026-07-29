#!/usr/bin/env python3
"""Validate the ST-C3 dataset contract against current integrity state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from tools.st_c3_data_integrity import inspect_dataset


def validate_dataset_contract(contract_path: str | Path, data_dir: str | Path) -> dict[str, Any]:
    contract_file = Path(contract_path)
    if not contract_file.exists():
        return _blocked(f"dataset contract missing: {contract_file}")
    contract = yaml.safe_load(contract_file.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        return _blocked("dataset contract must be a mapping")

    required = [
        "contract_id",
        "contract_version",
        "strategy",
        "spec_version",
        "status",
        "approval_status",
        "approved_scope",
        "expected_files",
        "approval_gate",
    ]
    missing = [field for field in required if field not in contract]
    if missing:
        return _blocked(f"dataset contract missing required fields: {missing}")

    summaries = inspect_dataset(data_dir)
    integrity_pass = all(summary.status == "PASS" for summary in summaries)
    contract_approved = contract.get("approval_status") == "APPROVED"
    gate = contract.get("approval_gate") or {}
    replay_prohibited = bool(gate.get("replay_prohibited_unless_approved", True))

    if contract_approved and not integrity_pass:
        return _rejected("contract claims approval while dataset integrity is blocked", summaries)
    if not contract_approved and not replay_prohibited:
        return _rejected("blocked/unapproved contract must prohibit replay", summaries)

    return {
        "stage": "dataset_contract",
        "status": "ACCEPTED" if contract_approved and integrity_pass else "BLOCKED",
        "reason": "dataset contract is approved and integrity passed" if contract_approved and integrity_pass else _first_blocker(summaries),
        "next_action": "Proceed to owner A3-opening decision" if contract_approved and integrity_pass else "Owner must provide a complete canonical dataset and approve the contract.",
        "details": {
            "contract": str(contract_file),
            "contract_status": contract.get("status"),
            "approval_status": contract.get("approval_status"),
            "integrity_pass": integrity_pass,
            "replay_prohibited_unless_approved": replay_prohibited,
            "files": [
                {
                    "path": summary.path,
                    "status": summary.status,
                    "missing_count": len(summary.missing_timestamps),
                    "duplicate_count": len(summary.duplicate_timestamps),
                    "issue_count": len(summary.issues),
                }
                for summary in summaries
            ],
        },
    }


def _first_blocker(summaries: list[Any]) -> str:
    for summary in summaries:
        if summary.missing_timestamps:
            return f"{Path(summary.path).name} missing candle {summary.missing_timestamps[0]}"
        if summary.duplicate_timestamps:
            return f"{Path(summary.path).name} duplicate timestamp {summary.duplicate_timestamps[0]}"
        if summary.issues:
            return f"{Path(summary.path).name}: {summary.issues[0].message}"
    return "dataset contract is not approved"


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "stage": "dataset_contract",
        "status": "BLOCKED",
        "reason": reason,
        "next_action": "Create or repair the dataset contract.",
        "details": {},
    }


def _rejected(reason: str, summaries: list[Any]) -> dict[str, Any]:
    return {
        "stage": "dataset_contract",
        "status": "REJECTED",
        "reason": reason,
        "next_action": "Correct the contract so it reflects the true blocked dataset state.",
        "details": {
            "first_blocker": _first_blocker(summaries),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=Path("contracts/DATASET_CONTRACT.yaml"))
    parser.add_argument("--data", type=Path, default=Path("data/market/approved/st_c3"))
    args = parser.parse_args()
    result = validate_dataset_contract(args.contract, args.data)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "REJECTED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
