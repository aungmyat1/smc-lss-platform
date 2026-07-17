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


def test_variant_table_matches_source_directions():
    for variant, (_sym, direction, _e, _tp) in FIXTURES.items():
        assert VARIANT_TABLE[variant]["direction"] == direction, variant


def test_signal_invariants_per_variant():
    for variant, (sym, direction, entry, tp) in FIXTURES.items():
        e_trig, m_mod = variant[:2], variant[2:]
        s = _structure_around(entry, direction, tp)
        sig = generate_signal(e_trig, m_mod, sym, s)
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


def test_tp1_is_exactly_one_R():
    s = _structure_around(1.10000, "SELL", 1.09000)
    sig = generate_signal("E1", "M3", "EURUSD", s)
    r = sig["risk_per_unit"]
    assert abs((sig["entry"] - sig["tp1_1R"]) - r) < 1e-6


def test_rr_gate_rejects_short_target():
    # primary_tp only 0.2R away -> must be rejected by min_rr
    s = Structure(zone_low=0.9999, zone_high=1.0001, swept_level=1.0003, primary_tp=0.99996)
    sig = generate_signal("E2", "M1", "EURUSD", s, min_rr=2.0)
    assert sig["decision"] == "REJECT_RR"


def test_no_target_is_rejected_not_auto_passed():
    # v3.6 spec Sec 11: primary_tp=None must REJECT, not silently clear the
    # R:R gate (the v3.5 defect: realized_rr=None used to count as "ok").
    s = Structure(zone_low=0.9999, zone_high=1.0001, swept_level=1.0003, primary_tp=None)
    sig = generate_signal("E2", "M1", "EURUSD", s, min_rr=2.0)
    assert sig["decision"] == "REJECT_NO_TARGET"
    assert sig["rr_to_primary_tp"] is None


def test_invalid_variant_returns_none():
    s = _structure_around(1.10000, "SELL", 1.09000)
    assert generate_signal("E4", "M1", "EURUSD", s) is None   # no such E-trigger
    assert generate_signal("E1", "M9", "EURUSD", s) is None   # no such M-model


def test_stop_always_on_correct_side_by_construction():
    # entry is the zone midpoint, so SELL stop is always above entry, BUY below.
    for variant, (sym, direction, entry, tp) in FIXTURES.items():
        s = _structure_around(entry, direction, tp)
        sig = generate_signal(variant[:2], variant[2:], sym, s)
        if direction == "SELL":
            assert sig["stop"] >= s.zone_high, variant
        else:
            assert sig["stop"] <= s.zone_low, variant


def test_determinism():
    s = _structure_around(26699.0, "SELL", 25324.7)
    a = generate_signal("E2", "M3", "BTCUSD", s)
    b = generate_signal("E2", "M3", "BTCUSD", s)
    assert a == b


def _bear_fvg_series():
    """Hand-built M5 with a clear 3-candle bearish FVG (c[i-2].low > c[i].high)."""
    def bar(o, h, l, c):
        return {"time": "t", "open": o, "high": h, "low": l, "close": c}
    return [
        bar(1.1050, 1.1052, 1.1040, 1.1041),   # down
        bar(1.1041, 1.1042, 1.1030, 1.1031),   # down (its low 1.1030 > next high => gap)
        bar(1.1020, 1.1021, 1.1010, 1.1011),   # gap: c[0].low? use i=2 -> c[0].low 1.1040 > c[2].high 1.1021
    ]


def test_detect_structure_m1_finds_bear_fvg():
    st = sg.detect_structure_m1(_bear_fvg_series(), "SELL")
    assert st is not None
    assert st.zone_high > st.zone_low


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
