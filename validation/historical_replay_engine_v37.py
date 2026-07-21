#!/usr/bin/env python3
"""Canonical v3.7 / ST-C1 v1.1.0 replay engine.

Subclasses HistoricalReplayEngine (validation/historical_replay_engine.py) to
reuse its cost model (_cost_to_r), management simulator (_simulate_trade_detail),
metrics computation, and replay/orchestration loop UNCHANGED — the ST-C1 v1.0
baseline path (the immutable historical control behind PR #3) is not touched
by this file. Only the signal-generation seam is overridden, using the G1-G9
pure decision module (src/signal_v37.py) instead of live_signal.py's v1
legacy signal — see reports/audit/ST_C1_V37_PRE_EDIT_FINDINGS.md §4 for why
that substitution is the point of this module.

Adds G8 (net reward gate, using the inherited cost model) at the point a
candidate would otherwise become a SignalRecord, and produces a full gate
trace per generate_signal call (candidate_id, strategy_version, symbol,
evaluation_time, G1-G10, final_decision, rejection_code, evidence_ids,
cost_snapshot, data_cutoff), per this task's IMPLEMENTATION ARCHITECTURE
requirement. No failed/unknown gate silently defaults to pass.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import signal_v37 as v37  # noqa: E402

from validation.historical_replay_engine import (
    CandidateRecord,
    HistoricalReplayEngine,
    SignalRecord,
    _is_session_allowed,
    _window,
)


class HistoricalReplayEngineV37(HistoricalReplayEngine):
    """ST-C1 v1.1.0 / spec v3.7 canonical replay. See module docstring."""

    def __init__(self, *args, ablation: dict[str, Any] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        # Locked A0-A3 ablation flags: toggle exactly two rules while every
        # other rule stays identical. See reports/ablation/ST_C1_V37_ABLATION_REPORT.md.
        self.ablation = {
            "location_gate": True,     # False = A0/A2: G4 premium/discount not enforced
            "net_reward_gate": True,   # False = A0/A1: gross 2R gate instead of net 3R
        }
        if ablation:
            self.ablation.update(ablation)
        self.gate_traces: list[dict[str, Any]] = []
        self._consumed_target_levels: set[str] = set()

    def generate_signal(self, index, m5, h1=None, d1=None, *, symbol=None,
                         rejected_candidates=None, funnel_counts=None):
        k = int(self.params.get("swing_lookback_bars", 2))
        if index < max(self.warmup_bars, 3 * k + 2):
            return None
        symbol_name = symbol or self._metadata_for_symbol(None).canonical_symbol

        def bump(key: str, amount: int = 1) -> None:
            if funnel_counts is not None:
                funnel_counts[key] = int(funnel_counts.get(key, 0)) + amount

        bump("evaluated")
        asof_time = m5[index + 1]["time"] if index + 1 < len(m5) else m5[index]["time"]
        # G6's poi_entry->sweep->displacement->choch->retrace chain can only
        # span poi_entry_to_sweep_max_m5_bars + displacement_max_run_bars +
        # displacement_to_choch_max_m5_bars + choch_to_retrace_entry_max_m5_bars
        # bars end-to-end (68 at defaults) BUT the "price enters fresh HTF
        # POI" touch itself can occur any time within the POI's own freshness
        # window (up to htf_poi_max_age_h1_bars H1 bars / d1_gap_max_age_d1_bars
        # D1 bars old). A window sized only to the 68-bar chain budget almost
        # never contains that first touch for an HTF POI that is genuinely
        # days old, so poi_entry_i is silently never found — NOT the same
        # thing as a correctly-evaluated rejection. `m5_poi_entry_search_bars`
        # bounds this search to a tractable width (default below) rather than
        # the full theoretical staleness window (which would be several
        # thousand M5 bars and make a multi-symbol backtest impractically
        # slow) — a disclosed scope-out, not a silent pass: see
        # reports/audit/ST_C1_V37_TRACEABILITY_MATRIX.md G6 row.
        m5_window_bars = int(self.params.get("m5_poi_entry_search_bars", 500))
        m5_window = _window(m5, index, max(m5_window_bars, self.warmup_bars))

        last_time = m5_window[-1]["time"]
        if not _is_session_allowed(last_time, self.sessions, self.session_windows):
            bump("rejected_session")
            self._record_rejection(rejected_candidates, m5, index, symbol_name,
                                    "session", "outside allowed session", "G0_SESSION")
            return None
        bump("session_pass")

        h1_lookback = max(
            int(self.params.get("dealing_range_lookback_h1_bars", 40)),
            int(self.params.get("htf_poi_max_age_h1_bars", 60)), 120)
        d1_lookback = max(int(self.params.get("d1_gap_max_age_d1_bars", 10)), 20)
        h1_window = self._bounded_context_window(h1, "H1", asof_time, h1_lookback) if h1 else None
        d1_window = self._bounded_context_window(d1, "D1", asof_time, d1_lookback) if d1 else None
        if not h1_window or len(h1_window) < 10:
            bump("rejected_g1_bias")
            self._record_rejection(rejected_candidates, m5, index, symbol_name,
                                    "g1_bias", "insufficient H1 context", "G1_NO_CONTEXT")
            return None

        entry_price = m5[index + 1]["open"]
        gate_params = dict(self.params)
        gate_params["_skip_g4"] = not self.ablation.get("location_gate", True)
        candidates = v37.evaluate_candidates(
            m5_window, h1_window, d1_window, entry_price,
            self._consumed_target_levels, gate_params,
        )
        candidate = candidates[0]
        trace = self._new_trace(index, symbol_name, m5_window[-1]["time"], candidate)

        if candidate.decision != "CANDIDATE_READY":
            bump(f"rejected_{candidate.rejection_code.split('_')[0].lower()}")
            self._record_rejection(rejected_candidates, m5, index, symbol_name,
                                    candidate.rejection_code.lower(), candidate.decision,
                                    candidate.rejection_code, direction=candidate.direction or "unknown")
            # G4 rejections that still have G7 (stop) + G9 (target) evidence
            # went through the full G1/G2/G5/G6/G7/G9 chain — only location
            # blocked them. Also compute G8 here so the trace can record BOTH
            # LOCATION and NET_RR evidence together when both are true (see
            # this task's Example 2 fixture requirement).
            if candidate.decision == "REJECT_G4_LOCATION" and "G7" in candidate.gates and "G9" in candidate.gates:
                gates = candidate.gates
                stop, target = gates["G7"]["final_stop"], gates["G9"]["target"]
                try:
                    _, cost = self._cost_to_r(symbol_name, entry_price, stop)
                    risk_distance = abs(entry_price - stop)
                    net_available_rr = (abs(target - entry_price) - cost["price_cost_round_trip"]) / risk_distance
                    min_net_rr = float(self.params.get("min_net_rr", 3.0))
                    trace["G8_reward"] = {
                        "net_available_rr": round(net_available_rr, 4),
                        "gate_applied": "net", "threshold": min_net_rr, "cost_snapshot": cost,
                    }
                    trace["cost_snapshot"] = cost
                    if net_available_rr < min_net_rr:
                        trace["rejection_code"] = "G4_WRONG_SIDE_OF_EQUILIBRIUM"
                        trace["secondary_rejection_codes"] = ["G8_NET_RR_BELOW_THRESHOLD"]
                        bump("rejected_g8_reward")
                except (ValueError, ZeroDivisionError):
                    pass
            self.gate_traces.append(trace)
            return None
        bump("candidate_ready")

        gates = candidate.gates
        stop = gates["G7"]["final_stop"]
        target = gates["G9"]["target"]
        direction = candidate.direction

        # --- G8: net reward gate, using the inherited, single cost model ---
        _, cost = self._cost_to_r(symbol_name, entry_price, stop)
        logical_target_distance = abs(target - entry_price)
        expected_round_trip_cost_price = cost["price_cost_round_trip"]
        risk_distance = abs(entry_price - stop)
        net_available_rr = (logical_target_distance - expected_round_trip_cost_price) / risk_distance
        gross_available_rr = logical_target_distance / risk_distance
        min_net_rr = float(self.params.get("min_net_rr", 3.0))
        min_rr_gross = float(self.params.get("min_rr", 2.0))
        if self.ablation.get("net_reward_gate", True):
            reward_ok = net_available_rr >= min_net_rr
            rr_reason = f"net_available_rr {net_available_rr:.3f} < {min_net_rr}"
            gate_applied, threshold = "net", min_net_rr
        else:
            reward_ok = gross_available_rr >= min_rr_gross
            rr_reason = f"gross_available_rr {gross_available_rr:.3f} < {min_rr_gross}"
            gate_applied, threshold = "gross", min_rr_gross
        trace["G8_reward"] = {
            "net_available_rr": round(net_available_rr, 4),
            "gross_available_rr": round(gross_available_rr, 4),
            "gate_applied": gate_applied, "threshold": threshold,
            "cost_snapshot": cost,
        }
        trace["cost_snapshot"] = cost
        if not reward_ok:
            bump("rejected_g8_reward")
            self._record_rejection(rejected_candidates, m5, index, symbol_name,
                                    "g8_reward", rr_reason, "G8_NET_RR_BELOW_THRESHOLD",
                                    direction=direction)
            trace["final_decision"] = "REJECT_G8_REWARD"
            trace["rejection_code"] = "G8_NET_RR_BELOW_THRESHOLD"
            self.gate_traces.append(trace)
            return None

        sweep_i, choch_i = gates["G6"]["sweep_i"], gates["G6"]["choch_i"]
        structure_identity = self._structure_identity(
            direction=direction,
            canonical_symbol=self._metadata_for_symbol(symbol_name).canonical_symbol,
            source_symbol=symbol_name,
            sweep={"time": m5_window[sweep_i]["time"], "level": gates["G6"]["sweep_level"]},
            poi={**gates["G5"], "type": gates["G5"]["poi_origin"]},
            confirmation_time=m5_window[choch_i]["time"],
            choch_break_level=stop,
            choch_time=m5_window[choch_i]["time"],
        )
        if gates["G9"]["level_id"]:
            self._consumed_target_levels.add(gates["G9"]["level_id"])

        trace["final_decision"] = "SIGNAL"
        trace["rejection_code"] = None
        self.gate_traces.append(trace)

        return SignalRecord(
            index=index, time=m5_window[-1]["time"], direction=direction,
            entry=round(entry_price, 5), stop=round(stop, 5), target=round(target, 5),
            structure_key=structure_identity,
            reason_codes=("G1_G9_PASS", f"G8_{gate_applied.upper()}"),
            structure_identity=structure_identity,
            canonical_symbol=self._metadata_for_symbol(symbol_name).canonical_symbol,
            source_symbol=symbol_name,
            sweep_time=m5_window[sweep_i]["time"], sweep_level=float(gates["G6"]["sweep_level"]),
            poi_type=gates["G5"]["poi_origin"], poi_time=str(gates["G5"]["time"]),
            poi_low=float(gates["G5"]["low"]), poi_high=float(gates["G5"]["high"]),
            confirmation_time=m5_window[choch_i]["time"], choch_time=m5_window[choch_i]["time"],
            choch_direction=direction, choch_break_level=float(stop),
            choch_reason="m5_close_confirmed_choch_or_bos",
        )

    def _new_trace(self, index: int, symbol: str, evaluation_time: str, candidate) -> dict[str, Any]:
        version = "1.1.0"
        if isinstance(self.contract, dict):
            version = str(self.contract.get("strategy", {}).get("version", version))
        return {
            "candidate_id": f"{symbol}:{index}",
            "strategy_version": version,
            "symbol": symbol, "evaluation_time": evaluation_time,
            "G1_bias": candidate.gates.get("G1"), "G2_structure": candidate.gates.get("G2"),
            "G3_confirmation": (candidate.gates.get("G1") or {}).get("last_break"),
            "G4_location": candidate.gates.get("G4"), "G5_confluence": candidate.gates.get("G5"),
            "G6_trigger": candidate.gates.get("G6"), "G7_invalidation": candidate.gates.get("G7"),
            "G8_reward": None, "G9_target": candidate.gates.get("G9"), "G10_management": None,
            "final_decision": candidate.decision, "rejection_code": candidate.rejection_code,
            "secondary_rejection_codes": list(candidate.secondary_rejection_codes),
            "evidence_ids": list(candidate.gates.keys()),
            "cost_snapshot": None, "data_cutoff": evaluation_time,
        }

    def _record_rejection(self, rejected_candidates, m5, index, symbol_name, stage, reason, code,
                           direction: str = "unknown") -> None:
        if rejected_candidates is None:
            return
        rejected_candidates.append(CandidateRecord(
            signal_time=m5[index]["time"], stage=stage, direction=direction,
            structure_key=None, rejection_reason=f"{reason} ({code})", symbol=symbol_name,
            metadata={"rejection_code": code},
        ))
