#!/usr/bin/env python3
"""Governance-safe ST-C3 replay runner.

This runner writes a deterministic ledger and hash. It does not open A3,
accept S1-G5/S1-G6, or authorize execution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validation.st_c3.replay_engine import run_replay, write_ledger, write_ledger_hash

DEFAULT_OUT_DIR = Path("reports/validation/st_c3/replay")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-version", default="1.0.7")
    parser.add_argument("--symbols", default="GBPUSD,EURUSD")
    parser.add_argument("--date-from", default="2018-01-01")
    parser.add_argument("--date-to", default="2024-12-31")
    parser.add_argument("--tf-set", default="H4,M15,M3")
    parser.add_argument("--data", type=Path, help="Approved ST-C3 market data directory")
    parser.add_argument("--source-ledger", type=Path)
    parser.add_argument("--sample", action="store_true", help="Use a tiny synthetic dry-run ledger")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    try:
        ledger = run_replay(
            spec_version=args.spec_version,
            symbols=[item.strip() for item in args.symbols.split(",") if item.strip()],
            date_from=args.date_from,
            date_to=args.date_to,
            tf_set=[item.strip() for item in args.tf_set.split(",") if item.strip()],
            source_ledger=args.source_ledger,
            data_dir=args.data,
            sample=args.sample,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": str(exc),
                    "guardrail": "Replay run does not open A3 or imply acceptance.",
                },
                indent=2,
            )
        )
        raise SystemExit(2)
    ledger_path = write_ledger(ledger, args.out_dir / "ledger.json")
    digest = write_ledger_hash(ledger_path, args.out_dir / "ledger.hash")
    print(
        json.dumps(
            {
                "status": "PASS",
                "ledger": str(ledger_path),
                "hash": str(args.out_dir / "ledger.hash"),
                "ledger_sha256": digest,
                "guardrail": "Replay run does not open A3 or imply acceptance.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
