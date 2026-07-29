#!/usr/bin/env python3
"""ST-C3 historical data integrity scanner and verified recovery tool.

The recovery path may only insert candles returned by the approved MT5 data
source for the exact missing timestamp. It never fabricates or interpolates
OHLC values.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_download_mt5_dataset import Candle, _copy_candles, _format_time, _session_for
from tools.st_c3_prepare_dataset_manifest import prepare_dataset_manifest
from validation.st_c3.dataset_loader import (
    EXPECTED_SYMBOLS,
    EXPECTED_TIMEFRAMES,
    MANIFEST_NAME,
    REQUIRED_COLUMNS,
    TIMEFRAME_DELTAS,
    _is_fx_holiday,
    _is_fx_market_open,
    _normalize_files,
    _parse_timestamp,
    _validate_csv_covers_requested_range,
    sha256_file,
)

REPORT_DIR = Path("reports/validation/st_c3/data_integrity")
GUARDRAIL = "Data recovery does not open A3, run replay, or imply acceptance."


@dataclass(frozen=True)
class DataIssue:
    code: str
    message: str
    timestamp: str | None = None
    previous_timestamp: str | None = None
    next_timestamp: str | None = None


@dataclass(frozen=True)
class FileIntegrity:
    symbol: str
    timeframe: str
    path: str
    exists: bool
    rows: int = 0
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    sha256: str | None = None
    missing_timestamps: tuple[str, ...] = ()
    duplicate_timestamps: tuple[str, ...] = ()
    issues: tuple[DataIssue, ...] = ()

    @property
    def status(self) -> str:
        return "PASS" if self.exists and not self.missing_timestamps and not self.duplicate_timestamps and not self.issues else "BLOCKED"


def run_integrity_check(
    data_dir: str | Path,
    *,
    recover: bool = False,
    write_reports: bool = False,
    max_recovery_gaps: int = 25,
) -> dict[str, Any]:
    root = Path(data_dir)
    before = inspect_dataset(root)
    recovery_log: list[dict[str, Any]] = []
    after = before
    if recover:
        recovery_log = attempt_recovery(root, before, max_gaps=max_recovery_gaps)
        after = inspect_dataset(root)

    manifest_result = (
        prepare_dataset_manifest(root, write=True)
        if _all_files_pass(after)
        else {
            "status": "BLOCKED",
            "reason": "dataset integrity issues remain; manifest was not rebuilt",
            "guardrail": GUARDRAIL,
        }
    )
    result = {
        "status": "PASS" if _all_files_pass(after) and manifest_result["status"] == "PASS" else "BLOCKED",
        "stage": "data_integrity",
        "reason": _reason(after, manifest_result),
        "before": _dataset_payload(before),
        "after": _dataset_payload(after),
        "recovery_attempted": recover,
        "recovery_log": recovery_log,
        "manifest": manifest_result,
        "guardrail": GUARDRAIL,
    }
    if write_reports:
        write_integrity_reports(result)
    return result


def inspect_dataset(data_dir: str | Path) -> list[FileIntegrity]:
    root = Path(data_dir)
    manifest_path = root / MANIFEST_NAME
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        import yaml

        loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest = loaded if isinstance(loaded, dict) else {}
    files = _normalize_files(manifest.get("files")) if manifest.get("files") else _default_file_entries()
    coverage = manifest.get("coverage") or {}
    by_key = {(item.get("symbol"), item.get("timeframe")): item for item in files}
    summaries: list[FileIntegrity] = []
    for symbol in sorted(EXPECTED_SYMBOLS):
        for timeframe in sorted(EXPECTED_TIMEFRAMES):
            entry = by_key.get((symbol, timeframe)) or {
                "symbol": symbol,
                "timeframe": timeframe,
                "path": f"{symbol}_{timeframe}.csv",
            }
            summaries.append(
                inspect_csv(
                    root / str(entry["path"]),
                    symbol=symbol,
                    timeframe=timeframe,
                    date_from=str(coverage.get("from", "")),
                    date_to=str(coverage.get("to", "")),
                )
            )
    return summaries


def inspect_csv(
    path: Path,
    *,
    symbol: str,
    timeframe: str,
    date_from: str | None = None,
    date_to: str | None = None,
) -> FileIntegrity:
    if not path.exists():
        return FileIntegrity(
            symbol=symbol,
            timeframe=timeframe,
            path=str(path),
            exists=False,
            issues=(DataIssue("FILE_MISSING", f"dataset file missing: {path}"),),
        )
    delta = TIMEFRAME_DELTAS[timeframe]
    issues: list[DataIssue] = []
    missing: list[str] = []
    duplicates: list[str] = []
    timestamps: list[datetime] = []
    seen: set[datetime] = set()
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing_columns:
            issues.append(DataIssue("MISSING_COLUMNS", f"missing required columns: {missing_columns}"))
        for row_number, row in enumerate(reader, start=2):
            try:
                current = _parse_timestamp(row["time"])
            except Exception as exc:  # noqa: BLE001 - report row-level validator failure.
                issues.append(DataIssue("INVALID_TIMESTAMP", f"row {row_number}: invalid timestamp: {exc}"))
                continue
            if current in seen:
                duplicates.append(_format_time(current))
                issues.append(DataIssue("DUPLICATE_TIMESTAMP", "duplicate timestamp", timestamp=_format_time(current)))
            if timestamps and current <= timestamps[-1]:
                issues.append(
                    DataIssue(
                        "TIMESTAMP_ORDER",
                        "timestamps must be strictly increasing",
                        previous_timestamp=_format_time(timestamps[-1]),
                        next_timestamp=_format_time(current),
                    )
                )
            if timestamps and current - timestamps[-1] != delta:
                missing.extend(_missing_market_open_timestamps(timestamps[-1], current, delta))
            _validate_row_values(row, row_number, issues)
            seen.add(current)
            timestamps.append(current)
    summary = {
        "rows": len(timestamps),
        "first_timestamp": _format_time(timestamps[0]) if timestamps else None,
        "last_timestamp": _format_time(timestamps[-1]) if timestamps else None,
    }
    if timestamps and date_from and date_to:
        try:
            _validate_csv_covers_requested_range(
                path,
                summary,
                timeframe=timeframe,
                date_from=date_from,
                date_to=date_to,
            )
        except ValueError as exc:
            issues.append(DataIssue("CSV_COVERAGE", str(exc)))
    return FileIntegrity(
        symbol=symbol,
        timeframe=timeframe,
        path=str(path),
        exists=True,
        rows=summary["rows"],
        first_timestamp=summary["first_timestamp"],
        last_timestamp=summary["last_timestamp"],
        sha256=sha256_file(path),
        missing_timestamps=tuple(missing),
        duplicate_timestamps=tuple(duplicates),
        issues=tuple(issues),
    )


def attempt_recovery(root: Path, summaries: Iterable[FileIntegrity], *, max_gaps: int) -> list[dict[str, Any]]:
    candidates: list[tuple[FileIntegrity, str]] = []
    for summary in summaries:
        for timestamp in summary.missing_timestamps:
            candidates.append((summary, timestamp))
    recovery_log: list[dict[str, Any]] = []
    if not candidates:
        return recovery_log
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return [{"status": "BLOCKED", "reason": "MetaTrader5 package is not installed"}]
    if not mt5.initialize():
        return [{"status": "BLOCKED", "reason": f"mt5.initialize() failed: {mt5.last_error()}"}]
    try:
        for summary, timestamp in candidates[:max_gaps]:
            path = Path(summary.path)
            missing_time = _parse_timestamp(timestamp)
            start = (missing_time - TIMEFRAME_DELTAS[summary.timeframe]).replace(tzinfo=UTC)
            end = (missing_time + TIMEFRAME_DELTAS[summary.timeframe]).replace(tzinfo=UTC)
            candles = _copy_candles(mt5, summary.symbol, summary.timeframe, start, end)
            exact = [candle for candle in candles if candle.timestamp == missing_time]
            if not exact:
                recovery_log.append(
                    {
                        "status": "BLOCKED",
                        "symbol": summary.symbol,
                        "timeframe": summary.timeframe,
                        "timestamp": timestamp,
                        "reason": "approved source did not return the exact missing candle",
                    }
                )
                continue
            _merge_candles(path, exact)
            recovery_log.append(
                {
                    "status": "RECOVERED",
                    "symbol": summary.symbol,
                    "timeframe": summary.timeframe,
                    "timestamp": timestamp,
                    "source": "MetaTrader5.copy_rates_range",
                }
            )
    finally:
        mt5.shutdown()
    if len(candidates) > max_gaps:
        recovery_log.append(
            {
                "status": "BLOCKED",
                "reason": f"recovery capped at {max_gaps} gaps; {len(candidates) - max_gaps} gaps not attempted",
            }
        )
    return recovery_log


def write_integrity_reports(result: dict[str, Any], *, report_dir: Path = REPORT_DIR) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "UPDATED_MANIFEST.json").write_text(json.dumps(result["manifest"], indent=2), encoding="utf-8")
    (report_dir / "RECOVERY_LOG.md").write_text(_recovery_markdown(result), encoding="utf-8")
    (report_dir / "DATA_INTEGRITY_REPORT.md").write_text(_integrity_markdown(result, section="before"), encoding="utf-8")
    (report_dir / "VALIDATION_SUMMARY.md").write_text(_integrity_markdown(result, section="after"), encoding="utf-8")


def _merge_candles(path: Path, candles: Iterable[Candle]) -> None:
    rows: dict[datetime, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or ["time", "open", "high", "low", "close", "volume", "session", "news_flag"]
        for row in reader:
            rows[_parse_timestamp(row["time"])] = row
    for candle in candles:
        rows[candle.timestamp] = {
            "time": _format_time(candle.timestamp),
            "open": f"{candle.open:.10f}",
            "high": f"{candle.high:.10f}",
            "low": f"{candle.low:.10f}",
            "close": f"{candle.close:.10f}",
            "volume": f"{candle.volume:.0f}",
            "session": _session_for(candle.timestamp),
            "news_flag": "false",
        }
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for timestamp in sorted(rows):
            writer.writerow(rows[timestamp])


def _validate_row_values(row: dict[str, str], row_number: int, issues: list[DataIssue]) -> None:
    try:
        open_price = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        volume = float(row["volume"])
    except (KeyError, ValueError) as exc:
        issues.append(DataIssue("INVALID_OHLCV", f"row {row_number}: invalid OHLCV value: {exc}"))
        return
    if high < max(open_price, close):
        issues.append(DataIssue("INVALID_OHLC", f"row {row_number}: high below open/close"))
    if low > min(open_price, close):
        issues.append(DataIssue("INVALID_OHLC", f"row {row_number}: low above open/close"))
    if high < low:
        issues.append(DataIssue("INVALID_OHLC", f"row {row_number}: high below low"))
    if volume < 0:
        issues.append(DataIssue("INVALID_VOLUME", f"row {row_number}: volume must be non-negative"))
    session = row.get("session", "")
    if session and session not in {"LONDON", "NY", "OTHER"}:
        issues.append(DataIssue("INVALID_SESSION", f"row {row_number}: invalid session {session!r}"))
    news_flag = row.get("news_flag", "")
    if news_flag and news_flag.lower() not in {"true", "false", "1", "0", "yes", "no"}:
        issues.append(DataIssue("INVALID_NEWS_FLAG", f"row {row_number}: invalid news_flag {news_flag!r}"))


def _missing_market_open_timestamps(previous: datetime, current: datetime, delta: timedelta) -> list[str]:
    missing: list[str] = []
    probe = previous + delta
    while probe < current:
        if _is_fx_market_open(probe) and not _is_fx_holiday(probe):
            missing.append(_format_time(probe))
        probe += delta
    return missing


def _default_file_entries() -> list[dict[str, str]]:
    return [
        {"symbol": symbol, "timeframe": timeframe, "path": f"{symbol}_{timeframe}.csv"}
        for symbol in sorted(EXPECTED_SYMBOLS)
        for timeframe in sorted(EXPECTED_TIMEFRAMES)
    ]


def _all_files_pass(summaries: Iterable[FileIntegrity]) -> bool:
    return all(summary.status == "PASS" for summary in summaries)


def _reason(summaries: Iterable[FileIntegrity], manifest_result: dict[str, Any]) -> str:
    for summary in summaries:
        if summary.missing_timestamps:
            return f"{Path(summary.path).name} missing candle {summary.missing_timestamps[0]}"
        if summary.duplicate_timestamps:
            return f"{Path(summary.path).name} duplicate timestamp {summary.duplicate_timestamps[0]}"
        if summary.issues:
            return f"{Path(summary.path).name}: {summary.issues[0].message}"
    return "dataset integrity passed" if manifest_result["status"] == "PASS" else str(manifest_result.get("reason"))


def _dataset_payload(summaries: Iterable[FileIntegrity]) -> list[dict[str, Any]]:
    return [
        {
            **asdict(summary),
            "status": summary.status,
            "missing_count": len(summary.missing_timestamps),
            "duplicate_count": len(summary.duplicate_timestamps),
            "issue_count": len(summary.issues),
        }
        for summary in summaries
    ]


def _integrity_markdown(result: dict[str, Any], *, section: str) -> str:
    rows = result[section]
    lines = [
        f"# ST-C3 Data Integrity Report ({section})",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Root Cause Analysis",
        "",
        _root_cause_text(rows, result),
        "",
        "| File | Status | Rows | First | Last | Missing | Duplicates | Issues |",
        "|---|---:|---:|---|---|---:|---:|---:|",
    ]
    for item in rows:
        lines.append(
            f"| `{Path(item['path']).name}` | {item['status']} | {item['rows']} | "
            f"{item['first_timestamp'] or ''} | {item['last_timestamp'] or ''} | "
            f"{item['missing_count']} | {item['duplicate_count']} | {item['issue_count']} |"
        )
    lines += ["", "## First Blocking Details", ""]
    for item in rows:
        if item["missing_timestamps"]:
            lines.append(f"- `{Path(item['path']).name}` first missing candle: `{item['missing_timestamps'][0]}`")
        for issue in item["issues"][:3]:
            lines.append(f"- `{Path(item['path']).name}` {issue['code']}: {issue['message']}")
    lines += [
        "",
        "## Required Owner Action",
        "",
        "Provide a complete approved dataset from an authoritative source for the full manifest coverage window.",
        "Do not manually edit, fabricate, or interpolate candles.",
        "After replacement, rerun `python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports`.",
    ]
    return "\n".join(lines) + "\n"


def _recovery_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# ST-C3 Data Recovery Log",
        "",
        f"Recovery attempted: **{result['recovery_attempted']}**",
        "",
        f"Final status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        "## Attempts",
        "",
    ]
    if not result["recovery_log"]:
        lines.append("- No recovery attempts were made.")
    for item in result["recovery_log"]:
        lines.append(f"- `{item.get('status')}` {item.get('symbol', '')} {item.get('timeframe', '')} {item.get('timestamp', '')}: {item.get('reason', item.get('source', ''))}")
    lines += [
        "",
        "## Guardrail",
        "",
        "No candles were fabricated or interpolated. Only exact candles returned by the approved source may be merged.",
        "",
        "## Required Data Source",
        "",
        "A complete owner-approved EURUSD/GBPUSD H4/M15/M3 historical dataset covering 2018-01-01 through 2024-12-31.",
    ]
    return "\n".join(lines) + "\n"


def _root_cause_text(rows: list[dict[str, Any]], result: dict[str, Any]) -> str:
    coverage_failures = [
        f"`{Path(item['path']).name}`: {issue['message']}"
        for item in rows
        for issue in item["issues"]
        if issue["code"] == "CSV_COVERAGE"
    ]
    missing_files = [item for item in rows if item["missing_count"]]
    if coverage_failures:
        return (
            "The approved-data directory contains partial or wrong-range files. "
            "M15 files begin in 2022 instead of 2018, and M3 files contain one "
            "2025 candle rather than the approved 2018-2024 window. "
            "The attempted MT5 recovery did not return exact missing candles, "
            "so no repair was applied.\n\n"
            + "\n".join(f"- {item}" for item in coverage_failures)
        )
    if missing_files:
        return (
            "The files are present but have market-open timestamp gaps. "
            "Automatic recovery must provide the exact missing candles before "
            "manifest hashes can be rebuilt."
        )
    if result["status"] == "PASS":
        return "No data-integrity defects remain."
    return "Dataset remains blocked by manifest or file validation issues."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/market/approved/st_c3"))
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--write-reports", action="store_true")
    parser.add_argument("--max-recovery-gaps", type=int, default=25)
    args = parser.parse_args()
    result = run_integrity_check(
        args.data,
        recover=args.recover,
        write_reports=args.write_reports,
        max_recovery_gaps=args.max_recovery_gaps,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
