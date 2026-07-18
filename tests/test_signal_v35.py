"""Fixtures for the v3.5 signal engine, drawn from the ruleset §2/§4 tables.

Validates the FORMULA layer (direction, stop side, tp1 = entry +/- 1R, horizon,
R:R to the pre-selected DOL, determinism). Detection of live zones is separate.
Run: python -m pytest -q
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import signal_v35 as sg
from signal_v35 import Structure, generate_signal, VARIANT_TABLE

# variant -> (symbol, direction, entry, primary_tp)  [source: ruleset §4 chart values]
FIXTURES = {
    "E1M1": ("XAUUSD",  "SELL", 1913.65, 1898.0),
    "E1M2": ("ETHUSDT", "BUY",  1171.55, 1219.0),
    "E1M3": ("EURUSD",  "SELL", 1.11357, 1.10875),
    "E2M1": ("EURGBP",  "SELL", 0.87001, 0.86730),
    "E2M2": ("CHFJPY",  "BUY",  162.35,  164.02),
    "E2M3": ("BTCUSDT", "SELL", 26699.0, 25324.7),
    "E3M1": ("GBPJPY",  "BUY",  165.582, 167.32),
    "E3M3": ("EURUSD",  "SELL", 1.09534, 1.09150),
}


def _structure_around(entry, direction, primary_tp):
    d = abs(entry) * 0.001 or 0.001            # symmetric zone around the entry anchor
    if direction == "SELL":                    # swept BSL sits above for a sell
        return Structure(zone_low=entry - d, zone_high=entry + d,
                         swept_level=entry + 2 * d, displacement_origin=entry + 1.5 * d,
                         inducement=entry + 1.2 * d, primary_tp=primary_tp)
    return Structure(zone_low=entry - d, zone_high=entry + d,
                     swept_level=entry - 2 * d, displacement_origin=entry - 1.5 * d,
                     inducement=entry - 1.2 * d, primary_tp=primary_tp)


def test_signal_invariants_per_variant():
    # v3.6 Sec 1: direction is supplied by the caller (the historically
    # observed direction for each fixture), not looked up from VARIANT_TABLE.
    for variant, (sym, direction, entry, tp) in FIXTURES.items():
        e_trig, m_mod = variant[:2], variant[2:]
        s = _structure_around(entry, direction, tp)
        sig = generate_signal(e_trig, m_mod, sym, s, direction)
        assert sig is not None, variant
        assert sig["direction"] == direction, variant
        assert sig["horizon"] == VARIANT_TABLE[variant]["horizon"], variant
        if direction == "SELL":                # stop above, targets below
            assert sig["stop"] > sig["entry"], variant
            assert sig["tp1_1R"] < sig["entry"], variant
            assert sig["primary_tp"] < sig["entry"], variant
        else:                                  # stop below, targets above
            assert sig["stop"] < sig["entry"], variant
            assert sig["tp1_1R"] > sig["entry"], variant
            assert sig["primary_tp"] > sig["entry"], variant
        assert sig["risk_per_unit"] > 0, variant


def test_variants_are_direction_neutral_not_locked():
    # v3.6 Sec 1: v3.5 hard-locked one direction per variant (e.g. E1M1 was
    # always SELL, baked from a single historical chart) — structurally
    # unable to trade the mirror direction even in the opposite regime. Prove
    # the engine will now happily fire the OPPOSITE direction for the same
    # variant given a mirrored structure, for a sample of variants.
    for variant in ("E1M1", "E2M2", "E3M3"):
        e_trig, m_mod = variant[:2], variant[2:]
        _sym, observed_dir, entry, _tp = FIXTURES[variant]
        mirror_dir = "BUY" if observed_dir == "SELL" else "SELL"
        # a generously far target (not the original fixture's tp distance,
        # which doesn't necessarily clear min_rr under every model's stop
        # formula) — the point here is proving direction-neutrality, not
        # reproducing the original R:R.
        d = abs(entry) * 0.001 or 0.001
        mirror_tp = entry - 10 * d if mirror_dir == "SELL" else entry + 10 * d
        s = _structure_around(entry, mirror_dir, mirror_tp)
        sig = generate_signal(e_trig, m_mod, "EURUSD", s, mirror_dir)
        assert sig is not None and sig["decision"] == "SIGNAL", variant
        assert sig["direction"] == mirror_dir, variant


def test_tp1_is_exactly_one_R():
    s = _structure_around(1.10000, "SELL", 1.09000)
    sig = generate_signal("E1", "M3", "EURUSD", s, "SELL")
    r = sig["risk_per_unit"]
    assert abs((sig["entry"] - sig["tp1_1R"]) - r) < 1e-6


def test_rr_gate_rejects_short_target():
    # primary_tp only 0.2R away -> must be rejected by min_rr
    s = Structure(zone_low=0.9999, zone_high=1.0001, swept_level=1.0003, primary_tp=0.99996)
    sig = generate_signal("E2", "M1", "EURUSD", s, "SELL", min_rr=2.0)
    assert sig["decision"] == "REJECT_RR"


def test_no_target_is_rejected_not_auto_passed():
    # v3.6 spec Sec 11: primary_tp=None must REJECT, not silently clear the
    # R:R gate (the v3.5 defect: realized_rr=None used to count as "ok").
    s = Structure(zone_low=0.9999, zone_high=1.0001, swept_level=1.0003, primary_tp=None)
    sig = generate_signal("E2", "M1", "EURUSD", s, "SELL", min_rr=2.0)
    assert sig["decision"] == "REJECT_NO_TARGET"
    assert sig["rr_to_primary_tp"] is None


def test_invalid_variant_returns_none():
    s = _structure_around(1.10000, "SELL", 1.09000)
    assert generate_signal("E4", "M1", "EURUSD", s, "SELL") is None   # no such E-trigger
    assert generate_signal("E1", "M9", "EURUSD", s, "SELL") is None   # no such M-model


def test_invalid_direction_returns_none():
    s = _structure_around(1.10000, "SELL", 1.09000)
    assert generate_signal("E1", "M1", "EURUSD", s, "SIDEWAYS") is None


def test_stop_always_on_correct_side_by_construction():
    # entry is the zone midpoint, so SELL stop is always above entry, BUY below.
    for variant, (sym, direction, entry, tp) in FIXTURES.items():
        s = _structure_around(entry, direction, tp)
        sig = generate_signal(variant[:2], variant[2:], sym, s, direction)
        if direction == "SELL":
            assert sig["stop"] >= s.zone_high, variant
        else:
            assert sig["stop"] <= s.zone_low, variant


def test_determinism():
    s = _structure_around(26699.0, "SELL", 25324.7)
    a = generate_signal("E2", "M3", "BTCUSD", s, "SELL")
    b = generate_signal("E2", "M3", "BTCUSD", s, "SELL")
    assert a == b


def _bear_fvg_series():
    """Hand-built M5 for M1 SELL: builds a confirmed swing high, then a
    bearish sweep (wick above the swing, body closes below it), then a
    3-candle bearish FVG that forms AFTER the sweep.

    M1 §7 ordering: sweep_i < fvg_i. The sweep must be confirmed (k=2
    following bars needed), so we pad with 2 post-sweep bars before the FVG.
    Timestamps are London-session UTC so _in_session() passes in analyze().
    """
    def bar(ts, o, h, l, c):
        return {"time": ts, "open": o, "high": h, "low": l, "close": c}
    # 6 bars building price up to form a swing high around 1.1060
    baseline = [
        bar("2026-01-05 07:00", 1.1000, 1.1010, 1.0995, 1.1005),
        bar("2026-01-05 07:05", 1.1005, 1.1020, 1.1000, 1.1018),
        bar("2026-01-05 07:10", 1.1018, 1.1040, 1.1015, 1.1038),
        bar("2026-01-05 07:15", 1.1038, 1.1060, 1.1030, 1.1058),  # swing high candidate
        bar("2026-01-05 07:20", 1.1058, 1.1059, 1.1030, 1.1032),  # k=1 confirm
        bar("2026-01-05 07:25", 1.1032, 1.1035, 1.1020, 1.1025),  # k=2 confirm -> swing high @ 1.1060 confirmed
    ]
    # Bearish sweep: wick pierces 1.1060, body closes below it
    sweep = bar("2026-01-05 07:30", 1.1025, 1.1075, 1.1010, 1.1020)  # high 1.1075 > 1.1060, close 1.1020 < 1.1060
    # 2 confirmation bars after sweep (needed for k=2 sweep confirmation)
    post_sweep = [
        bar("2026-01-05 07:35", 1.1020, 1.1025, 1.1005, 1.1010),
        bar("2026-01-05 07:40", 1.1010, 1.1015, 1.1000, 1.1005),
    ]
    # 3-candle bearish FVG: c[i-2].low > c[i].high
    fvg = [
        bar("2026-01-05 07:45", 1.1005, 1.1008, 1.0990, 1.0992),  # low 1.0990
        bar("2026-01-05 07:50", 1.0992, 1.0995, 1.0980, 1.0983),  # middle
        bar("2026-01-05 07:55", 1.0983, 1.0985, 1.0960, 1.0962),  # high 1.0985 < 1.0990 => bearish FVG
    ]
    return baseline + [sweep] + post_sweep + fvg


def test_detect_structure_m1_finds_bear_fvg():
    """M1 SELL: sweep precedes the bearish FVG — ordering gate must pass."""
    st = sg.detect_structure_m1(_bear_fvg_series(), "SELL")
    assert st is not None, "expected M1 structure but got None"
    assert st.zone_high > st.zone_low


def test_detect_structure_m1_none_without_sweep():
    """M1 requires a sweep before the FVG — no sweep => None."""
    def bar(o, h, l, c):
        return {"time": "2026-01-05 07:00", "open": o, "high": h, "low": l, "close": c}
    # Only a bearish FVG, no sweep candle
    no_sweep = [
        bar(1.1050, 1.1052, 1.1040, 1.1041),
        bar(1.1041, 1.1042, 1.1030, 1.1031),
        bar(1.1020, 1.1021, 1.1010, 1.1011),
    ]
    assert sg.detect_structure_m1(no_sweep, "SELL") is None


def test_analyze_returns_no_signal_dict_not_crash():
    out = sg.analyze("EURUSD", _bear_fvg_series())
    assert isinstance(out, dict) and "decision" in out


# --- M3 IFVG (v3.6 spec Sec 5-7): sweep -> ATR displacement -> opposite-
# polarity FVG inverted by a full close -> retrace entry. Constructed and
# verified interactively (each negative case confirmed to independently
# return None) rather than hand-derived, since the interacting index
# constraints (displacement window, inversion age, retrace window) are easy
# to get subtly wrong by inspection alone.

def _m3_baseline():
    def bar(o, h, l, c):
        return {"time": "t", "open": o, "high": h, "low": l, "close": c}
    baseline = []
    for i in range(20):
        if i == 15:
            baseline.append(bar(100.0, 100.05, 99.80, 99.85))   # swept low
        elif i in (13, 14, 16, 17):
            baseline.append(bar(100.0, 100.05, 99.90, 100.0))   # confirms it (k=2)
        else:
            baseline.append(bar(100.0, 100.05, 99.95, 100.0))
    return baseline


def _m3_bull_fixture():
    def bar(o, h, l, c):
        return {"time": "t", "open": o, "high": h, "low": l, "close": c}
    sweep = bar(99.85, 99.90, 99.70, 99.86)          # bull sweep of the 99.80 low
    disp = [                                          # ATR-qualified bullish displacement
        bar(99.86, 100.80, 99.80, 100.75),
        bar(100.75, 101.70, 100.70, 101.65),
        bar(101.65, 102.60, 101.60, 102.55),
    ]
    pullback = bar(100.60, 100.65, 99.50, 99.60)      # bear FVG vs disp[1] (low 100.70 > high 100.65)
    inversion = bar(99.60, 100.95, 99.55, 100.90)     # closes above fv.upper (100.70) -> inverts
    retrace = bar(100.90, 100.95, 100.60, 100.80)     # >=50% retrace bar (>= mid 100.675)
    return _m3_baseline() + [sweep] + disp + [pullback, inversion, retrace]


def test_detect_structure_m3_finds_valid_ifvg_setup():
    st = sg.detect_structure_m3(_m3_bull_fixture(), "BUY")
    assert st is not None
    assert st.zone_low == 100.65 and st.zone_high == 100.70
    assert st.zone_creation_i == 24


def test_detect_structure_m3_none_without_displacement():
    def bar(o, h, l, c):
        return {"time": "t", "open": o, "high": h, "low": l, "close": c}
    weak = [bar(99.86, 99.91, 99.81, 99.87) for _ in range(3)]
    pullback = bar(99.60, 99.65, 99.50, 99.60)
    inversion = bar(99.60, 99.95, 99.55, 99.90)
    retrace = bar(99.90, 99.95, 99.60, 99.80)
    m5 = _m3_baseline() + [bar(99.85, 99.90, 99.70, 99.86)] + weak + [pullback, inversion, retrace]
    assert sg.detect_structure_m3(m5, "BUY") is None


def test_detect_structure_m3_none_without_inversion():
    def bar(o, h, l, c):
        return {"time": "t", "open": o, "high": h, "low": l, "close": c}
    sweep = bar(99.85, 99.90, 99.70, 99.86)
    disp = [
        bar(99.86, 100.80, 99.80, 100.75),
        bar(100.75, 101.70, 100.70, 101.65),
        bar(101.65, 102.60, 101.60, 102.55),
    ]
    pullback = bar(100.60, 100.65, 99.50, 99.60)
    no_inversion_1 = bar(99.60, 100.60, 99.55, 100.60)     # never closes above fv.upper (100.70)
    no_inversion_2 = bar(100.60, 100.65, 100.55, 100.60)
    m5 = _m3_baseline() + [sweep] + disp + [pullback, no_inversion_1, no_inversion_2]
    assert sg.detect_structure_m3(m5, "BUY") is None


def test_detect_structure_m3_none_before_retrace_bar_exists():
    # inversion just happened on the LAST bar of the window -> no retrace
    # bar has occurred yet (Sec 7: retrace must be strictly after inversion).
    m5 = _m3_bull_fixture()[:-1]     # drop the retrace bar, ending right at inversion
    assert sg.detect_structure_m3(m5, "BUY") is None
