#!/usr/bin/env python3
"""CLI wrapper for `tools.existence_check` (Lever A).

Usage:
    python scripts/run_existence_for_candidate.py \\
        --spec-id ST-C3 --symbol GBPUSD --timeframe M15 \\
        --candles data/GBPUSD_M15.csv \\
        --signal-fn my_module:my_signal_fn

`--signal-fn` is a "module:function" dotted path. The function must accept
`(candles, index)` and return a `tools.existence_check.ExistenceOutcome`
(`signal=True` on a fire, or `signal=False, rejection_code=...` otherwise).
This script never invents its own strategy detection logic — it only wires
an existing, caller-supplied signal function into the generic existence-check
scanner and writes a JSON report to `reports/existence/`.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (str(ROOT), str(SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

from smc_engine import load_candles  # noqa: E402
from tools.existence_check import run_existence_check, write_existence_report  # noqa: E402


def _resolve_signal_fn(dotted_path: str):
    module_name, _, func_name = dotted_path.partition(":")
    if not module_name or not func_name:
        raise ValueError(f"--signal-fn must be 'module:function', got {dotted_path!r}")
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-id", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--candles", required=True, help="Path to a CSV of OHLC candles")
    parser.add_argument("--signal-fn", required=True, help="'module:function' dotted path")
    parser.add_argument("--warmup-bars", type=int, default=0)
    parser.add_argument("--out-dir", default=str(ROOT / "reports" / "existence"))
    args = parser.parse_args(argv)

    candles = load_candles(args.candles)
    signal_fn = _resolve_signal_fn(args.signal_fn)
    result = run_existence_check(
        spec_id=args.spec_id,
        symbol=args.symbol,
        timeframe=args.timeframe,
        candles=candles,
        signal_fn=signal_fn,
        warmup_bars=args.warmup_bars,
    )
    report_path = write_existence_report(result, out_dir=args.out_dir)
    print(f"spec={result.spec_id} symbol={result.symbol} tf={result.timeframe}")
    print(f"bars_scanned={result.bars_scanned} signals={result.signals} "
          f"signal_rate={result.to_dict()['signal_rate']:.6f}")
    print(f"rejections_by_code={result.rejections_by_code}")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
