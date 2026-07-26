"""Verifies the ST-C3 kernel is wire-compatible with `tools/existence_check.py`.

Not a real R-18 pass — see `validation/run_st_c3_existence_readiness.py`.
"""
from __future__ import annotations

from validation.run_st_c3_existence_readiness import run_readiness_pass


def test_readiness_pass_tallies_signals_and_rejections():
    result = run_readiness_pass()
    assert result.spec_id == "ST-C3_v1.0.1_READINESS"
    assert result.bars_scanned == 4
    assert result.total_windows == 4
    assert result.signals == 1
    assert result.rejections_by_code["R2_NO_SWEEP"] == 1
    assert result.rejections_by_code["R4_NO_OTE_PULLBACK"] == 1
    assert result.rejections_by_code["R8_INVALID_RISK_OR_TARGET"] == 1
