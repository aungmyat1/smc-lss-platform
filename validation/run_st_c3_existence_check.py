#!/usr/bin/env python3
"""R-18 existence-check runner: real GBPUSD H4/M15/M3 data through the real
ST-C3 funnel (validation.st_c3.evidence_builder + validation.st_c3.kernel),
via the generic tools/existence_check.py harness — no changes to that
module, matching its `SignalFn` contract exactly (candles=M15 series, i=MF
bar index).

EURUSD is excluded: its H4 (19 rows)/M15 (21 rows) CSVs cover only a few
hours, already flagged as insufficient for distribution research in
R27_R30_RESEARCH_REPORT.md — nowhere near enough for a real signal-rate run.
GBPUSD's H4/M15/M3 series overlap for 2026-06-05 through 2026-07-24 (bounded
by M3's start date), which is the window actually scanned.

Research tool only — no execution, optimization, demo, or live trading.
Governed by NEXT_ACTION.md / docs/RESEARCH-CHARTER.md; this run is within
A2/S1-G2's existing `existence_check_conformance_run` scope.
"""
from __future__ import annotations

import bisect

from src import smc_engine as engine
from tools.existence_check import ExistenceOutcome, run_existence_check, write_existence_report
from validation.st_c3.evidence_builder import build_evidence_bundle
from validation.st_c3.kernel import run_kernel


def main() -> None:
    htf = engine.load_candles("data/GBPUSD_H4.csv")
    mf = engine.load_candles("data/GBPUSD_M15.csv")
    ltf = engine.load_candles("data/GBPUSD_M3.csv")

    ltf_start = ltf[0]["time"]
    start_idx = bisect.bisect_left([c["time"] for c in mf], ltf_start)
    warmup = max(start_idx, 200)   # also give HTF/MF swing detection enough runway

    def signal_fn(candles, i):
        bundle = build_evidence_bundle(candles, i, spec=None, htf_candles=htf, ltf_candles=ltf)
        result = run_kernel(bundle)
        return ExistenceOutcome(
            signal=(result.outcome == "VALID"),
            rejection_code=(result.rejection.code if result.rejection else None),
        )

    result = run_existence_check(
        spec_id="ST-C3_v1.0.6", symbol="GBPUSD", timeframe="M15",
        candles=mf, signal_fn=signal_fn, warmup_bars=warmup,
    )
    out_path = write_existence_report(result, out_dir="reports/existence")
    print(f"Scanned {result.total_windows} windows ({mf[warmup]['time']} -> {mf[-1]['time']})")
    print(f"Signals: {result.signals} (rate={result.to_dict()['signal_rate']:.6f})")
    print(f"Rejections by code: {result.rejections_by_code}")
    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
