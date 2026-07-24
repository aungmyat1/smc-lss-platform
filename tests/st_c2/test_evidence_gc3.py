from __future__ import annotations

from validation import st_c2_reference as stc2
from validation.st_c2.evidence_gc3 import EvidenceBuilder, FVGChainEvidence, LTFConfirmationEvidence
from validation.st_c2.symbols import load_symbol_metadata


def bar(t, o, h, l, c):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


def _builder():
    return EvidenceBuilder(
        spec=stc2.load_spec(),
        symbol_metadata=load_symbol_metadata("GBPUSD"),
        causal_cutoff="2026-01-03 00:00",
    )


def _fvg_frames():
    htf = [
        bar("2026-01-01 00:00", 1.0990, 1.1000, 1.0980, 1.0995),
        bar("2026-01-01 04:00", 1.0995, 1.1002, 1.0990, 1.1000),
        bar("2026-01-01 08:00", 1.1008, 1.1015, 1.1005, 1.1010),
    ]
    mf = [
        bar("2026-01-01 00:00", 1.0990, 1.1002, 1.0988, 1.0995),
        bar("2026-01-01 00:15", 1.0995, 1.1003, 1.0992, 1.1000),
        bar("2026-01-01 00:30", 1.1008, 1.1014, 1.1005, 1.1010),
    ]
    ltf = [
        bar("2026-01-01 00:00", 1.0990, 1.1003, 1.0988, 1.0995),
        bar("2026-01-01 00:03", 1.0995, 1.1004, 1.0992, 1.1000),
        bar("2026-01-01 00:06", 1.1008, 1.1012, 1.1006, 1.1010),
    ]
    return htf, mf, ltf


def _ltf_confirmation_frames():
    return [
        bar("2026-01-02 00:00", 1.0990, 1.1000, 1.0988, 1.0995),
        bar("2026-01-02 00:03", 1.0995, 1.1005, 1.0990, 1.1000),
        bar("2026-01-02 00:06", 1.1000, 1.1010, 1.1005, 1.1008),
        bar("2026-01-02 00:09", 1.1008, 1.1009, 1.0999, 1.1002),
        bar("2026-01-02 00:12", 1.1002, 1.1003, 1.0998, 1.1000),
        bar("2026-01-02 00:15", 1.1000, 1.1001, 1.0997, 1.0999),
        bar("2026-01-02 00:18", 1.0999, 1.1015, 1.0998, 1.1012),
    ]


def test_gc3_builder_emits_valid_fvg_chain_evidence():
    evidence = _builder().build_fvg_chain(*_fvg_frames(), direction="long")
    assert isinstance(evidence, FVGChainEvidence)
    assert evidence.valid
    assert evidence.continuity
    assert evidence.mf_fvg is not None
    assert evidence.ltf_fvg is not None
    assert evidence.confluence_zone is not None
    assert evidence.provenance == "GC3_fvg_ltf_module_v1.0.0"


def test_gc3_builder_rejects_fvg_chain_without_ltf_continuity():
    htf, mf, ltf = _fvg_frames()
    evidence = _builder().build_fvg_chain(htf, mf, ltf[:2], direction="long")
    assert not evidence.valid
    assert not evidence.continuity
    assert evidence.rejection_code == "R4"


def test_gc3_builder_emits_ltf_confirmation_evidence():
    evidence = _builder().build_ltf_confirmation(_ltf_confirmation_frames(), direction="long")
    assert isinstance(evidence, LTFConfirmationEvidence)
    assert evidence.valid
    assert evidence.choch_event is not None
    assert evidence.internal_bos is not None
    assert evidence.displacement_score is not None
    assert evidence.rejection_code is None
    assert evidence.provenance == "GC3_fvg_ltf_module_v1.0.0"


def test_gc3_builder_rejects_ltf_confirmation_without_displacement():
    weak = list(_ltf_confirmation_frames())
    weak[-1] = bar("2026-01-02 00:18", 1.1011, 1.1015, 1.0998, 1.1012)
    evidence = _builder().build_ltf_confirmation(weak, direction="long")
    assert not evidence.valid
    assert evidence.rejection_code == "R5"
