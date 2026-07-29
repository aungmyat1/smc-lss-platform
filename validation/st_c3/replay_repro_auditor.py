"""Replay reproducibility auditor for ST-C3 ledgers."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from validation.st_c3.replay_engine import load_ledger, read_ledger_hash


def audit_replay_reproducibility(first_dir: str | Path, second_dir: str | Path) -> dict[str, Any]:
    first = Path(first_dir)
    second = Path(second_dir)
    first_hash = read_ledger_hash(first / "ledger.hash")
    second_hash = read_ledger_hash(second / "ledger.hash")
    first_ledger = load_ledger(first / "ledger.json")
    second_ledger = load_ledger(second / "ledger.json")
    first_ids = [trade["id"] for trade in first_ledger["trades"]]
    second_ids = [trade["id"] for trade in second_ledger["trades"]]
    return {
        "status": "PASS" if first_hash == second_hash and first_ids == second_ids else "FAIL",
        "first_ledger_sha256": first_hash,
        "second_ledger_sha256": second_hash,
        "hash_match": first_hash == second_hash,
        "trade_count_match": len(first_ids) == len(second_ids),
        "trade_ids_match": first_ids == second_ids,
        "first_trade_count": len(first_ids),
        "second_trade_count": len(second_ids),
        "guardrail": "Audit only. Does not accept gates, open A3, or authorize execution.",
    }


def run_and_audit_replay(
    *,
    first_dir: str | Path,
    second_dir: str | Path,
    data_dir: str | Path | None = None,
    source_ledger: str | Path | None = None,
    sample: bool = False,
    spec_version: str = "1.0.7",
) -> dict[str, Any]:
    modes = sum(1 for value in (data_dir, source_ledger, sample) if value)
    if modes != 1:
        raise ValueError("choose exactly one of data_dir, source_ledger, or sample")
    for out_dir in (Path(first_dir), Path(second_dir)):
        command = [
            sys.executable,
            "-m",
            "validation.st_c3.run_st_c3_replay",
            "--spec-version",
            spec_version,
            "--out-dir",
            str(out_dir),
        ]
        if data_dir:
            command.extend(["--data", str(data_dir)])
        elif source_ledger:
            command.extend(["--source-ledger", str(source_ledger)])
        else:
            command.append("--sample")
        subprocess.run(command, check=True, capture_output=True, text=True)
    return audit_replay_reproducibility(first_dir, second_dir)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first_dir", type=Path)
    parser.add_argument("second_dir", type=Path)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--source-ledger", type=Path)
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--spec-version", default="1.0.7")
    args = parser.parse_args()
    if args.data or args.source_ledger or args.sample:
        result = run_and_audit_replay(
            first_dir=args.first_dir,
            second_dir=args.second_dir,
            data_dir=args.data,
            source_ledger=args.source_ledger,
            sample=args.sample,
            spec_version=args.spec_version,
        )
    else:
        result = audit_replay_reproducibility(args.first_dir, args.second_dir)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
