"""Phase A stop-report generation for corrected ST-C1 baseline acceptance."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from src.research.report_builder import render_table, write_markdown
from src.research.run_baseline import REQUIRED_TIMEFRAMES, _resolve_artifact_path, _validate_dataset_file, resolve_latest_run
from src.research.dataset_manifest import sha256_file
from symbol_metadata import resolve_symbol


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "reports" / "audit" / "phase_a_stop_report.md"
DEFAULT_REQUIRED_SYMBOLS = ("EURUSD", "GBPUSD", "XAUUSD")

LATEST_VOLATILE_KEYS = {"run_id", "run_dir", "manifest_path", "metrics_path", "report_path", "created_utc", "artifact_hashes"}
MANIFEST_VOLATILE_KEYS = {"generated_utc"}


@dataclass(frozen=True)
class RunSnapshot:
    output_root: Path
    latest_path: Path
    run_dir: Path
    latest: dict[str, Any]
    manifest: dict[str, Any]
    metrics: dict[str, Any]
    report_text: str
    trades: list[dict[str, Any]]
    management_events: list[dict[str, Any]]
    rejected_candidates: list[dict[str, Any]]


@dataclass(frozen=True)
class ComparisonSummary:
    clean_manifest_raw_match: bool
    clean_manifest_normalized_match: bool
    clean_latest_normalized_match: bool
    clean_metrics_match: bool
    clean_trades_hash_match: bool
    clean_management_hash_match: bool
    clean_rejected_hash_match: bool
    clean_equity_hash_match: bool
    resumed_manifest_raw_match: bool | None
    resumed_manifest_normalized_match: bool | None
    resumed_latest_normalized_match: bool | None
    resumed_metrics_match: bool | None
    resumed_trades_hash_match: bool | None
    resumed_management_hash_match: bool | None
    resumed_rejected_hash_match: bool | None
    resumed_equity_hash_match: bool | None
    trade_reconciliation: dict[str, float]
    cost_reconciliation: dict[str, float]


@dataclass(frozen=True)
class PhaseAStopReport:
    decision: str
    reasons: tuple[str, ...]
    branch: str
    head: str
    merge_base: str
    ahead: int
    behind: int
    merge_base_ref: str
    changed_files_by_group: dict[str, tuple[str, ...]]
    required_symbols: tuple[str, ...]
    required_timeframes: tuple[str, ...]
    suite_status: str
    ci_status: str
    ci_links: tuple[str, ...]
    clean_a: RunSnapshot
    clean_b: RunSnapshot
    resumed: RunSnapshot | None
    comparison: ComparisonSummary
    coverage_rows: tuple[dict[str, Any], ...]
    coverage_complete: bool
    strategy_contract_sha256: str
    spec_sha256: str
    cost_profile_sha256: str
    code_tree_sha256: str
    test_command: str | None
    test_duration_seconds: float | None

    def to_markdown(self) -> str:
        lines: list[str] = [
            "# Phase A Stop Report",
            "",
            f"Decision: `{self.decision}`",
            "",
            "## Repository",
            "",
            f"- Branch: `{self.branch}`",
            f"- HEAD: `{self.head}`",
            f"- Merge base: `{self.merge_base}`",
            f"- Ahead/behind: `{self.ahead}/{self.behind}`",
            f"- Merge-base ref: `{self.merge_base_ref}`",
            f"- Code tree SHA: `{self.code_tree_sha256}`",
            f"- Strategy contract SHA256: `{self.strategy_contract_sha256}`",
            f"- Research spec SHA256: `{self.spec_sha256}`",
            f"- Cost profile SHA256: `{self.cost_profile_sha256}`",
            "",
            "## Validation Status",
            "",
            f"- Full suite status: `{self.suite_status}`",
            f"- CI status: `{self.ci_status}`",
            f"- Coverage complete: `{self.coverage_complete}`",
            f"- Clean runs match: `{self.comparison.clean_metrics_match and self.comparison.clean_trades_hash_match and self.comparison.clean_management_hash_match and self.comparison.clean_rejected_hash_match and self.comparison.clean_equity_hash_match and self.comparison.clean_manifest_normalized_match and self.comparison.clean_latest_normalized_match}`",
            f"- Resumed run supplied: `{self.resumed is not None}`",
        ]

        if self.test_command:
            lines.append(f"- Test command: `{self.test_command}`")
        if self.test_duration_seconds is not None:
            lines.append(f"- Test duration seconds: `{self.test_duration_seconds}`")

        if self.ci_links:
            lines.extend(["", "### CI Links"])
            for link in self.ci_links:
                lines.append(f"- {link}")

        if self.reasons:
            lines.extend(["", "### Decision Reasons"])
            for reason in self.reasons:
                lines.append(f"- {reason}")

        lines.extend(
            [
                "",
                "## Changed Files",
                "",
            ]
        )
        for group, files in self.changed_files_by_group.items():
            lines.append(f"### {group.title()}")
            if not files:
                lines.append("- none")
            else:
                for path in files:
                    lines.append(f"- `{path}`")
            lines.append("")

        lines.extend(
            [
                "## Required Coverage",
                "",
                render_table(
                    ["Symbol", "Timeframe", "Status", "Source Symbol", "Path", "Rows", "Validation"],
                    [
                        [
                            row.get("symbol"),
                            row.get("timeframe"),
                            row.get("status"),
                            row.get("source_symbol"),
                            row.get("path"),
                            row.get("rows"),
                            row.get("validation"),
                        ]
                        for row in self.coverage_rows
                    ],
                ),
                "",
                "## Reproducibility",
                "",
                render_table(
                    ["Check", "Result"],
                    [
                        ["clean manifest raw hash", self.comparison.clean_manifest_raw_match],
                        ["clean manifest normalized", self.comparison.clean_manifest_normalized_match],
                        ["clean latest normalized", self.comparison.clean_latest_normalized_match],
                        ["clean metrics", self.comparison.clean_metrics_match],
                        ["clean trades hash", self.comparison.clean_trades_hash_match],
                        ["clean management hash", self.comparison.clean_management_hash_match],
                        ["clean rejected hash", self.comparison.clean_rejected_hash_match],
                        ["clean equity hash", self.comparison.clean_equity_hash_match],
                        ["resumed manifest raw hash", self.comparison.resumed_manifest_raw_match],
                        ["resumed manifest normalized", self.comparison.resumed_manifest_normalized_match],
                        ["resumed latest normalized", self.comparison.resumed_latest_normalized_match],
                        ["resumed metrics", self.comparison.resumed_metrics_match],
                        ["resumed trades hash", self.comparison.resumed_trades_hash_match],
                        ["resumed management hash", self.comparison.resumed_management_hash_match],
                        ["resumed rejected hash", self.comparison.resumed_rejected_hash_match],
                        ["resumed equity hash", self.comparison.resumed_equity_hash_match],
                    ],
                ),
                "",
                "## Trade Cost Reconciliation",
                "",
                render_table(
                    ["Check", "Value"],
                    [[key, value] for key, value in self.comparison.trade_reconciliation.items()],
                ),
                "",
                "## Cost Breakdown",
                "",
                render_table(
                    ["Check", "Value"],
                    [[key, value] for key, value in self.comparison.cost_reconciliation.items()],
                ),
                "",
                "## Safety Statement",
                "",
                "No strategy parameters were optimized.",
                "No broker orders were sent.",
                "Live trading remains disabled.",
            ]
        )
        return "\n".join(lines) + "\n"


def _run_git(args: Sequence[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _run_git_optional(args: Sequence[str]) -> str | None:
    try:
        return _run_git(args)
    except Exception:
        return None


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _normalize_payload(payload: dict[str, Any], volatile_keys: set[str]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key in sorted(payload):
        if key in volatile_keys:
            continue
        value = payload[key]
        if isinstance(value, dict):
            normalized[key] = _normalize_payload(value, volatile_keys)
        elif isinstance(value, list):
            normalized[key] = [
                _normalize_payload(item, volatile_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            normalized[key] = value
    return normalized


def _normalized_json_text(payload: dict[str, Any], volatile_keys: set[str]) -> str:
    return json.dumps(_normalize_payload(payload, volatile_keys), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _float(row: dict[str, Any], key: str) -> float:
    value = row.get(key, 0.0)
    if value in ("", None):
        return 0.0
    return float(value)


def _trade_reconciliation(rows: list[dict[str, Any]]) -> dict[str, float]:
    summary = {
        "trade_count": float(len(rows)),
        "gross_r": round(sum(_float(row, "gross_r") for row in rows), 6),
        "net_r": round(sum(_float(row, "net_r") for row in rows), 6),
        "spread_r": round(sum(_float(row, "spread_r") for row in rows), 6),
        "slippage_r": round(sum(_float(row, "slippage_r") for row in rows), 6),
        "commission_r": round(sum(_float(row, "commission_r") for row in rows), 6),
        "swap_r": round(sum(_float(row, "swap_r") for row in rows), 6),
        "total_cost_drag_r": round(sum(_float(row, "total_cost_r") for row in rows), 6),
    }
    summary["gross_minus_cost_minus_net_r"] = round(summary["gross_r"] - summary["total_cost_drag_r"] - summary["net_r"], 12)
    summary["component_minus_cost_drag_r"] = round(
        summary["spread_r"] + summary["slippage_r"] + summary["commission_r"] + summary["swap_r"] - summary["total_cost_drag_r"],
        12,
    )
    summary["max_trade_gross_net_residual_r"] = 0.0
    summary["max_trade_component_residual_r"] = 0.0
    for row in rows:
        gross = _float(row, "gross_r")
        net = _float(row, "net_r")
        total_cost = _float(row, "total_cost_r")
        components = _float(row, "spread_r") + _float(row, "slippage_r") + _float(row, "commission_r") + _float(row, "swap_r")
        summary["max_trade_gross_net_residual_r"] = max(summary["max_trade_gross_net_residual_r"], abs(gross - total_cost - net))
        summary["max_trade_component_residual_r"] = max(summary["max_trade_component_residual_r"], abs(components - total_cost))
    return summary


def _normalize_latest(latest: dict[str, Any]) -> dict[str, Any]:
    return _normalize_payload(latest, LATEST_VOLATILE_KEYS)


def _normalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return _normalize_payload(manifest, MANIFEST_VOLATILE_KEYS)


def _resolve_data_path(data_dir: Path, symbol: str, timeframe: str) -> tuple[str | None, Path | None]:
    meta = resolve_symbol(symbol)
    for prefix in (meta.canonical_symbol, *meta.aliases):
        candidate = data_dir / f"{prefix}_{timeframe}.csv"
        if candidate.exists():
            return prefix, candidate
    return None, None


def _coverage_rows(data_dir: Path, required_symbols: Iterable[str], required_timeframes: Iterable[str]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for symbol in required_symbols:
        for timeframe in required_timeframes:
            source_symbol, path = _resolve_data_path(data_dir, symbol, timeframe)
            if path is None:
                rows.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "status": "missing",
                        "source_symbol": None,
                        "path": None,
                        "rows": None,
                        "validation": "missing required dataset",
                    }
                )
                continue
            try:
                stats = _validate_dataset_file(path, symbol=symbol, source_symbol=source_symbol or symbol, timeframe=timeframe)
                rows.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "status": "valid",
                        "source_symbol": source_symbol,
                        "path": stats["path"],
                        "rows": stats["rows"],
                        "validation": "ok",
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "status": "invalid",
                        "source_symbol": source_symbol,
                        "path": str(path),
                        "rows": None,
                        "validation": str(exc),
                    }
                )
    return tuple(rows)


def _load_snapshot(output_root: Path) -> RunSnapshot:
    latest = resolve_latest_run(output_root)
    latest_path = output_root / "LATEST.json"
    run_dir = _resolve_artifact_path(output_root, str(latest["run_dir"]))
    manifest_path = _resolve_artifact_path(output_root, str(latest["manifest_path"]))
    metrics_path = _resolve_artifact_path(output_root, str(latest["metrics_path"]))
    report_path = _resolve_artifact_path(output_root, str(latest["report_path"]))
    return RunSnapshot(
        output_root=output_root,
        latest_path=latest_path,
        run_dir=run_dir,
        latest=latest,
        manifest=_load_json(manifest_path),
        metrics=_load_json(metrics_path),
        report_text=report_path.read_text(encoding="utf-8"),
        trades=_load_csv_rows(run_dir / "baseline_trades.csv"),
        management_events=_load_csv_rows(run_dir / "management_events.csv"),
        rejected_candidates=_load_csv_rows(run_dir / "rejected_candidates.csv"),
    )


def _git_state() -> dict[str, Any]:
    branch = _run_git_optional(["branch", "--show-current"]) or "unknown"
    head = _run_git_optional(["rev-parse", "HEAD"]) or "unknown"
    upstream = _run_git_optional(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if not upstream:
        for candidate in ("origin/main", "origin/master", "main", "master"):
            if _run_git_optional(["rev-parse", "--verify", candidate]):
                upstream = candidate
                break
    if not upstream:
        upstream = head
    merge_base = _run_git_optional(["merge-base", "HEAD", upstream]) or head
    counts = _run_git_optional(["rev-list", "--left-right", "--count", f"{upstream}...HEAD"]) or "0\t0"
    behind, ahead = (int(part) for part in counts.split())
    changed_files = _run_git_optional(["diff", "--name-only", f"{merge_base}...HEAD"]) or ""
    return {
        "branch": branch,
        "head": head,
        "merge_base": merge_base,
        "merge_base_ref": upstream,
        "ahead": ahead,
        "behind": behind,
        "changed_files": [line for line in changed_files.splitlines() if line.strip()],
    }


def _group_changed_files(files: Iterable[str]) -> dict[str, tuple[str, ...]]:
    groups: dict[str, list[str]] = {"replay": [], "data": [], "artifacts": [], "tests": [], "ci": [], "docs": [], "other": []}
    for path in files:
        normalized = path.replace("\\", "/")
        if normalized.startswith(("src/research/", "validation/")):
            groups["replay"].append(path)
        elif normalized.startswith("data/"):
            groups["data"].append(path)
        elif normalized.startswith(("reports/refinement/", "validation/cache/")):
            groups["artifacts"].append(path)
        elif normalized.startswith("tests/"):
            groups["tests"].append(path)
        elif normalized.startswith(".github/"):
            groups["ci"].append(path)
        elif normalized.startswith(("docs/", "reports/")):
            groups["docs"].append(path)
        else:
            groups["other"].append(path)
    return {group: tuple(paths) for group, paths in groups.items() if paths or group != "other"}


def _truncate_files(paths: Sequence[str], limit: int = 25) -> tuple[str, ...]:
    if len(paths) <= limit:
        return tuple(paths)
    return tuple(paths[:limit]) + (f"... ({len(paths) - limit} more)",)


def _comparison_summary(clean_a: RunSnapshot, clean_b: RunSnapshot, resumed: RunSnapshot | None) -> ComparisonSummary:
    clean_a_latest = _normalize_latest(clean_a.latest)
    clean_b_latest = _normalize_latest(clean_b.latest)
    clean_a_manifest = _normalize_manifest(clean_a.manifest)
    clean_b_manifest = _normalize_manifest(clean_b.manifest)

    clean_trades_hash_match = clean_a.latest["artifact_hashes"]["trades"] == clean_b.latest["artifact_hashes"]["trades"]
    clean_management_hash_match = clean_a.latest["artifact_hashes"]["management_events"] == clean_b.latest["artifact_hashes"]["management_events"]
    clean_rejected_hash_match = clean_a.latest["artifact_hashes"]["rejected_candidates"] == clean_b.latest["artifact_hashes"]["rejected_candidates"]
    clean_equity_hash_match = clean_a.latest["artifact_hashes"]["equity"] == clean_b.latest["artifact_hashes"]["equity"]
    clean_metrics_match = clean_a.metrics == clean_b.metrics

    resumed_manifest_raw_match = None
    resumed_manifest_normalized_match = None
    resumed_latest_normalized_match = None
    resumed_metrics_match = None
    resumed_trades_hash_match = None
    resumed_management_hash_match = None
    resumed_rejected_hash_match = None
    resumed_equity_hash_match = None

    if resumed is not None:
        resumed_manifest_raw_match = clean_a.manifest == resumed.manifest
        resumed_manifest_normalized_match = _normalize_manifest(clean_a.manifest) == _normalize_manifest(resumed.manifest)
        resumed_latest_normalized_match = _normalize_latest(clean_a.latest) == _normalize_latest(resumed.latest)
        resumed_metrics_match = clean_a.metrics == resumed.metrics
        resumed_trades_hash_match = clean_a.latest["artifact_hashes"]["trades"] == resumed.latest["artifact_hashes"]["trades"]
        resumed_management_hash_match = clean_a.latest["artifact_hashes"]["management_events"] == resumed.latest["artifact_hashes"]["management_events"]
        resumed_rejected_hash_match = clean_a.latest["artifact_hashes"]["rejected_candidates"] == resumed.latest["artifact_hashes"]["rejected_candidates"]
        resumed_equity_hash_match = clean_a.latest["artifact_hashes"]["equity"] == resumed.latest["artifact_hashes"]["equity"]

    return ComparisonSummary(
        clean_manifest_raw_match=clean_a.manifest == clean_b.manifest,
        clean_manifest_normalized_match=clean_a_manifest == clean_b_manifest,
        clean_latest_normalized_match=clean_a_latest == clean_b_latest,
        clean_metrics_match=clean_metrics_match,
        clean_trades_hash_match=clean_trades_hash_match,
        clean_management_hash_match=clean_management_hash_match,
        clean_rejected_hash_match=clean_rejected_hash_match,
        clean_equity_hash_match=clean_equity_hash_match,
        resumed_manifest_raw_match=resumed_manifest_raw_match,
        resumed_manifest_normalized_match=resumed_manifest_normalized_match,
        resumed_latest_normalized_match=resumed_latest_normalized_match,
        resumed_metrics_match=resumed_metrics_match,
        resumed_trades_hash_match=resumed_trades_hash_match,
        resumed_management_hash_match=resumed_management_hash_match,
        resumed_rejected_hash_match=resumed_rejected_hash_match,
        resumed_equity_hash_match=resumed_equity_hash_match,
        trade_reconciliation=_trade_reconciliation(clean_a.trades),
        cost_reconciliation=_cost_reconciliation(clean_a.metrics, clean_a.trades),
    )


def _cost_reconciliation(metrics: dict[str, Any], trades: list[dict[str, Any]]) -> dict[str, float]:
    cost = dict(metrics.get("cost_breakdown", {}))
    trade_summary = _trade_reconciliation(trades)
    return {
        "trade_count": trade_summary["trade_count"],
        "gross_r": trade_summary["gross_r"],
        "net_r": trade_summary["net_r"],
        "spread_r": trade_summary["spread_r"],
        "slippage_r": trade_summary["slippage_r"],
        "commission_r": trade_summary["commission_r"],
        "swap_r": trade_summary["swap_r"],
        "total_cost_drag_r": trade_summary["total_cost_drag_r"],
        "reported_gross_r": float(cost.get("gross_r", trade_summary["gross_r"])),
        "reported_net_r": float(cost.get("net_r", trade_summary["net_r"])),
        "reported_spread_r": float(cost.get("spread_r", trade_summary["spread_r"])),
        "reported_slippage_r": float(cost.get("slippage_r", trade_summary["slippage_r"])),
        "reported_commission_r": float(cost.get("commission_r", trade_summary["commission_r"])),
        "reported_swap_r": float(cost.get("swap_r", trade_summary["swap_r"])),
        "reported_total_cost_drag_r": float(cost.get("total_cost_drag_r", trade_summary["total_cost_drag_r"])),
    }


def build_phase_a_stop_report(
    *,
    clean_run_a: str | Path,
    clean_run_b: str | Path,
    resumed_run: str | Path | None = None,
    data_dir: str | Path = ROOT / "data",
    required_symbols: Iterable[str] = DEFAULT_REQUIRED_SYMBOLS,
    required_timeframes: Iterable[str] = REQUIRED_TIMEFRAMES,
    suite_status: str = "unknown",
    ci_status: str = "unknown",
    ci_links: Iterable[str] = (),
    test_command: str | None = None,
    test_duration_seconds: float | None = None,
    git_state: dict[str, Any] | None = None,
) -> PhaseAStopReport:
    clean_a = _load_snapshot(Path(clean_run_a))
    clean_b = _load_snapshot(Path(clean_run_b))
    resumed = _load_snapshot(Path(resumed_run)) if resumed_run is not None else None
    git = git_state or _git_state()

    coverage_rows = _coverage_rows(Path(data_dir), required_symbols, required_timeframes)
    coverage_complete = all(row["status"] == "valid" for row in coverage_rows)
    comparison = _comparison_summary(clean_a, clean_b, resumed)

    reasons: list[str] = []
    if suite_status != "passed":
        reasons.append(f"Full suite status is {suite_status!r}.")
    if ci_status != "passed":
        reasons.append(f"CI status is {ci_status!r}.")
    if not coverage_complete:
        reasons.append("Required dataset coverage is incomplete or invalid.")
    if not comparison.clean_manifest_normalized_match:
        reasons.append("Clean run manifests do not match after removing volatile fields.")
    if not comparison.clean_latest_normalized_match:
        reasons.append("Clean run latest pointers do not match after removing volatile fields.")
    if not comparison.clean_metrics_match:
        reasons.append("Clean run metrics do not match.")
    if not comparison.clean_trades_hash_match:
        reasons.append("Clean run trade artifacts do not match.")
    if not comparison.clean_management_hash_match:
        reasons.append("Clean run management-event artifacts do not match.")
    if not comparison.clean_rejected_hash_match:
        reasons.append("Clean run rejected-candidate artifacts do not match.")
    if not comparison.clean_equity_hash_match:
        reasons.append("Clean run equity artifacts do not match.")
    if resumed is None:
        reasons.append("Interrupted/resumed replay was not supplied.")
    else:
        checks = [
            comparison.resumed_manifest_normalized_match,
            comparison.resumed_latest_normalized_match,
            comparison.resumed_metrics_match,
            comparison.resumed_trades_hash_match,
            comparison.resumed_management_hash_match,
            comparison.resumed_rejected_hash_match,
            comparison.resumed_equity_hash_match,
        ]
        if not all(check is True for check in checks):
            reasons.append("Resumed replay does not match the clean baseline.")

    decision = "PASS_FOR_BASELINE_REVIEW" if not reasons else "BLOCKED"

    strategy_contract_path = ROOT / "strategies" / "candidates" / "ST-C1_v1.yaml"
    spec_path = ROOT / "specs" / "research" / "v1_baseline.yaml"
    cost_profile_path = ROOT / "config" / "research_costs.yaml"

    return PhaseAStopReport(
        decision=decision,
        reasons=tuple(reasons),
        branch=str(git["branch"]),
        head=str(git["head"]),
        merge_base=str(git["merge_base"]),
        ahead=int(git["ahead"]),
        behind=int(git["behind"]),
        merge_base_ref=str(git["merge_base_ref"]),
        changed_files_by_group={group: _truncate_files(paths) for group, paths in _group_changed_files(git["changed_files"]).items()},
        required_symbols=tuple(required_symbols),
        required_timeframes=tuple(required_timeframes),
        suite_status=suite_status,
        ci_status=ci_status,
        ci_links=tuple(ci_links),
        clean_a=clean_a,
        clean_b=clean_b,
        resumed=resumed,
        comparison=comparison,
        coverage_rows=coverage_rows,
        coverage_complete=coverage_complete,
        strategy_contract_sha256=sha256_file(strategy_contract_path),
        spec_sha256=sha256_file(spec_path),
        cost_profile_sha256=sha256_file(cost_profile_path),
        code_tree_sha256=_run_git(["rev-parse", "HEAD^{tree}"]),
        test_command=test_command,
        test_duration_seconds=test_duration_seconds,
    )


def write_phase_a_stop_report(path: str | Path, report: PhaseAStopReport) -> str:
    return write_markdown(path, report.to_markdown().splitlines())


def _parse_csv_list(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the Phase A stop report.")
    parser.add_argument("--clean-run-a", required=True, help="Output root for clean baseline run #1")
    parser.add_argument("--clean-run-b", required=True, help="Output root for clean baseline run #2")
    parser.add_argument("--resumed-run", help="Output root for resumed baseline run")
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--required-symbols", default=",".join(DEFAULT_REQUIRED_SYMBOLS))
    parser.add_argument("--required-timeframes", default=",".join(REQUIRED_TIMEFRAMES))
    parser.add_argument("--suite-status", default="unknown", choices=("passed", "blocked", "unknown"))
    parser.add_argument("--ci-status", default="unknown", choices=("passed", "blocked", "unknown"))
    parser.add_argument("--ci-link", action="append", default=[])
    parser.add_argument("--test-command")
    parser.add_argument("--test-duration-seconds", type=float)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)

    report = build_phase_a_stop_report(
        clean_run_a=args.clean_run_a,
        clean_run_b=args.clean_run_b,
        resumed_run=args.resumed_run,
        data_dir=args.data_dir,
        required_symbols=_parse_csv_list(args.required_symbols),
        required_timeframes=_parse_csv_list(args.required_timeframes),
        suite_status=args.suite_status,
        ci_status=args.ci_status,
        ci_links=args.ci_link,
        test_command=args.test_command,
        test_duration_seconds=args.test_duration_seconds,
    )
    output = write_phase_a_stop_report(args.output, report)
    print(output)
    print(report.decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
