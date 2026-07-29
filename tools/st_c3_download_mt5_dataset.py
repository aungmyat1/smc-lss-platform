#!/usr/bin/env python3
"""Download the six ST-C3 v1.0.7 approved-data CSVs from local MetaTrader 5.

This tool only reads historical market data. It does not open A3, accept
S1-G5/S1-G6, or activate execution/demo/live paths.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import yaml

from tools.st_c3_prepare_dataset_manifest import prepare_dataset_manifest
from validation.st_c3.dataset_loader import (
    EXPECTED_SYMBOLS,
    EXPECTED_TIMEFRAMES,
    MANIFEST_NAME,
)

GUARDRAIL = "Replay run does not open A3 or imply acceptance."


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def download_st_c3_mt5_dataset(
    data_dir: str | Path,
    *,
    write_manifest: bool = False,
) -> dict[str, Any]:
    root = Path(data_dir)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        return _blocked(f"missing ST-C3 dataset manifest: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        return _blocked("dataset manifest must be a mapping")
    if manifest.get("approved") is not True:
        return _blocked("dataset manifest is not approved")
    if str(manifest.get("spec_version")) != "1.0.7":
        return _blocked("dataset manifest spec_version must be 1.0.7")
    if set(manifest.get("symbols") or []) != EXPECTED_SYMBOLS:
        return _blocked(f"manifest symbols must be exactly {sorted(EXPECTED_SYMBOLS)}")
    if set(manifest.get("timeframes") or []) != EXPECTED_TIMEFRAMES:
        return _blocked(f"manifest timeframes must be exactly {sorted(EXPECTED_TIMEFRAMES)}")

    try:
        import MetaTrader5 as mt5
    except ImportError:
        return _blocked("MetaTrader5 package is not installed")

    coverage = manifest.get("coverage") or {}
    start = _date_start(str(coverage.get("from", "")))
    end = _date_end(str(coverage.get("to", "")))
    if not mt5.initialize():
        return _blocked(f"mt5.initialize() failed: {mt5.last_error()}")

    root.mkdir(parents=True, exist_ok=True)
    downloads: list[dict[str, Any]] = []
    try:
        for symbol in sorted(EXPECTED_SYMBOLS):
            if not mt5.symbol_select(symbol, True):
                return _blocked(f"MT5 symbol_select failed for {symbol}: {mt5.last_error()}")
            for timeframe in sorted(EXPECTED_TIMEFRAMES):
                candles = _copy_candles(mt5, symbol, timeframe, start, end)
                if not candles:
                    return _blocked(f"MT5 returned no data for {symbol} {timeframe}: {mt5.last_error()}")
                path = root / f"{symbol}_{timeframe}.csv"
                _write_csv(path, candles)
                downloads.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "path": str(path),
                        "rows": len(candles),
                        "first_timestamp": _format_time(candles[0].timestamp),
                        "last_timestamp": _format_time(candles[-1].timestamp),
                    }
                )
    finally:
        mt5.shutdown()

    manifest_result = prepare_dataset_manifest(root, write=write_manifest)
    if manifest_result["status"] != "PASS":
        return manifest_result
    return {
        "status": "PASS",
        "downloads": downloads,
        "manifest": manifest_result,
        "guardrail": GUARDRAIL,
    }


def _copy_candles(mt5: Any, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[Candle]:
    tf_map = {
        "H4": mt5.TIMEFRAME_H4,
        "M15": mt5.TIMEFRAME_M15,
        "M3": getattr(mt5, "TIMEFRAME_M3", None),
    }
    if timeframe == "M3" and tf_map["M3"] is None:
        return _derive_m3_from_m1(mt5, symbol, start, end)
    candles = _copy_candles_chunked(mt5, symbol, tf_map[timeframe], start, end, _chunk_days(timeframe))
    if timeframe == "M3" and not candles:
        return _derive_m3_from_m1(mt5, symbol, start, end)
    return candles


def _derive_m3_from_m1(mt5: Any, symbol: str, start: datetime, end: datetime) -> list[Candle]:
    source = _copy_candles_chunked(mt5, symbol, mt5.TIMEFRAME_M1, start, end, 14)
    by_time = {item.timestamp: item for item in source}
    derived: list[Candle] = []
    for item in source:
        if item.timestamp.minute % 3 != 0:
            continue
        window = [by_time.get(item.timestamp + timedelta(minutes=offset)) for offset in range(3)]
        if any(candle is None for candle in window):
            continue
        candles = [candle for candle in window if candle is not None]
        derived.append(
            Candle(
                timestamp=item.timestamp,
                open=candles[0].open,
                high=max(candle.high for candle in candles),
                low=min(candle.low for candle in candles),
                close=candles[-1].close,
                volume=sum(candle.volume for candle in candles),
            )
        )
    return derived


def _copy_candles_chunked(
    mt5: Any,
    symbol: str,
    timeframe_id: int,
    start: datetime,
    end: datetime,
    chunk_days: int,
) -> list[Candle]:
    by_time: dict[datetime, Candle] = {}
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=chunk_days) - timedelta(seconds=1), end)
        rates = mt5.copy_rates_range(symbol, timeframe_id, cursor, chunk_end)
        for candle in _rates_to_candles(rates):
            by_time[candle.timestamp] = candle
        cursor = chunk_end + timedelta(seconds=1)
    return [by_time[key] for key in sorted(by_time)]


def _chunk_days(timeframe: str) -> int:
    if timeframe == "H4":
        return 365
    if timeframe == "M15":
        return 60
    return 30


def _rates_to_candles(rates: Any) -> list[Candle]:
    if rates is None or len(rates) == 0:
        return []
    candles: list[Candle] = []
    for rate in rates:
        volume = float(rate["tick_volume"])
        if "real_volume" in rate.dtype.names and float(rate["real_volume"]) > 0:
            volume = float(rate["real_volume"])
        candles.append(
            Candle(
                timestamp=datetime.fromtimestamp(int(rate["time"]), tz=UTC).replace(tzinfo=None),
                open=float(rate["open"]),
                high=float(rate["high"]),
                low=float(rate["low"]),
                close=float(rate["close"]),
                volume=volume,
            )
        )
    return sorted(candles, key=lambda candle: candle.timestamp)


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
                    f"{candle.volume:.0f}",
                    _session_for(candle.timestamp),
                    "false",
                ]
            )


def _session_for(value: datetime) -> str:
    minutes = value.hour * 60 + value.minute
    if 7 * 60 <= minutes < 10 * 60:
        return "LONDON"
    if 13 * 60 <= minutes < 16 * 60:
        return "NY"
    return "OTHER"


def _format_time(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_start(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)


def _date_end(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC) + timedelta(days=1) - timedelta(seconds=1)


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "BLOCKED", "reason": reason, "guardrail": GUARDRAIL}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/market/approved/st_c3"))
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    result = download_st_c3_mt5_dataset(args.data, write_manifest=args.write_manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
