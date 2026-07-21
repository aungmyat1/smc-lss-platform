"""One-command Phase A reproducibility gate for the ST-C1 baseline."""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence

from src.research.dataset_manifest import sha256_file
from src.research.phase_a_stop_report import (
    DEFAULT_REQUIRED_SYMBOLS,
    _coverage_rows,
    _git_state,
    _parse_csv_list,
    build_phase_a_stop_report,
    write_phase_a_stop_report,
)
from src.research.report_builder import render_table, write_markdown
from src.research.run_baseline import REQUIRED_TIMEFRAMES


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = ROOT / "specs" / "research" / "v1_baseline.yaml"
DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_GATE_ROOT = ROOT / "reports" / "audit" / "phase_a_gate"
DEFAULT_CACHE_ROOT = ROOT / "validation" / "cache" / "phase_a_gate"
DEFAULT_TEST_COMMAND = "python -m pytest -q"


def _repo_relative(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT))
    except Exception:
        return str(candidate)


def _run_command(command: Sequence[str], *, cwd: Path = ROOT) -> tuple[int, float]:
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=cwd)
    return completed.returncode, round(time.perf_counter() - start, 3)


def _split_command(command: str) -> list[str]:
    import shlex

    return shlex.split(command, posix=False)


def _write_preflight_report(
    *,
    path: Path,
    data_dir: Path,
    required_symbols: Iterable[str],
    required_timeframes: Iterable[str],
    suite_status: str,
    test_command: str | None,
    test_duration_seconds: float | None,
    focused_status: str = "not_run",
    focused_test_command: str | None = None,
    focused_test_duration_seconds: float | None = None,
    ci_status: str,
    ci_head: str | None = None,
    reasons: Sequence[str],
) -> str:
    git = _git_state()
    coverage = _coverage_rows(data_dir, required_symbols, required_timeframes)
    contract_path = ROOT / "strategies" / "candidates" / "ST-C1_v1.yaml"
    cost_path = ROOT / "config" / "research_costs.yaml"

    lines = [
        "# Phase A Gate Preflight Report",
        "",
        "Decision: `BLOCKED`",
        "",
        "## Repository",
        "",
        f"- Branch: `{git['branch']}`",
        f"- HEAD: `{git['head']}`",
        f"- Merge base: `{git['merge_base']}`",
        f"- Ahead/behind: `{git['ahead']}/{git['behind']}`",
        f"- Strategy contract SHA256: `{sha256_file(contract_path)}`",
        f"- Research spec SHA256: `{sha256_file(DEFAULT_SPEC)}`",
        f"- Cost profile SHA256: `{sha256_file(cost_path)}`",
        "",
        "## Validation Status",
        "",
        f"- Focused tests status: `{focused_status}`",
        f"- Full suite status: `{suite_status}`",
        f"- CI status: `{ci_status}`",
        f"- CI HEAD: `{ci_head or 'unknown'}`",
        "- Clean runs supplied: `False`",
        "- Interrupted/resumed replay supplied: `False`",
    ]
    if focused_test_command:
        lines.append(f"- Focused test command: `{focused_test_command}`")
    if focused_test_duration_seconds is not None:
        lines.append(f"- Focused test duration seconds: `{focused_test_duration_seconds}`")
    if test_command:
        lines.append(f"- Full suite command: `{test_command}`")
    if test_duration_seconds is not None:
        lines.append(f"- Test duration seconds: `{test_duration_seconds}`")
    lines.extend(["", "### Decision Reasons"])
    for reason in reasons:
        lines.append(f"- {reason}")
    lines.extend(
        [
            "",
            "## Required Coverage",
            "",
            render_table(
                [
                    "Symbol",
                    "Timeframe",
                    "Status",
                    "Source Symbol",
                    "Path",
                    "Start UTC",
                    "End UTC",
                    "Rows",
                    "SHA256",
                    "Duplicate",
                    "Out-of-order",
                    "Expected gaps",
                    "Synthetic",
                    "Provenance",
                    "Validation",
                ],
                [
                    [
                        row.get("symbol"),
                        row.get("timeframe"),
                        row.get("status"),
                        row.get("source_symbol"),
                        row.get("path"),
                        row.get("start_utc"),
                        row.get("end_utc"),
                        row.get("rows"),
                        row.get("sha256"),
                        row.get("duplicate_count"),
                        row.get("out_of_order_count"),
                        row.get("expected_interval_gap_count"),
                        row.get("synthetic_repaired_candle_count"),
                        row.get("provenance"),
                        row.get("validation"),
                    ]
                    for row in coverage
                ],
            ),
            "",
            "## Safety Statement",
            "",
            "No strategy parameters were optimized.",
            "No broker orders were sent.",
            "Live trading remains disabled.",
        ]
    )
    return write_markdown(path, lines)


def run_phase_a_gate(
    *,
    spec: str | Path = DEFAULT_SPEC,
    data_dir: str | Path = DEFAULT_DATA_DIR,
    gate_root: str | Path = DEFAULT_GATE_ROOT,
    cache_root: str | Path = DEFAULT_CACHE_ROOT,
    required_symbols: Iterable[str] = DEFAULT_REQUIRED_SYMBOLS,
    required_timeframes: Iterable[str] = REQUIRED_TIMEFRAMES,
    seed: int = 7,
    progress_every: int = 50000,
    test_command: str = DEFAULT_TEST_COMMAND,
    focused_test_command: str = "",
    ci_status: str = "unknown",
    ci_head: str | None = None,
) -> int:
    spec_path = Path(spec)
    data_root = Path(data_dir)
    gate_base = Path(gate_root)
    cache_base = Path(cache_root)
    stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    output_base = gate_base / stamp
    report_path = output_base / "phase_a_stop_report.md"
    output_base.mkdir(parents=True, exist_ok=True)

    coverage = _coverage_rows(data_root, required_symbols, required_timeframes)
    coverage_complete = all(row["status"] == "valid" for row in coverage)

    focused_status = "not_run"
    focused_test_duration_seconds: float | None = None
    if focused_test_command:
        returncode, focused_test_duration_seconds = _run_command(_split_command(focused_test_command))
        focused_status = "passed" if returncode == 0 else "blocked"

    suite_status = "unknown"
    test_duration_seconds: float | None = None
    if test_command:
        returncode, test_duration_seconds = _run_command(_split_command(test_command))
        suite_status = "passed" if returncode == 0 else "blocked"

    git = _git_state()
    effective_ci_status = ci_status
    if ci_status == "passed" and ci_head and ci_head != git["head"]:
        effective_ci_status = "blocked"
    elif ci_status == "passed" and not ci_head:
        effective_ci_status = "blocked"

    if not coverage_complete:
        missing = [f"{row['symbol']} {row['timeframe']}" for row in coverage if row["status"] != "valid"]
        output = _write_preflight_report(
            path=report_path,
            data_dir=data_root,
            required_symbols=required_symbols,
            required_timeframes=required_timeframes,
            suite_status=suite_status,
            test_command=test_command,
            test_duration_seconds=test_duration_seconds,
            focused_status=focused_status,
            focused_test_command=focused_test_command,
            focused_test_duration_seconds=focused_test_duration_seconds,
            ci_status=effective_ci_status,
            ci_head=ci_head,
            reasons=[
                "Required dataset coverage is incomplete or invalid.",
                "Baseline replay was not started because mandatory inputs failed preflight.",
                "Missing or invalid datasets: " + ", ".join(missing),
            ],
        )
        print(output)
        print("BLOCKED")
        return 2

    if suite_status != "passed":
        output = _write_preflight_report(
            path=report_path,
            data_dir=data_root,
            required_symbols=required_symbols,
            required_timeframes=required_timeframes,
            suite_status=suite_status,
            test_command=test_command,
            test_duration_seconds=test_duration_seconds,
            focused_status=focused_status,
            focused_test_command=focused_test_command,
            focused_test_duration_seconds=focused_test_duration_seconds,
            ci_status=effective_ci_status,
            ci_head=ci_head,
            reasons=[
                f"Full suite status is {suite_status!r}.",
                "Baseline replay was not started because tests failed preflight.",
            ],
        )
        print(output)
        print("BLOCKED")
        return 2

    if effective_ci_status != "passed":
        output = _write_preflight_report(
            path=report_path,
            data_dir=data_root,
            required_symbols=required_symbols,
            required_timeframes=required_timeframes,
            suite_status=suite_status,
            test_command=test_command,
            test_duration_seconds=test_duration_seconds,
            focused_status=focused_status,
            focused_test_command=focused_test_command,
            focused_test_duration_seconds=focused_test_duration_seconds,
            ci_status=effective_ci_status,
            ci_head=ci_head,
            reasons=[
                f"CI status is {effective_ci_status!r}.",
                "Baseline replay was not started because exact-HEAD CI evidence is required for Phase A acceptance.",
            ],
        )
        print(output)
        print("BLOCKED")
        return 2

    clean_a = output_base / "clean_a"
    clean_b = output_base / "clean_b"
    resumed = output_base / "resumed"
    clean_a_cache = cache_base / stamp / "clean_a"
    clean_b_cache = cache_base / stamp / "clean_b"

    base_command = [
        sys.executable,
        "-m",
        "src.research.run_baseline",
        "--spec",
        str(spec_path),
        "--data-dir",
        str(data_root),
        "--seed",
        str(seed),
        "--progress-every",
        str(progress_every),
    ]
    runs = [
        [*base_command, "--output", str(clean_a), "--cache-dir", str(clean_a_cache), "--no-resume"],
        [*base_command, "--output", str(clean_b), "--cache-dir", str(clean_b_cache), "--no-resume"],
        [*base_command, "--output", str(resumed), "--cache-dir", str(clean_a_cache)],
    ]
    for command in runs:
        returncode, _ = _run_command(command)
        if returncode != 0:
            output = _write_preflight_report(
                path=report_path,
                data_dir=data_root,
                required_symbols=required_symbols,
                required_timeframes=required_timeframes,
                suite_status=suite_status,
                test_command=test_command,
                test_duration_seconds=test_duration_seconds,
                focused_status=focused_status,
                focused_test_command=focused_test_command,
                focused_test_duration_seconds=focused_test_duration_seconds,
                ci_status=effective_ci_status,
                ci_head=ci_head,
                reasons=[
                    "Baseline replay command failed.",
                    "Failed command: " + " ".join(command),
                ],
            )
            print(output)
            print("BLOCKED")
            return returncode

    report = build_phase_a_stop_report(
        clean_run_a=clean_a,
        clean_run_b=clean_b,
        resumed_run=resumed,
        data_dir=data_root,
        required_symbols=required_symbols,
        required_timeframes=required_timeframes,
        suite_status=suite_status,
        focused_status=focused_status,
        ci_status=effective_ci_status,
        ci_head=ci_head,
        test_command=test_command,
        test_duration_seconds=test_duration_seconds,
    )
    output = write_phase_a_stop_report(report_path, report)
    print(output)
    print(report.decision)
    print(f"clean_a={_repo_relative(clean_a)}")
    print(f"clean_b={_repo_relative(clean_b)}")
    print(f"resumed={_repo_relative(resumed)}")
    return 0 if report.decision == "PASS_FOR_BASELINE_REVIEW" else 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the full Phase A reproducibility gate.")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--gate-root", default=str(DEFAULT_GATE_ROOT))
    parser.add_argument("--cache-root", default=str(DEFAULT_CACHE_ROOT))
    parser.add_argument("--required-symbols", default=",".join(DEFAULT_REQUIRED_SYMBOLS))
    parser.add_argument("--required-timeframes", default=",".join(REQUIRED_TIMEFRAMES))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--progress-every", type=int, default=50000)
    parser.add_argument("--test-command", default=DEFAULT_TEST_COMMAND)
    parser.add_argument("--focused-test-command", default="")
    parser.add_argument("--ci-status", default="unknown", choices=("passed", "blocked", "unknown"))
    parser.add_argument("--ci-head")
    args = parser.parse_args(argv)
    return run_phase_a_gate(
        spec=args.spec,
        data_dir=args.data_dir,
        gate_root=args.gate_root,
        cache_root=args.cache_root,
        required_symbols=_parse_csv_list(args.required_symbols),
        required_timeframes=_parse_csv_list(args.required_timeframes),
        seed=args.seed,
        progress_every=args.progress_every,
        test_command=args.test_command,
        focused_test_command=args.focused_test_command,
        ci_status=args.ci_status,
        ci_head=args.ci_head,
    )


if __name__ == "__main__":
    raise SystemExit(main())
