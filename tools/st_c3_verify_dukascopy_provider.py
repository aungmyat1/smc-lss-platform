#!/usr/bin/env python3
"""Verify a limited Dukascopy provider sample for ST-C3 data qualification.

This is provider qualification only. It does not build or approve the full
dataset, open replay, or modify validation gates.
"""
from __future__ import annotations

import argparse
import json
import lzma
import struct
import urllib.request
from collections import OrderedDict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterable

BASE_URL = "https://datafeed.dukascopy.com/datafeed"
GUARDRAIL = "Provider verification does not approve a dataset or unblock replay."


@dataclass(frozen=True)
class Tick:
    timestamp: datetime
    ask: float
    bid: float
    ask_volume: float
    bid_volume: float


def verify_dukascopy_sample(
    *,
    symbols: Iterable[str] = ("EURUSD", "GBPUSD"),
    hours: Iterable[datetime] = (datetime(2024, 1, 2, 0, tzinfo=UTC), datetime(2024, 1, 2, 1, tzinfo=UTC)),
    cache_dir: str | Path = Path("data/market/raw/dukascopy_sample"),
) -> dict[str, object]:
    results: list[dict[str, object]] = []
    for symbol in symbols:
        for hour in hours:
            ticks = _load_hour(symbol, hour, Path(cache_dir))
            minute_bars = _minute_bid_bars(ticks)
            results.append(
                {
                    "symbol": symbol,
                    "hour_utc": hour.strftime("%Y-%m-%dT%H:00:00Z"),
                    "ticks": len(ticks),
                    "first_tick": ticks[0].timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if ticks else None,
                    "last_tick": ticks[-1].timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if ticks else None,
                    "monotonic_ticks": _monotonic(ticks),
                    "minute_bars": len(minute_bars),
                    "minute_gap_count": _minute_gap_count(minute_bars, hour),
                    "ohlc_valid": all(bar["high"] >= max(bar["open"], bar["close"]) and bar["low"] <= min(bar["open"], bar["close"]) and bar["high"] >= bar["low"] for bar in minute_bars.values()),
                }
            )
    passed = all(
        item["ticks"]
        and item["monotonic_ticks"]
        and item["minute_bars"] == 60
        and item["minute_gap_count"] == 0
        and item["ohlc_valid"]
        for item in results
    )
    return {
        "stage": "provider_verification",
        "provider": "Dukascopy",
        "status": "PASS" if passed else "BLOCKED",
        "reason": "limited sample passed provider verification" if passed else "limited sample failed provider verification",
        "details": {"samples": results},
        "guardrail": GUARDRAIL,
    }


def _load_hour(symbol: str, hour: datetime, cache_dir: Path) -> list[Tick]:
    path = _download_hour(symbol, hour, cache_dir)
    return _parse_bi5_ticks(path.read_bytes(), hour, symbol)


def _download_hour(symbol: str, hour: datetime, cache_dir: Path) -> Path:
    hour = hour.astimezone(UTC)
    path = cache_dir / symbol / f"{hour:%Y_%m_%d_%H}h_ticks.bi5"
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_URL}/{symbol}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/{hour.hour:02d}h_ticks.bi5"
    request = urllib.request.Request(url, headers={"User-Agent": "smc-lss-platform provider qualification"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    if not payload:
        raise ValueError(f"Dukascopy returned empty payload for {symbol} {hour.isoformat()}")
    path.write_bytes(payload)
    return path


def _parse_bi5_ticks(payload: bytes, hour: datetime, symbol: str) -> list[Tick]:
    decoded = lzma.decompress(payload)
    if len(decoded) % 20:
        raise ValueError("Dukascopy tick payload length is not divisible by 20")
    scale = _price_scale(symbol)
    ticks: list[Tick] = []
    hour = hour.astimezone(UTC)
    for offset in range(0, len(decoded), 20):
        millisecond, ask, bid, ask_volume, bid_volume = struct.unpack(">IIIff", decoded[offset : offset + 20])
        ticks.append(
            Tick(
                timestamp=hour + timedelta(milliseconds=millisecond),
                ask=ask / scale,
                bid=bid / scale,
                ask_volume=float(ask_volume),
                bid_volume=float(bid_volume),
            )
        )
    return ticks


def _price_scale(symbol: str) -> float:
    return 1000.0 if symbol.endswith("JPY") else 100000.0


def _minute_bid_bars(ticks: list[Tick]) -> OrderedDict[datetime, dict[str, float]]:
    grouped: OrderedDict[datetime, list[float]] = OrderedDict()
    for tick in ticks:
        minute = tick.timestamp.replace(second=0, microsecond=0)
        grouped.setdefault(minute, []).append(tick.bid)
    bars: OrderedDict[datetime, dict[str, float]] = OrderedDict()
    for minute, prices in grouped.items():
        bars[minute] = {
            "open": prices[0],
            "high": max(prices),
            "low": min(prices),
            "close": prices[-1],
        }
    return bars


def _minute_gap_count(bars: OrderedDict[datetime, dict[str, float]], hour: datetime) -> int:
    expected = {hour.astimezone(UTC).replace(minute=minute, second=0, microsecond=0) for minute in range(60)}
    return len(expected - set(bars))


def _monotonic(ticks: list[Tick]) -> bool:
    return all(current.timestamp >= previous.timestamp for previous, current in zip(ticks, ticks[1:]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("data/market/raw/dukascopy_sample"))
    args = parser.parse_args()
    result = verify_dukascopy_sample(cache_dir=args.cache)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
