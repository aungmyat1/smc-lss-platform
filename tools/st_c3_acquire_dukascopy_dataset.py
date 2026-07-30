#!/usr/bin/env python3
"""Acquire and construct an ST-C3 Dataset v1.0 candidate from Dukascopy ticks.

This tool builds candidate data only. It does not approve the dataset, open A3,
run replay, or change ST-C3 strategy/replay/validation logic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import struct
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import yaml

from tools.st_c3_data_integrity import run_integrity_check
from tools.st_c3_dataset_contract import validate_dataset_contract
from tools.st_c3_download_mt5_dataset import _format_time, _session_for
from tools.st_c3_verify_dukascopy_provider import BASE_URL, Tick, _parse_bi5_ticks
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS, EXPECTED_TIMEFRAMES, MANIFEST_NAME, TIMEFRAME_DELTAS

SOURCE = "Dukascopy tick datafeed"
RAW_CACHE = Path("data/market/raw/dukascopy/st_c3")
REPORT_DIR = Path("reports/validation/st_c3/data_integrity")
STATUS_REPORT = REPORT_DIR / "DUKASCOPY_ACQUISITION_STATUS.json"
ACQUISITION_PROGRESS = REPORT_DIR / "ACQUISITION_PROGRESS.json"
CHECKPOINT_MANIFEST = REPORT_DIR / "CHECKPOINT_MANIFEST.json"
DOWNLOAD_RECOVERY_LOG = REPORT_DIR / "DOWNLOAD_RECOVERY_LOG.md"
NORMALIZATION_REPORT = REPORT_DIR / "NORMALIZATION_REPORT.md"
AGGREGATION_REPORT = REPORT_DIR / "AGGREGATION_REPORT.md"
GUARDRAIL = "Acquisition builds candidates only; approval, replay, A3, demo, and live remain gated."


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def acquire_dukascopy_dataset(
    data_dir: str | Path,
    *,
    cache_dir: str | Path = RAW_CACHE,
    start: datetime | None = None,
    end: datetime | None = None,
    symbols: Iterable[str] | None = None,
    download: bool = False,
    construct: bool = False,
    validate: bool = False,
    max_hours: int | None = None,
    retries: int = 3,
    write_report: bool = True,
) -> dict[str, Any]:
    root = Path(data_dir)
    cache = Path(cache_dir)
    manifest = _load_manifest(root)
    gate = _validate_manifest_gate(manifest)
    if gate is not None:
        return gate

    coverage = manifest.get("coverage") or {}
    range_start = start or _date_start(str(coverage["from"]))
    range_end = end or _date_end(str(coverage["to"]))
    selected_symbols = tuple(sorted(symbols or EXPECTED_SYMBOLS))
    if set(selected_symbols) != EXPECTED_SYMBOLS:
        return _blocked(f"symbols must be exactly {sorted(EXPECTED_SYMBOLS)}")

    downloads: list[dict[str, Any]] = []
    construction: list[dict[str, Any]] = []
    validation_result: dict[str, Any] | None = None
    contract_result: dict[str, Any] | None = None

    if download:
        downloads = _download_tick_range(
            selected_symbols,
            range_start,
            range_end,
            cache,
            max_hours=max_hours,
            retries=retries,
        )
    if construct:
        root.mkdir(parents=True, exist_ok=True)
        construction = _construct_candidate_files(selected_symbols, range_start, range_end, root, cache)
    if validate:
        validation_result = run_integrity_check(root, recover=False, write_reports=True)
        contract_result = validate_dataset_contract("contracts/DATASET_CONTRACT.yaml", root)

    result = {
        "stage": "market_data_acquisition",
        "status": _status(downloads, construction, validation_result),
        "reason": _reason(download, construct, validate, downloads, construction, validation_result),
        "next_action": _next_action(download, construct, validate, validation_result),
        "details": {
            "provider": SOURCE,
            "data_dir": str(root),
            "cache_dir": str(cache),
            "coverage_start_utc": _format_time(range_start.replace(tzinfo=None)),
            "coverage_end_utc": _format_time(range_end.replace(tzinfo=None)),
            "symbols": list(selected_symbols),
            "timeframes": sorted(EXPECTED_TIMEFRAMES),
            "cached_open_hours_in_range": _count_cached_open_hours(selected_symbols, range_start, range_end, cache),
            "downloaded_hours": len([item for item in downloads if item["status"] in {"DOWNLOADED", "CACHED_VERIFIED"}]),
            "verified_cached_hours": len([item for item in downloads if item["status"] == "CACHED_VERIFIED"]),
            "skipped_closed_hours": len([item for item in downloads if item["status"] == "SKIPPED_CLOSED"]),
            "failed_hours": [item for item in downloads if item["status"] == "FAILED"],
            "corrupt_cached_hours": [item for item in downloads if item["status"] == "CORRUPT_CACHE"],
            "construction": construction,
            "validation": _compact_validation(validation_result),
            "contract": contract_result,
        },
        "guardrail": GUARDRAIL,
    }
    if write_report:
        _write_status_report(result)
    return result


def _download_tick_range(
    symbols: Iterable[str],
    start: datetime,
    end: datetime,
    cache: Path,
    *,
    max_hours: int | None,
    retries: int,
) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    processed = 0
    selected_symbols = tuple(symbols)
    for hour in _iter_hours(start, end):
        for symbol in selected_symbols:
            if max_hours is not None and processed >= max_hours:
                return attempts
            processed += 1
            if not _hour_requires_source(hour):
                attempts.append(_hour_attempt(symbol, hour, "SKIPPED_CLOSED", "market closed by ST-C3 calendar"))
                continue
            attempts.append(_download_hour(symbol, hour, cache, retries=retries))
    return attempts


def _download_hour(symbol: str, hour: datetime, cache: Path, *, retries: int) -> dict[str, Any]:
    path = _cache_path(cache, symbol, hour)
    corrupt_reason: str | None = None
    if path.exists() and path.stat().st_size > 0:
        cache_check = _verify_cached_hour(path, hour, symbol)
        if cache_check["status"] == "CACHED_VERIFIED":
            return _hour_attempt(
                symbol,
                hour,
                "CACHED_VERIFIED",
                "cached payload parsed successfully",
                path=path,
                bytes_count=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        corrupt_path = path.with_suffix(path.suffix + ".corrupt")
        path.replace(corrupt_path)
        corrupt_reason = f"replaced corrupt cache {corrupt_path}: {cache_check['reason']}"
    path.parent.mkdir(parents=True, exist_ok=True)
    url = _dukascopy_url(symbol, hour)
    last_reason = ""
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "smc-lss-platform dataset acquisition"})
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
            if not payload:
                last_reason = "empty payload"
                continue
            path.write_bytes(payload)
            parsed = _verify_payload(payload, hour, symbol)
            if parsed is not None:
                last_reason = f"downloaded payload failed parse verification: {parsed}"
                path.unlink(missing_ok=True)
                continue
            return _hour_attempt(
                symbol,
                hour,
                "DOWNLOADED",
                corrupt_reason or "downloaded",
                path=path,
                bytes_count=len(payload),
                sha256=hashlib.sha256(payload).hexdigest(),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_reason = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(min(2 ** (attempt - 1), 8))
    return _hour_attempt(symbol, hour, "FAILED", last_reason or "download failed", path=path, url=url)


def _verify_cached_hour(path: Path, hour: datetime, symbol: str) -> dict[str, str]:
    reason = _verify_payload(path.read_bytes(), hour, symbol)
    if reason is None:
        return {"status": "CACHED_VERIFIED", "reason": "cached payload parsed successfully"}
    return {"status": "CORRUPT_CACHE", "reason": reason}


def _verify_payload(payload: bytes, hour: datetime, symbol: str) -> str | None:
    try:
        ticks = _parse_bi5_ticks(payload, hour.replace(tzinfo=UTC), symbol)
    except (lzma.LZMAError, ValueError, EOFError, struct.error) as exc:
        return f"{type(exc).__name__}: {exc}"
    if not ticks:
        return "payload parsed but contained no ticks"
    if any(current.timestamp < previous.timestamp for previous, current in zip(ticks, ticks[1:])):
        return "tick timestamps are not monotonic"
    return None


def _construct_candidate_files(
    symbols: Iterable[str],
    start: datetime,
    end: datetime,
    data_dir: Path,
    cache: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        m1 = _load_m1_from_cache(symbol, start, end, cache)
        for timeframe in sorted(EXPECTED_TIMEFRAMES):
            candles = _aggregate(m1, timeframe)
            output = data_dir / f"{symbol}_{timeframe}.csv"
            _write_csv(output, candles)
            rows.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "path": str(output),
                    "rows": len(candles),
                    "first_timestamp": _format_time(candles[0].timestamp) if candles else None,
                    "last_timestamp": _format_time(candles[-1].timestamp) if candles else None,
                    "status": "CONSTRUCTED" if candles else "BLOCKED",
                }
            )
    return rows


def _load_m1_from_cache(symbol: str, start: datetime, end: datetime, cache: Path) -> OrderedDict[datetime, Candle]:
    by_minute: OrderedDict[datetime, Candle] = OrderedDict()
    for hour in _iter_hours(start, end):
        if not _hour_requires_source(hour):
            continue
        path = _cache_path(cache, symbol, hour)
        if not path.exists() or path.stat().st_size == 0:
            continue
        ticks = _parse_bi5_ticks(path.read_bytes(), hour.replace(tzinfo=UTC), symbol)
        for minute, candle in _ticks_to_m1(ticks).items():
            naive_minute = minute.replace(tzinfo=None)
            if start.replace(tzinfo=None) <= naive_minute <= end.replace(tzinfo=None):
                by_minute[naive_minute] = candle
    return OrderedDict(sorted(by_minute.items()))


def _ticks_to_m1(ticks: list[Tick]) -> OrderedDict[datetime, Candle]:
    grouped: OrderedDict[datetime, list[Tick]] = OrderedDict()
    for tick in ticks:
        minute = tick.timestamp.replace(second=0, microsecond=0)
        grouped.setdefault(minute, []).append(tick)
    bars: OrderedDict[datetime, Candle] = OrderedDict()
    for minute, minute_ticks in grouped.items():
        bids = [tick.bid for tick in minute_ticks]
        bars[minute] = Candle(
            timestamp=minute,
            open=bids[0],
            high=max(bids),
            low=min(bids),
            close=bids[-1],
            volume=sum(tick.bid_volume for tick in minute_ticks),
        )
    return bars


def _aggregate(source: OrderedDict[datetime, Candle], timeframe: str) -> list[Candle]:
    delta = TIMEFRAME_DELTAS[timeframe]
    span_minutes = int(delta.total_seconds() // 60)
    source_by_time = dict(source)
    candles: list[Candle] = []
    for timestamp in source:
        total_minutes = timestamp.hour * 60 + timestamp.minute
        if total_minutes % span_minutes != 0:
            continue
        window: list[Candle] = []
        cursor = timestamp
        while cursor < timestamp + delta:
            candle = source_by_time.get(cursor)
            if candle is None:
                window = []
                break
            window.append(candle)
            cursor += timedelta(minutes=1)
        if not window:
            continue
        candles.append(
            Candle(
                timestamp=timestamp,
                open=window[0].open,
                high=max(item.high for item in window),
                low=min(item.low for item in window),
                close=window[-1].close,
                volume=sum(item.volume for item in window),
            )
        )
    return candles


def _write_csv(path: Path, candles: Iterable[Candle]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["time", "open", "high", "low", "close", "volume", "session", "news_flag"])
        for candle in candles:
            writer.writerow(
                [
                    _format_time(candle.timestamp),
                    f"{candle.open:.10f}",
                    f"{candle.high:.10f}",
                    f"{candle.low:.10f}",
                    f"{candle.close:.10f}",
                    f"{candle.volume:.5f}",
                    _session_for(candle.timestamp),
                    "false",
                ]
            )


def _load_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        return {}
    loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _validate_manifest_gate(manifest: dict[str, Any]) -> dict[str, Any] | None:
    if not manifest:
        return _blocked("missing ST-C3 dataset manifest")
    if manifest.get("approved") is True:
        return _blocked("dataset manifest is already approved; approved datasets are immutable")
    if str(manifest.get("spec_version")) != "1.0.7":
        return _blocked("dataset manifest spec_version must be 1.0.7")
    if set(manifest.get("symbols") or []) != EXPECTED_SYMBOLS:
        return _blocked(f"manifest symbols must be exactly {sorted(EXPECTED_SYMBOLS)}")
    if set(manifest.get("timeframes") or []) != EXPECTED_TIMEFRAMES:
        return _blocked(f"manifest timeframes must be exactly {sorted(EXPECTED_TIMEFRAMES)}")
    return None


def _status(
    downloads: list[dict[str, Any]],
    construction: list[dict[str, Any]],
    validation_result: dict[str, Any] | None,
) -> str:
    if any(item["status"] == "FAILED" for item in downloads):
        return "BLOCKED"
    if validation_result is not None:
        return "PASS" if validation_result["status"] == "PASS" else "BLOCKED"
    if any(item["status"] == "BLOCKED" for item in construction):
        return "BLOCKED"
    return "IN_PROGRESS" if downloads or construction else "BLOCKED"


def _reason(
    download: bool,
    construct: bool,
    validate: bool,
    downloads: list[dict[str, Any]],
    construction: list[dict[str, Any]],
    validation_result: dict[str, Any] | None,
) -> str:
    failed = [item for item in downloads if item["status"] == "FAILED"]
    if failed:
        first = failed[0]
        return f"{first['symbol']} {first['hour_utc']} download failed: {first['reason']}"
    if validation_result is not None:
        return str(validation_result.get("reason"))
    blocked = [item for item in construction if item["status"] == "BLOCKED"]
    if blocked:
        first = blocked[0]
        return f"{first['symbol']} {first['timeframe']} construction produced no rows"
    if download and not construct:
        return "tick acquisition batch completed; candidate construction has not run"
    if construct and not validate:
        return "candidate CSV construction completed; validation has not run"
    if validate:
        return "validation requested"
    return "no action selected; pass --download, --construct, or --validate"


def _next_action(download: bool, construct: bool, validate: bool, validation_result: dict[str, Any] | None) -> str:
    if validation_result is not None and validation_result["status"] == "PASS":
        return "Owner may review integrity evidence and decide whether to approve the dataset contract."
    if validate:
        return "Resolve validation blockers without changing validation rules."
    if construct:
        return "Run strict dataset integrity validation."
    if download:
        return "Continue resumable tick download until all required open-market hours are cached."
    return "Run with --download to start raw Dukascopy tick acquisition."


def _compact_validation(result: dict[str, Any] | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "status": result.get("status"),
        "reason": result.get("reason"),
        "manifest_status": (result.get("manifest") or {}).get("status"),
    }


def _write_status_report(result: dict[str, Any]) -> None:
    STATUS_REPORT.parent.mkdir(parents=True, exist_ok=True)
    STATUS_REPORT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    _write_checkpoint_files(result)


def _write_checkpoint_files(result: dict[str, Any]) -> None:
    details = result.get("details") or {}
    construction = details.get("construction") or []
    validation = details.get("validation") or {}
    progress = {
        "stage": result.get("stage"),
        "status": result.get("status"),
        "dataset_version": "Dataset_v1.0_5Y",
        "provider": details.get("provider"),
        "completed_date_range": {
            "from": details.get("coverage_start_utc"),
            "to": details.get("coverage_end_utc"),
        },
        "downloaded_hours": details.get("downloaded_hours", 0),
        "cached_open_hours_in_range": details.get("cached_open_hours_in_range", 0),
        "verified_cached_hours": details.get("verified_cached_hours", 0),
        "skipped_closed_hours": details.get("skipped_closed_hours", 0),
        "failed_hours": len(details.get("failed_hours") or []),
        "reconstructed_candles": sum(int(item.get("rows") or 0) for item in construction),
        "missing_candles": "PENDING_FULL_VALIDATION" if not validation else validation.get("reason"),
        "duplicate_count": "PENDING_FULL_VALIDATION",
        "validation_status": validation.get("status", "NOT_RUN") if isinstance(validation, dict) else "NOT_RUN",
        "estimated_completion": "CONTINUE_BATCHED_DOWNLOADS",
        "guardrail": GUARDRAIL,
    }
    ACQUISITION_PROGRESS.write_text(json.dumps(progress, indent=2, sort_keys=True), encoding="utf-8")

    checkpoint_manifest = {
        "dataset_version": "Dataset_v1.0_5Y",
        "approval_status": "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "coverage": progress["completed_date_range"],
        "symbols": details.get("symbols", []),
        "timeframes": details.get("timeframes", []),
        "provider": details.get("provider"),
        "cache_dir": details.get("cache_dir"),
        "data_dir": details.get("data_dir"),
        "status_report": str(STATUS_REPORT),
    }
    CHECKPOINT_MANIFEST.write_text(json.dumps(checkpoint_manifest, indent=2, sort_keys=True), encoding="utf-8")

    failed_hours = details.get("failed_hours") or []
    corrupt_hours = details.get("corrupt_cached_hours") or []
    recovery_lines = [
        "# ST-C3 Dukascopy Download Recovery Log",
        "",
        f"Dataset version: `Dataset_v1.0_5Y`",
        "",
        f"Latest status: **{result.get('status')}**",
        "",
        "## Failed Hours",
        "",
    ]
    if not failed_hours:
        recovery_lines.append("- No failed market-open hours in the latest batch.")
    for item in failed_hours:
        recovery_lines.append(f"- `{item.get('symbol')}` `{item.get('hour_utc')}`: {item.get('reason')}")
    recovery_lines += ["", "## Corrupt Cache", ""]
    if not corrupt_hours:
        recovery_lines.append("- No corrupt cached files remain in the latest batch report.")
    for item in corrupt_hours:
        recovery_lines.append(f"- `{item.get('symbol')}` `{item.get('hour_utc')}`: {item.get('reason')}")
    recovery_lines += ["", "No candles were fabricated, interpolated, or manually edited."]
    DOWNLOAD_RECOVERY_LOG.write_text("\n".join(recovery_lines) + "\n", encoding="utf-8")

    NORMALIZATION_REPORT.write_text(_normalization_markdown(progress, construction), encoding="utf-8")
    AGGREGATION_REPORT.write_text(_aggregation_markdown(progress, construction), encoding="utf-8")


def _normalization_markdown(progress: dict[str, Any], construction: list[dict[str, Any]]) -> str:
    lines = [
        "# ST-C3 Normalization Report",
        "",
        f"Dataset version: `Dataset_v1.0_5Y`",
        "",
        f"Status: **{progress['status']}**",
        "",
        "Normalization source: Dukascopy UTC hourly tick `.bi5` files.",
        "",
        "Rule: ticks are reconstructed into M1 bid OHLCV candles without filling missing minutes.",
        "",
        f"Reconstructed candidate candles in latest run: `{progress['reconstructed_candles']}`",
        "",
    ]
    if not construction:
        lines.append("Candidate CSV construction has not run for the latest checkpoint.")
    return "\n".join(lines) + "\n"


def _aggregation_markdown(progress: dict[str, Any], construction: list[dict[str, Any]]) -> str:
    lines = [
        "# ST-C3 Aggregation Report",
        "",
        f"Dataset version: `Dataset_v1.0_5Y`",
        "",
        f"Status: **{progress['status']}**",
        "",
        "Aggregation rule: emit only complete M1 windows for H4, M15, and M3.",
        "",
        "| Symbol | Timeframe | Rows | First | Last | Status |",
        "|---|---|---:|---|---|---|",
    ]
    if not construction:
        lines.append("| PENDING | PENDING | 0 |  |  | NOT_STARTED |")
    for item in construction:
        lines.append(
            f"| `{item.get('symbol')}` | `{item.get('timeframe')}` | {item.get('rows', 0)} | "
            f"{item.get('first_timestamp') or ''} | {item.get('last_timestamp') or ''} | {item.get('status')} |"
        )
    return "\n".join(lines) + "\n"


def _hour_attempt(
    symbol: str,
    hour: datetime,
    status: str,
    reason: str,
    *,
    path: Path | None = None,
    url: str | None = None,
    bytes_count: int | None = None,
    sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "hour_utc": _format_time(hour.replace(tzinfo=None)),
        "status": status,
        "reason": reason,
        "path": str(path) if path else None,
        "url": url,
        "bytes": bytes_count,
        "sha256": sha256,
    }


def _iter_hours(start: datetime, end: datetime) -> Iterable[datetime]:
    cursor = start.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    last = end.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    while cursor <= last:
        yield cursor
        cursor += timedelta(hours=1)


def _hour_requires_source(hour: datetime) -> bool:
    naive = hour.astimezone(UTC).replace(tzinfo=None)
    probes = [naive + timedelta(minutes=minute) for minute in (0, 30, 59)]
    return any(_is_market_open(probe) for probe in probes)


def _count_cached_open_hours(symbols: Iterable[str], start: datetime, end: datetime, cache: Path) -> int:
    count = 0
    for hour in _iter_hours(start, end):
        if not _hour_requires_source(hour):
            continue
        for symbol in symbols:
            path = _cache_path(cache, symbol, hour)
            if path.exists() and path.stat().st_size > 0:
                count += 1
    return count


def _is_market_open(value: datetime) -> bool:
    if (value.month, value.day) in {(1, 1), (12, 25)}:
        return False
    if value.weekday() == 5:
        return False
    if value.weekday() == 6:
        return False
    if value.weekday() == 4 and value.hour >= 22:
        return False
    return True


def _cache_path(cache: Path, symbol: str, hour: datetime) -> Path:
    hour = hour.astimezone(UTC)
    return cache / symbol / f"{hour:%Y}" / f"{hour:%m}" / f"{hour:%d}" / f"{hour:%H}h_ticks.bi5"


def _dukascopy_url(symbol: str, hour: datetime) -> str:
    hour = hour.astimezone(UTC)
    return f"{BASE_URL}/{symbol}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/{hour.hour:02d}h_ticks.bi5"


def _date_start(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)


def _date_end(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC) + timedelta(days=1) - timedelta(seconds=1)


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(UTC)


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "stage": "market_data_acquisition",
        "status": "BLOCKED",
        "reason": reason,
        "next_action": "Repair acquisition inputs while preserving ST-C3 governance gates.",
        "details": {},
        "guardrail": GUARDRAIL,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/market/approved/st_c3"))
    parser.add_argument("--cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--start", type=_parse_utc, default=None)
    parser.add_argument("--end", type=_parse_utc, default=None)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--construct", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--max-hours", type=int, default=None)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = acquire_dukascopy_dataset(
        args.data,
        cache_dir=args.cache,
        start=args.start,
        end=args.end,
        download=args.download,
        construct=args.construct,
        validate=args.validate,
        max_hours=args.max_hours,
        retries=args.retries,
        write_report=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
