from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation import st_c2_reference as stc2  # noqa: E402


def bar(t, o, h, l, c):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


def _positive_bull_windows():
    htf = [
        bar("2026-01-01 00:00", 1.1000, 1.1050, 1.0980, 1.1010),
        bar("2026-01-01 04:00", 1.1010, 1.1080, 1.0990, 1.1060),
        bar("2026-01-01 08:00", 1.1060, 1.1120, 1.1040, 1.1100),
        bar("2026-01-01 12:00", 1.1100, 1.1200, 1.1080, 1.1150),
        bar("2026-01-01 16:00", 1.1150, 1.1160, 1.1060, 1.1080),
        bar("2026-01-01 20:00", 1.1080, 1.1100, 1.1010, 1.1030),
        bar("2026-01-02 00:00", 1.1030, 1.1060, 1.0980, 1.1000),
        bar("2026-01-02 04:00", 1.1000, 1.1040, 1.0950, 1.0980),
        bar("2026-01-02 08:00", 1.0980, 1.1050, 1.0970, 1.1030),
        bar("2026-01-02 12:00", 1.1030, 1.1120, 1.1020, 1.1100),
        bar("2026-01-02 16:00", 1.1100, 1.1230, 1.1090, 1.1210),
        bar("2026-01-02 20:00", 1.1000, 1.1030, 1.0940, 1.1010),
        bar("2026-01-03 00:00", 1.1010, 1.1180, 1.1000, 1.1120),
    ]
    mf = [
        bar("2026-01-02 00:00", 1.1000, 1.1002, 1.0997, 1.0999),
        bar("2026-01-02 00:15", 1.0999, 1.1001, 1.0996, 1.0998),
        bar("2026-01-02 00:30", 1.1006, 1.1012, 1.1005, 1.1010),
        bar("2026-01-02 00:45", 1.1010, 1.1011, 1.0992, 1.1010),
    ]
    ltf = [
        bar("2026-01-02 00:00", 1.0990, 1.1000, 1.0988, 1.0995),
        bar("2026-01-02 00:03", 1.0995, 1.1005, 1.0990, 1.1000),
        bar("2026-01-02 00:06", 1.1000, 1.1010, 1.1005, 1.1008),
        bar("2026-01-02 00:09", 1.1008, 1.1009, 1.0999, 1.1002),
        bar("2026-01-02 00:12", 1.1002, 1.1003, 1.0998, 1.1000),
        bar("2026-01-02 00:15", 1.1000, 1.1001, 1.0997, 1.0999),
        bar("2026-01-02 00:18", 1.0999, 1.1015, 1.0998, 1.1012),
    ]
    return htf, mf, ltf


def _mirror_bear_windows():
    htf, mf, ltf = _positive_bull_windows()
    def mirror(c):
        return {**c, "open": 3 - c["open"], "high": 3 - c["low"], "low": 3 - c["high"], "close": 3 - c["close"]}
    return [mirror(c) for c in htf], [mirror(c) for c in mf], [mirror(c) for c in ltf]


def test_spec_is_frozen_gbpusd_only():
    spec = stc2.load_spec()
    assert spec["status"] == "frozen"
    assert spec["implementation_authorization"] == "scoped_reference_implementation_granted"
    assert stc2.enabled_symbols(spec) == ["GBPUSD"]


def test_positive_golden_case_emits_signal():
    result = stc2.analyze_windows(*_positive_bull_windows())
    assert result.decision == "SIGNAL"
    assert result.symbol == "GBPUSD"
    assert result.direction == "long"
    assert all(stage.passed for stage in result.stages)
    assert result.stages[0].detail["bias_event_id"].startswith("STRUCTURE-")
    assert result.stages[1].detail["sweep"]["metadata"]["reclaim_status"] == "reclaimed"
    assert result.stages[2].detail["ote"]["range_id"].startswith("DEALING_RANGE-")


def test_negative_without_liquidity_rejects_r1():
    htf, mf, ltf = _positive_bull_windows()
    no_sweep_htf = list(htf)
    no_sweep_htf[-2] = bar("2026-01-02 20:00", 1.1000, 1.1030, 1.0960, 1.1010)
    result = stc2.analyze_windows(no_sweep_htf, mf, ltf)
    assert result.decision == "NO_SIGNAL"
    assert result.rejection_code == "R1"


def test_negative_without_structural_bias_rejects_r2():
    htf, mf, ltf = _positive_bull_windows()
    flat_htf = [bar(c["time"], 1.1000, 1.1002, 1.0998, 1.1000) for c in htf]
    result = stc2.analyze_windows(flat_htf, mf, ltf)
    assert result.decision == "NO_SIGNAL"
    assert result.rejection_code == "R2"


def test_bearish_mirror_emits_short_signal():
    result = stc2.analyze_windows(*_mirror_bear_windows())
    assert result.decision == "SIGNAL"
    assert result.direction == "short"


def test_cutoff_invariance_when_future_bars_excluded():
    htf, mf, ltf = _positive_bull_windows()
    future = bar("2099-01-01 00:00", 9, 10, 8, 9)
    original = stc2.analyze_windows(htf, mf, ltf)
    resliced = stc2.analyze_windows((htf + [future])[: len(htf)], (mf + [future])[: len(mf)], (ltf + [future])[: len(ltf)])
    assert original == resliced


def test_deterministic_clean_vs_rerun():
    result1 = stc2.analyze_windows(*_positive_bull_windows())
    result2 = stc2.analyze_windows(*_positive_bull_windows())
    assert result1 == result2


def test_no_broker_imports_in_reference_kernel():
    assert stc2.no_broker_import_guard()
