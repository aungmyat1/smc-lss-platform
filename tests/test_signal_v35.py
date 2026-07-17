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


def test_e1_requires_h1_gap_fill_and_reaction_not_fallback():
    def bar(o, h, l, c):
        return {"time": "t", "open": o, "high": h, "low": l, "close": c}

    # Bars 0..2 form a bearish FVG [103, 105].  The final closed H1 candle
    # fills into that gap and rejects below its midpoint, matching slide 53.
    h1 = [
        bar(106, 107, 105, 105.5),
        bar(104.5, 105, 103.5, 104),
        bar(102, 103, 101, 102),
        bar(102, 102.8, 101.5, 102.4),
        bar(103, 104.5, 101.8, 102.2),
    ]
    assert sg.detect_e1_gap_reaction(h1, "SELL")

    no_gap = [bar(100, 101, 99, 100), bar(100, 101, 99, 100),
              bar(100, 101, 99, 100), bar(100, 101, 99, 100)]
    assert not sg.detect_e1_gap_reaction(no_gap, "SELL")
    assert sg.detect_e_trigger(no_gap, "SELL") is None


def test_analyze_returns_no_signal_dict_not_crash():
    out = sg.analyze("EURUSD", _bear_fvg_series())
    assert isinstance(out, dict) and "decision" in out
