#!/usr/bin/env python3
"""ST-C3 existence-check *readiness* pass — not R-18 itself.

`tools/existence_check.py` is spec-agnostic: it scans a sequence and tallies
signal-fn outcomes vs. rejection codes. This module proves the ST-C3 kernel
(`validation/st_c3/kernel.py`) is wire-compatible with that tool by running
it over a small, hand-built set of evidence bundles.

This is deliberately NOT the R-18 existence-check floor computation the
frozen spec's `rcr_preregistration.existence_check_floor` still leaves
`UNRESOLVED`. A real R-18 pass needs a signal_fn that derives evidence from
actual historical candles, which requires the sweep/displacement/freshness
detection thresholds that are still `UNRESOLVED`/`PROVISIONAL` in
`specs/st-c3_v1.0.1.yaml` (see `validation/st_c3/__init__.py`). Running this
module only demonstrates mechanical readiness, not a real signal-rate result.
"""
from __future__ import annotations

from typing import Sequence

from tools.existence_check import ExistenceOutcome, run_existence_check, write_existence_report
from validation.st_c3.kernel import EvidenceBundle, run_kernel

from validation.st_c3._readiness_bundles import readiness_bundles


def bundle_signal_fn(bundles: Sequence[EvidenceBundle]):
    def _signal_fn(_candles: Sequence[EvidenceBundle], i: int) -> ExistenceOutcome:
        result = run_kernel(bundles[i])
        if result.outcome == "VALID":
            return ExistenceOutcome(signal=True)
        if result.outcome == "REJECTED":
            return ExistenceOutcome(signal=False, rejection_code=result.rejection.code)
        return ExistenceOutcome(signal=False, rejection_code="NOT_STARTED")

    return _signal_fn


def run_readiness_pass():
    bundles = readiness_bundles()
    result = run_existence_check(
        spec_id="ST-C3_v1.0.1_READINESS",
        symbol="SYNTHETIC",
        timeframe="EVIDENCE_BUNDLE",
        candles=bundles,
        signal_fn=bundle_signal_fn(bundles),
    )
    return result


if __name__ == "__main__":
    res = run_readiness_pass()
    path = write_existence_report(res, out_dir="reports/existence")
    print(f"Wrote {path}")
    print(res.to_dict())
