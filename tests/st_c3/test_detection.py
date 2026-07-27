"""Tests for validation.st_c3.detection — real price-level detection
against real GBPUSD H4/M15 data, using the frozen v1.0.5 parameters.

Not exhaustive golden-case coverage (that's tests/st_c3/test_golden_cases.py
against hand-built Evidence); these confirm the detection functions produce
spec-conformant Evidence objects and behave sensibly against real candles.
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


def test_params_match_frozen_spec_values(spec):
    assert det.htf_bias_params(spec) == {"k": 2}
    assert det.sweep_params(spec) == {
        "wick_ratio_min": 0.50,
        "equal_tolerance_atr_mult": 0.10,
        "max_sweep_age_bars": 15,
    }
    assert det.displacement_bos_params(spec) == {
        "body_ratio_min": 0.50,
        "atr_floor_multiplier": 1.0,
        "confirmation_bars": 2,
        "pullback_depth_atr_multiplier": 0.30,
    }
    assert det.fvg_ob_params(spec) == {
        "fvg_min_gap_atr_multiplier": 0.15,
        "ob_freshness_max_mf_swings": 3,
        "fvg_freshness_max_mf_swings": 1,
    }


def test_htf_bias_events_are_spec_conformant_and_deterministic(h4, spec):
    k = det.htf_bias_params(spec)["k"]
    events_a = det.detect_htf_bias_events(h4, k=k)
    events_b = det.detect_htf_bias_events(h4, k=k)
    assert events_a == events_b  # deterministic, same input -> same output
    assert len(events_a) > 0
    assert all(e["bias"] in ("BULLISH", "BEARISH") for e in events_a)
    # no two consecutive events share the same bias (each is a real flip)
    for prev, cur in zip(events_a, events_a[1:]):
        assert prev["bias"] != cur["bias"]

    ev = det.htf_bias_evidence_at(h4, events_a, len(h4) - 1, evidence_id="HTF_BIAS-1")
    assert ev.kind == "HTFBiasEvidence"
    assert ev.tf == ("H4",)
    assert ev.get("bias") in ("BULLISH", "BEARISH", "NONE")
    assert ev.get("structure") in ("HHHL", "LHLL", "UNCLEAR")


def test_htf_bias_before_first_event_is_invalid(h4, spec):
    k = det.htf_bias_params(spec)["k"]
    events = det.detect_htf_bias_events(h4, k=k)
    first_event_index = events[0]["i"]
    ev = det.htf_bias_evidence_at(h4, events, first_event_index - 1, evidence_id="HTF_BIAS-EARLY")
    assert ev.valid is False
    assert ev.get("bias") == "NONE"


def test_sweep_detection_respects_wick_ratio_threshold(m15, spec):
    params = det.sweep_params(spec)
    # A stricter wick-ratio threshold can only reduce (never increase) how
    # often a sweep validates, all else equal.
    lenient = sum(
        1 for i in range(2500, 2600)
        if det.detect_sweep_at(
            m15, i, k=2, wick_ratio_min=0.1,
            equal_tolerance_atr_mult=params["equal_tolerance_atr_mult"],
            max_sweep_age_bars=params["max_sweep_age_bars"], evidence_id=f"SWEEP-{i}",
        ).valid
    )
    strict = sum(
        1 for i in range(2500, 2600)
        if det.detect_sweep_at(
            m15, i, k=2, wick_ratio_min=0.9,
            equal_tolerance_atr_mult=params["equal_tolerance_atr_mult"],
            max_sweep_age_bars=params["max_sweep_age_bars"], evidence_id=f"SWEEP-{i}",
        ).valid
    )
    assert strict <= lenient


def test_sweep_evidence_is_spec_conformant(m15, spec):
    params = det.sweep_params(spec)
    ev = det.detect_sweep_at(m15, 3000, k=2, evidence_id="SWEEP-1", **params)
    assert ev.kind == "SweepEvidence"
    assert ev.get("sweep_type") in ("BUY_SIDE", "SELL_SIDE")
    assert isinstance(ev.get("wick_penetration"), bool)


def test_bos_confirmation_bars_filters_whipsaws(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    candidates = det.find_bos_candidates(m15[:3000], k=k)
    assert candidates
    confirmed_n0 = sum(1 for e in candidates if det.bos_confirmed(m15, e, confirmation_bars=0))
    confirmed_n5 = sum(1 for e in candidates if det.bos_confirmed(m15, e, confirmation_bars=5))
    assert confirmed_n0 == len(candidates)  # N=0 always "confirmed" (no window to fail in)
    assert confirmed_n5 <= confirmed_n0  # more confirmation bars can only reject more


def test_displacement_and_bos_evidence_are_spec_conformant(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    db_params = det.displacement_bos_params(spec)
    candidates = det.find_bos_candidates(m15[:3000], k=k)
    event = candidates[50]
    disp = det.displacement_evidence_for(
        m15, event, body_ratio_min=db_params["body_ratio_min"],
        atr_floor_multiplier=db_params["atr_floor_multiplier"], evidence_id="DISP-1",
    )
    bos = det.bos_evidence_for(m15, event, confirmation_bars=db_params["confirmation_bars"], evidence_id="BOS-1")
    assert disp.kind == "DisplacementEvidence"
    assert bos.kind == "BOSEvidence"
    assert bos.get("bos_direction") in ("UP", "DOWN")
    assert bos.get("body_close_break") is True


def test_bos_extreme_lock_depth_threshold_reduces_lock_rate(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    candidates = det.find_bos_candidates(m15[:5000], k=k)
    shallow = sum(
        1 for e in candidates
        if det.bos_extreme_evidence_for(m15, e, pullback_depth_atr_multiplier=0.1, window=40, evidence_id="X").valid
    )
    deep = sum(
        1 for e in candidates
        if det.bos_extreme_evidence_for(m15, e, pullback_depth_atr_multiplier=1.0, window=40, evidence_id="X").valid
    )
    assert deep <= shallow


def test_dealing_range_evidence_has_positive_range_when_valid(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    candidates = det.find_bos_candidates(m15[:3000], k=k)
    for event in candidates[:20]:
        ev = det.dealing_range_evidence_for(m15, event, k=k, evidence_id="DR-1")
        if ev.valid:
            assert ev.get("range_size") > 0


def test_fvg_and_orderblock_evidence_are_spec_conformant(m15, spec):
    k = det.htf_bias_params(spec)["k"]
    fv_params = det.fvg_ob_params(spec)
    fvg_ev = det.fvg_evidence_near(
        m15, 5000, min_gap_atr_multiplier=fv_params["fvg_min_gap_atr_multiplier"],
        freshness_max_mf_swings=fv_params["fvg_freshness_max_mf_swings"], k=k, evidence_id="FVG-1",
    )
    ob_ev = det.order_block_evidence_near(
        m15, 5000, k=k, freshness_max_mf_swings=fv_params["ob_freshness_max_mf_swings"], evidence_id="OB-1",
    )
    assert fvg_ev.kind == "FVGEvidence"
    assert ob_ev.kind == "OrderBlockEvidence"
    # OTE gate is NOT_YET_SUPPORTED -- inside_ote must never be silently claimed true
    assert fvg_ev.get("inside_ote") is False
    assert ob_ev.get("inside_ote") is False


def test_not_yet_supported_stages_are_documented():
    assert det.NOT_YET_SUPPORTED == (
        "S3_SWEEP_RECLAIM", "S7_OTE", "S9_LTF_CONFIRMATION",
        "S10_SESSION_GATEKEEPER", "S11_ENTRY_WINDOW", "S12_RISK_SLTP",
    )
