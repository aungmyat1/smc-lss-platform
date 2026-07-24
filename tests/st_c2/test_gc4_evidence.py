from __future__ import annotations

import importlib.util
from pathlib import Path

from validation import st_c2_reference as stc2
from validation.st_c2.evidence_gc3 import EvidenceBuilder
from validation.st_c2.evidence_gc4 import (
    DecisionEvidenceBuilder,
    build_rejection_evidence,
    validate_transition_sequence,
)
from validation.st_c2.interfaces import (
    collect_logical_trade_plan,
    collect_rejection_evidence,
    collect_signal_candidate_evidence,
    collect_state_transition_evidence,
)
from validation.st_c2.structure import structural_context
from validation.st_c2.symbols import load_symbol_metadata


def _positive_bull_windows():
    fixture_path = Path(__file__).resolve().parents[1] / "test_st_c2_reference.py"
    spec = importlib.util.spec_from_file_location("st_c2_reference_fixtures", fixture_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load ST-C2 reference fixtures")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._positive_bull_windows()


def _gc4_decision():
    htf, mf, ltf = _positive_bull_windows()
    spec = stc2.load_spec()
    metadata = load_symbol_metadata("GBPUSD")
    context = structural_context(htf, mf, spec=spec, symbol="GBPUSD")
    gc3 = EvidenceBuilder(spec=spec, symbol_metadata=metadata, causal_cutoff=htf[-1]["time"])
    fvg_chain = gc3.build_fvg_chain(htf, mf, ltf, direction="long")
    confirmation = gc3.build_ltf_confirmation(ltf, direction="long")
    return DecisionEvidenceBuilder(spec=spec, symbol_metadata=metadata, causal_cutoff=htf[-1]["time"]).build_decision(
        direction="long",
        signal_timestamp=ltf[-1]["time"],
        bias_event_id=context["bias"].bias_event_id,
        pool=context["pool"],
        sweep=context["sweep"],
        dealing_range=context["range"],
        ote=context["ote"],
        fvg_chain=fvg_chain,
        confirmation=confirmation,
    )


def test_gc4_builds_complete_state_signal_and_trade_plan():
    decision = _gc4_decision()
    assert decision.valid
    assert decision.signal is not None
    assert decision.trade_plan is not None
    assert decision.trade_plan.metadata["research_only"]
    assert decision.trade_plan.metadata["no_order_routing"]
    assert len(decision.transitions) == 9
    assert validate_transition_sequence(decision.transitions) == ()


def test_gc4_interfaces_collect_evidence_from_context():
    decision = _gc4_decision()
    context = {"gc4_decision": decision}
    assert collect_state_transition_evidence(context) == decision.transitions
    assert collect_signal_candidate_evidence(context) == (decision.signal,)
    assert collect_logical_trade_plan(context) == (decision.trade_plan,)
    assert collect_rejection_evidence(context) == ()


def test_gc4_rejection_evidence_is_stable_and_canonical():
    first = build_rejection_evidence(
        symbol="GBPUSD",
        rule_id="STC2-RISK-001",
        rejection_code="R6.NET_R_TOO_LOW",
        reason="net reward/risk below frozen minimum",
        timestamp="2026-01-02 00:18",
        causal_cutoff="2026-01-03 00:00",
        source_event_ids=("A", "B"),
    )
    second = build_rejection_evidence(
        symbol="GBPUSD",
        rule_id="STC2-RISK-001",
        rejection_code="R6.NET_R_TOO_LOW",
        reason="net reward/risk below frozen minimum",
        timestamp="2026-01-02 00:18",
        causal_cutoff="2026-01-03 00:00",
        source_event_ids=("A", "B"),
    )
    assert first == second
    assert first.rejection_id.startswith("REJECTION-")


def test_gc4_detects_illegal_transition_sequence():
    decision = _gc4_decision()
    bad = (decision.transitions[1], decision.transitions[0])
    errors = validate_transition_sequence(bad)
    assert errors
