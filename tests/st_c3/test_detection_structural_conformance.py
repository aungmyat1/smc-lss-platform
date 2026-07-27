"""S1/S2/S4/S5/S6/S8 structural conformance — causal invariance and
determinism against real GBPUSD data.

"Causal invariance" means: evidence computed as of bar i must not change if
bars after i are appended or altered (no lookahead), mirroring the pattern
already established in tests/st_c2/test_structural_conformance.py's
`test_structural_context_is_causal_and_deterministic`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from smc_engine import load_candles  # noqa: E402

from validation.st_c3 import detection as det  # noqa: E402
from validation.st_c3.evidence import load_spec  # noqa: E402

H4_PATH = ROOT / "data" / "GBPUSD_H4.csv"
M15_PATH = ROOT / "data" / "GBPUSD_M15.csv"


@pytest.fixture(scope="module")
def spec():
    return load_spec()


@pytest.fixture(scope="module")
def h4():
    return load_candles(str(H4_PATH))


@pytest.fixture(scope="module")
def m15():
    return load_candles(str(M15_PATH))


def _future_candle(last):
    return {"time": "2099-01-01 00:00", "open": last["close"], "high": last["close"] + 1,
             "low": last["close"] - 1, "close": last["close"]}


def test_htf_bias_evidence_is_causal(h4, spec):
    k = det.htf_bias_params(spec)["k"]
    cutoff = 3000
    events_at_cutoff = det.detect_htf_bias_events(h4[: cutoff + 1], k=k)
    ev_original = det.htf_bias_evidence_at(h4[: cutoff + 1], events_at_cutoff, cutoff, evidence_id="X")

    extended = list(h4[: cutoff + 1]) + [_future_candle(h4[cutoff]) for _ in range(50)]
    events_extended = det.detect_htf_bias_events(extended, k=k)
    ev_extended = det.htf_bias_evidence_at(extended, events_extended, cutoff, evidence_id="X")

    assert ev_original.valid == ev_extended.valid
    assert ev_original.get("bias") == ev_extended.get("bias")
    assert ev_original.get("structure") == ev_extended.get("structure")


def test_sweep_evidence_is_causal(m15, spec):
    params = det.sweep_params(spec)
    cutoff = 3000
    ev_original = det.detect_sweep_at(m15[: cutoff + 1], cutoff, k=2, evidence_id="X", **params)

    extended = list(m15[: cutoff + 1]) + [_future_candle(m15[cutoff]) for _ in range(50)]
    ev_extended = det.detect_sweep_at(extended, cutoff, k=2, evidence_id="X", **params)

    assert ev_original.valid == ev_extended.valid
    assert ev_original.get("sweep_type") == ev_extended.get("sweep_type")
    assert ev_original.get("level") == ev_extended.get("level")


def test_displacement_bos_and_dealing_range_are_causal(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    db_params = det.displacement_bos_params(spec)
    window = m15[:3000]
    candidates = det.find_bos_candidates(window, k=k)
    event = candidates[20]

    disp_orig = det.displacement_evidence_for(
        window, event, body_ratio_min=db_params["body_ratio_min"],
        atr_floor_multiplier=db_params["atr_floor_multiplier"], evidence_id="X",
    )
    dr_orig = det.dealing_range_evidence_for(window, event, k=k, evidence_id="X")

    extended = list(window) + [_future_candle(window[-1]) for _ in range(50)]
    disp_ext = det.displacement_evidence_for(
        extended, event, body_ratio_min=db_params["body_ratio_min"],
        atr_floor_multiplier=db_params["atr_floor_multiplier"], evidence_id="X",
    )
    dr_ext = det.dealing_range_evidence_for(extended, event, k=k, evidence_id="X")

    assert disp_orig.valid == disp_ext.valid
    assert disp_orig.get("impulse_strength") == disp_ext.get("impulse_strength")
    assert dr_orig.valid == dr_ext.valid
    assert dr_orig.get("range_size") == dr_ext.get("range_size")


def test_fvg_and_orderblock_evidence_are_causal(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    fv_params = det.fvg_ob_params(spec)
    cutoff = 3000
    window = m15[: cutoff + 1]

    fvg_orig = det.fvg_evidence_near(
        window, cutoff, min_gap_atr_multiplier=fv_params["fvg_min_gap_atr_multiplier"],
        freshness_max_mf_swings=fv_params["fvg_freshness_max_mf_swings"], k=k, evidence_id="X",
    )
    ob_orig = det.order_block_evidence_near(
        window, cutoff, k=k, freshness_max_mf_swings=fv_params["ob_freshness_max_mf_swings"], evidence_id="X",
    )

    extended = list(window) + [_future_candle(window[-1]) for _ in range(50)]
    fvg_ext = det.fvg_evidence_near(
        extended, cutoff, min_gap_atr_multiplier=fv_params["fvg_min_gap_atr_multiplier"],
        freshness_max_mf_swings=fv_params["fvg_freshness_max_mf_swings"], k=k, evidence_id="X",
    )
    ob_ext = det.order_block_evidence_near(
        extended, cutoff, k=k, freshness_max_mf_swings=fv_params["ob_freshness_max_mf_swings"], evidence_id="X",
    )

    assert fvg_orig.valid == fvg_ext.valid
    assert fvg_orig.get("gap_top") == fvg_ext.get("gap_top")
    assert ob_orig.valid == ob_ext.valid
    assert ob_orig.get("ob_high") == ob_ext.get("ob_high")


def test_sweep_reclaim_evidence_is_causal(m15, spec):
    params = det.sweep_reclaim_params(spec)
    sw_params = det.sweep_params(spec)
    sweep_i = None
    sweep_ev = None
    for i in range(2500, 3000):
        candidate = det.detect_sweep_at(m15, i, k=2, evidence_id="X", **sw_params)
        if candidate.valid:
            sweep_i, sweep_ev = i, candidate
            break
    assert sweep_ev is not None, "expected at least one valid sweep in this window"

    window = m15[: sweep_i + params["max_allowed_bars"] + 5]
    ev_original = det.sweep_reclaim_evidence_for(
        window, sweep_i, sweep_ev.get("sweep_type"), sweep_ev.get("level"),
        max_allowed_bars=params["max_allowed_bars"], evidence_id="X",
    )
    extended = list(window) + [_future_candle(window[-1]) for _ in range(50)]
    ev_extended = det.sweep_reclaim_evidence_for(
        extended, sweep_i, sweep_ev.get("sweep_type"), sweep_ev.get("level"),
        max_allowed_bars=params["max_allowed_bars"], evidence_id="X",
    )
    assert ev_original.valid == ev_extended.valid
    assert ev_original.get("reclaimed") == ev_extended.get("reclaimed")
    assert ev_original.get("reclaim_within_bars") == ev_extended.get("reclaim_within_bars")


def test_session_window_evidence_is_pure_function_of_timestamp():
    a = det.session_window_evidence_for({"time": "2026-07-13 08:00"}, evidence_id="X")
    b = det.session_window_evidence_for({"time": "2026-07-13 08:00"}, evidence_id="X")
    assert a.valid == b.valid
    assert a.get("session") == b.get("session")


def test_entry_window_evidence_is_pure_function_of_inputs():
    a = det.entry_window_evidence_for(3, max_allowed_bars=4, timestamp="t", evidence_id="X")
    b = det.entry_window_evidence_for(3, max_allowed_bars=4, timestamp="t", evidence_id="X")
    assert a.valid == b.valid
    assert a.get("inside_window") == b.get("inside_window")


def test_rerun_is_bitwise_deterministic(m15, spec):
    """Same input, called twice, must produce identical results -- no
    hidden state, no randomness, no wall-clock dependence."""
    k = det.htf_bias_params(spec)["k"]
    params = det.sweep_params(spec)
    window = m15[:3000]

    run_a = [det.detect_sweep_at(window, i, k=k, evidence_id="X", **params).valid for i in range(500, 600)]
    run_b = [det.detect_sweep_at(window, i, k=k, evidence_id="X", **params).valid for i in range(500, 600)]
    assert run_a == run_b

    candidates_a = det.find_bos_candidates(window, k=k)
    candidates_b = det.find_bos_candidates(window, k=k)
    assert candidates_a == candidates_b
