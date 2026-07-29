#!/usr/bin/env python3
"""Run the governance-safe ST-C3 ultra-fast validation pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validation.st_c3.owner_packet_generator import build_owner_packet, write_owner_packet
from validation.st_c3.replay_engine import run_replay, verify_ledger_hash, write_ledger, write_ledger_hash
from validation.st_c3.robustness_engine import run_robustness_matrix, write_robustness_matrix
from validation.st_c3.stats_engine import compute_stats_from_ledger, write_stats_report
from validation.st_c3.walkforward_engine import run_fixed_year_walkforward, write_walkforward_results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-version", default="1.0.7")
    parser.add_argument("--symbols", default="GBPUSD,EURUSD")
    parser.add_argument("--date-from", default="2018-01-01")
    parser.add_argument("--date-to", default="2024-12-31")
    parser.add_argument("--tf-set", default="H4,M15,M3")
    parser.add_argument("--source-ledger", type=Path)
    parser.add_argument("--sample", action="store_true", help="Use a tiny synthetic dry-run ledger")
    parser.add_argument("--out-dir", type=Path, default=Path("reports/validation/st_c3/replay"))
    parser.add_argument("--recommendation", choices=("accept", "reject", "defer"), default="defer")
    parser.add_argument("--max-workers", type=int)
    args = parser.parse_args()

    out_dir = args.out_dir
    ledger = run_replay(
        spec_version=args.spec_version,
        symbols=[item.strip() for item in args.symbols.split(",") if item.strip()],
        date_from=args.date_from,
        date_to=args.date_to,
        tf_set=[item.strip() for item in args.tf_set.split(",") if item.strip()],
        source_ledger=args.source_ledger,
        sample=args.sample,
    )
    ledger_path = write_ledger(ledger, out_dir / "ledger.json")
    hash_path = out_dir / "ledger.hash"
    ledger_sha256 = write_ledger_hash(ledger_path, hash_path)
    verify_ledger_hash(ledger_path, hash_path)

    stats = compute_stats_from_ledger(ledger_path, hash_path)
    stats_path = write_stats_report(stats, out_dir / "stats_summary.json", out_dir / "stats_summary.md")

    robustness = run_robustness_matrix(
        ledger_path,
        hash_path,
        "validation/st_c3/robustness_thresholds.yaml",
        max_workers=args.max_workers,
    )
    robustness_path = write_robustness_matrix(robustness, out_dir / "robustness_matrix.json")

    walkforward = run_fixed_year_walkforward(ledger_path, hash_path)
    walkforward_path = write_walkforward_results(walkforward, out_dir / "walkforward_results.json")

    packet = build_owner_packet(
        ledger_hash_path=hash_path,
        stats_summary_path=stats_path,
        robustness_matrix_path=robustness_path,
        walkforward_results_path=walkforward_path,
        recommendation=args.recommendation,
    )
    packet_path = write_owner_packet(
        packet,
        out_dir / "OWNER_DECISION_PACKET_ST_C3_A2.json",
        out_dir / "OWNER_DECISION_PACKET_ST_C3_A2.md",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "ledger_sha256": ledger_sha256,
                "outputs": {
                    "ledger": str(ledger_path),
                    "hash": str(hash_path),
                    "stats": str(stats_path),
                    "robustness": str(robustness_path),
                    "walkforward": str(walkforward_path),
                    "owner_packet": str(packet_path),
                },
                "guardrail": (
                    "This pipeline run does not mark S1-G5/S1-G6 accepted and "
                    "does not open A3. Owner decision required."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
