"""Generate a governance owner packet from verified ST-C3 validation outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validation.st_c3.replay_engine import read_ledger_hash


def build_owner_packet(
    *,
    ledger_hash_path: str | Path | None,
    stats_summary_path: str | Path | None,
    robustness_matrix_path: str | Path | None,
    walkforward_results_path: str | Path | None,
    recommendation: str,
) -> dict[str, Any]:
    if recommendation not in {"accept", "reject", "defer"}:
        raise ValueError("recommendation must be accept, reject, or defer")
    return {
        "strategy": "ST-C3",
        "stage": "A2",
        "focus": ["S1-G5", "S1-G6"],
        "recommendation": recommendation,
        "ledger_sha256": read_ledger_hash(ledger_hash_path) if ledger_hash_path else None,
        "stats_summary": _load_json_optional(stats_summary_path),
        "robustness_matrix": _load_json_optional(robustness_matrix_path),
        "walkforward_results": _load_json_optional(walkforward_results_path),
        "gate_evidence": {
            "s1_g5": [
                "reports/validation/st_c3/S1_G5_SIGNAL_TRADE_PLAN_CONFORMANCE_REPORT.md",
                "reports/validation/st_c3/S1_G5_SIGNAL_TRADE_PLAN_CONFORMANCE_COMPLETION_AUDIT.md",
            ],
            "s1_g6": [
                "reports/validation/st_c3/S1_G6_GOLDEN_CASE_QUALIFICATION_REPORT.md",
                "reports/validation/st_c3/S1_G6_GOLDEN_CASE_QUALIFICATION_COMPLETION_AUDIT.md",
            ],
        },
        "guardrail": (
            "Owner packet only. Does not accept S1-G5 or S1-G6, pass A2, open A3, "
            "or authorize execution, optimization, broker integration, demo, live trading, or production."
        ),
    }


def write_owner_packet(packet: dict[str, Any], json_path: str | Path, md_path: str | Path | None = None) -> Path:
    out_path = Path(json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if md_path is not None:
        Path(md_path).write_text(_packet_markdown(packet), encoding="utf-8")
    return out_path


def _load_json_optional(path: str | Path | None) -> Any:
    if path is None:
        return None
    json_path = Path(path)
    if not json_path.exists():
        return None
    return json.loads(json_path.read_text(encoding="utf-8"))


def _packet_markdown(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ST-C3 Owner Decision Packet (A2 / S1-G5 / S1-G6)",
            "",
            "## 1. Replay Ledger",
            f"- Ledger SHA-256: `{packet.get('ledger_sha256')}`",
            "",
            "## 2. Baseline Statistics Summary",
            f"- Status: `{(packet.get('stats_summary') or {}).get('status')}`",
            "",
            "## 3. Robustness Matrix",
            f"- Status: `{(packet.get('robustness_matrix') or {}).get('status')}`",
            "",
            "## 4. Walk-Forward / OOS Results",
            f"- Status: `{(packet.get('walkforward_results') or {}).get('status')}`",
            "",
            "## 5. Gate Evidence",
            "- S1-G5 evidence: listed in packet JSON",
            "- S1-G6 evidence: listed in packet JSON",
            "",
            "## 6. Recommendation",
            f"- Recommended outcome: `{packet['recommendation']}`",
            "",
            "## 7. Decision Section (Owner)",
            "- S1-G5 decision:",
            "- S1-G6 decision:",
            "- Date:",
            "- Owner signature:",
            "",
            f"Guardrail: {packet['guardrail']}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-hash", type=Path, default=Path("reports/validation/st_c3/replay/ledger.hash"))
    parser.add_argument("--stats", type=Path, default=Path("reports/validation/st_c3/replay/stats_summary.json"))
    parser.add_argument("--robustness", type=Path, default=Path("reports/validation/st_c3/replay/robustness_matrix.json"))
    parser.add_argument("--walkforward", type=Path, default=Path("reports/validation/st_c3/replay/walkforward_results.json"))
    parser.add_argument("--recommendation", choices=("accept", "reject", "defer"), default="defer")
    parser.add_argument("--json-out", type=Path, default=Path("reports/validation/st_c3/replay/OWNER_DECISION_PACKET_ST_C3_A2.json"))
    parser.add_argument("--md-out", type=Path, default=Path("reports/validation/st_c3/replay/OWNER_DECISION_PACKET_ST_C3_A2.md"))
    args = parser.parse_args()
    packet = build_owner_packet(
        ledger_hash_path=args.ledger_hash,
        stats_summary_path=args.stats,
        robustness_matrix_path=args.robustness,
        walkforward_results_path=args.walkforward,
        recommendation=args.recommendation,
    )
    write_owner_packet(packet, args.json_out, args.md_out)
    print(json.dumps({"recommendation": packet["recommendation"], "ledger_sha256": packet["ledger_sha256"], "output": str(args.json_out)}, indent=2))


if __name__ == "__main__":
    main()
