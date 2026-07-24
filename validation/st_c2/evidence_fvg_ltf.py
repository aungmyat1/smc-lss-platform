"""Kernel-facing ST-C2 GC3 FVG/LTF evidence builder."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from validation.st_c2.fvg_confirmation import detect_fvg_chain, detect_ltf_confirmation
from validation.st_c2.identifiers import stable_id
from validation.st_c2.schemas import ConfirmationEvent, FVGEvent
from validation.st_c2.symbols import SymbolMetadata

Candle = dict[str, Any]


@dataclass(frozen=True)
class FVGChainEvidence:
    id: str
    tf: str
    htf_fvg: FVGEvent | None
    mf_fvg: FVGEvent | None
    ltf_fvg: FVGEvent | None
    continuity: bool
    confluence_zone: dict[str, str] | None
    timestamp: str
    provenance: str
    valid: bool
    rejection_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LTFConfirmationEvidence:
    id: str
    tf: str
    choch_event: ConfirmationEvent | None
    internal_bos: ConfirmationEvent | None
    displacement_score: str | None
    valid: bool
    rejection_code: str | None
    timestamp: str
    provenance: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvidenceBuilder:
    def __init__(self, *, spec: dict[str, Any], symbol_metadata: SymbolMetadata, causal_cutoff: str) -> None:
        self.spec = spec
        self.symbol_metadata = symbol_metadata
        self.causal_cutoff = causal_cutoff

    def build_fvg_chain(
        self,
        htf: list[Candle],
        mf: list[Candle],
        ltf: list[Candle],
        *,
        direction: str,
    ) -> FVGChainEvidence:
        events = detect_fvg_chain(
            htf,
            mf,
            ltf,
            direction=direction,
            spec=self.spec,
            symbol_metadata=self.symbol_metadata,
            causal_cutoff=self.causal_cutoff,
        )
        htf_fvg = next((ev for ev in events if ev.timeframe == "H4"), None)
        mf_fvg = next((ev for ev in events if ev.timeframe == "M15"), None)
        ltf_fvg = next((ev for ev in events if ev.timeframe == "M3"), None)
        continuity = mf_fvg is not None and ltf_fvg is not None
        confluence = None
        if mf_fvg is not None:
            confluence = {
                "lower": mf_fvg.reference_levels["lower"],
                "upper": mf_fvg.reference_levels["upper"],
                "source_event_id": mf_fvg.event_id,
            }
        valid = continuity
        attrs = {
            "symbol": self.symbol_metadata.symbol,
            "direction": direction,
            "htf_fvg_id": None if htf_fvg is None else htf_fvg.event_id,
            "mf_fvg_id": None if mf_fvg is None else mf_fvg.event_id,
            "ltf_fvg_id": None if ltf_fvg is None else ltf_fvg.event_id,
            "causal_cutoff": self.causal_cutoff,
        }
        return FVGChainEvidence(
            id=stable_id("fvg_chain", attrs),
            tf="H4/M15/M3",
            htf_fvg=htf_fvg,
            mf_fvg=mf_fvg,
            ltf_fvg=ltf_fvg,
            continuity=continuity,
            confluence_zone=confluence,
            timestamp=self.causal_cutoff,
            provenance="GC3_fvg_ltf_module_v1.0.0",
            valid=valid,
            rejection_code=None if valid else "R4",
        )

    def build_ltf_confirmation(self, ltf: list[Candle], *, direction: str) -> LTFConfirmationEvidence:
        event = detect_ltf_confirmation(
            ltf,
            direction=direction,
            spec=self.spec,
            symbol_metadata=self.symbol_metadata,
            causal_cutoff=self.causal_cutoff,
        )
        attrs = {
            "symbol": self.symbol_metadata.symbol,
            "direction": direction,
            "confirmation_event_id": None if event is None else event.event_id,
            "causal_cutoff": self.causal_cutoff,
        }
        body_ratio = None if event is None else event.metadata.get("body_ratio")
        return LTFConfirmationEvidence(
            id=stable_id("ltf_confirmation_evidence", attrs),
            tf="M3",
            choch_event=event,
            internal_bos=event,
            displacement_score=None if body_ratio is None else str(body_ratio),
            valid=event is not None,
            rejection_code=None if event is not None else "R5",
            timestamp=self.causal_cutoff if event is None else str(event.confirmation_timestamp),
            provenance="GC3_fvg_ltf_module_v1.0.0",
        )
