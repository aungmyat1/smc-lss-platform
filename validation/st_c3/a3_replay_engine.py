"""ST-C3 A3 historical multi-timeframe replay engine.

Authorized by owner decision, 2026-07-26 ("A3 statistical validation —
OPENED" entry in `reports/validation/st_c3/OWNER_DECISION_LOG.md`), scoped
to `historical_baseline` / `cost_adjusted_backtest` / `walk_forward`
research per `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md`. No broker
integration, demo, live, or Stage B execution exists here or is authorized
by this module.

Reuses the frozen v1.0.6 funnel exactly as A2/S1-G2 built it — this module
adds zero new detection logic:

- `validation.st_c3.evidence_builder.build_evidence_bundle` produces the
  per-bar `EvidenceBundle` (same function R-18's existence check used).
- `validation.st_c3.kernel.run_kernel` evaluates it (same kernel).

The only new logic in this file is post-S13 TradePlan *lifecycle*
simulation (did price reach SL or TP1/TP2/TP3 after the plan was emitted)
and metrics aggregation across a full replay — neither of which existed in
the R-18 existence-check harness, which only asked whether S13 was ever
reached.

Documented limitation: expiry monitoring only checks `SL_BREAK` (a direct
price comparison) and `BIAS_FLIP` (recomputing H4 bias at each subsequent
bar via the same `build_evidence_bundle` call). `ENTRY_WINDOW` expiry does
not apply post-entry, and `SUPERSEDED_SETUP` (a newer, higher-priority
concurrent setup) is not evaluated — this replay engine tracks one open
TradePlan at a time per call and does not implement portfolio-level
setup-priority arbitration. This is a scope limitation, not a hidden bug.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from typing import Optional, Sequence

from validation.st_c3.evidence_builder import build_evidence_bundle
from validation.st_c3.kernel import run_kernel
from validation.st_c3.trade_plan import TradePlan

# Partial-exit fractions per `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md`
# section 9 (planning material, not an R-tracker field — these are
# position-management percentages, not detection-threshold parameters).
TP1_CLOSE_FRACTION = 0.30
TP2_CLOSE_FRACTION = 0.30
TP3_CLOSE_FRACTION = 0.40


@dataclass(frozen=True)
class TargetHit:
    target: str  # "TP1" | "TP2" | "TP3"
    bar_index: int
    timestamp: str
    price: float
    rr: float
    fraction_closed: float


@dataclass(frozen=True)
class TradeLifecycle:
    entry_index: int
    entry_time: str
    direction: str
    entry_price: float
    sl_price: float
    targets: dict  # {"TP1": price, "TP2": price, "TP3": price}
    hits: tuple[TargetHit, ...]
    sl_hit: bool
    sl_hit_index: Optional[int]
    bias_flip_index: Optional[int]
    bars_held: int
    remaining_fraction: float
    realized_rr: float
    unrealized_rr: float
    termination: str  # "SL_HIT" | "ALL_TARGETS_HIT" | "BIAS_FLIP" | "OPEN_AT_DATA_END" | "MAX_HOLD_REACHED"


def _simulate_lifecycle(
    trade_plan: TradePlan,
    mf_candles: Sequence[dict],
    htf_candles: Sequence[dict],
    ltf_candles: Sequence[dict],
    spec,
    entry_index: int,
    max_hold_bars: int,
) -> TradeLifecycle:
    direction = trade_plan.direction  # "LONG" | "SHORT"
    entry_price = float(trade_plan.entry["entry_price"])
    sl_price = float(trade_plan.risk["sl_price"])
    risk = abs(entry_price - sl_price)
    targets = {
        "TP1": (float(trade_plan.targets["tp1"]["price"]), float(trade_plan.targets["tp1"]["rr"])),
        "TP2": (float(trade_plan.targets["tp2"]["price"]), float(trade_plan.targets["tp2"]["rr"])),
        "TP3": (float(trade_plan.targets["tp3"]["price"]), float(trade_plan.targets["tp3"]["rr"])),
    }
    fractions = {"TP1": TP1_CLOSE_FRACTION, "TP2": TP2_CLOSE_FRACTION, "TP3": TP3_CLOSE_FRACTION}
    # Evaluate targets nearest-first (ascending distance from entry), matching
    # partial-exit order in ST-C3_BACKTEST_SPEC.md section 9.
    order = sorted(targets.keys(), key=lambda k: abs(targets[k][0] - entry_price))

    hits: list[TargetHit] = []
    remaining = 1.0
    realized_rr = 0.0
    sl_hit = False
    sl_hit_index: Optional[int] = None
    bias_flip_index: Optional[int] = None
    last_j = entry_index
    n = len(mf_candles)
    end_j = min(entry_index + max_hold_bars, n - 1)

    for j in range(entry_index + 1, end_j + 1):
        last_j = j
        bar = mf_candles[j]

        # SL_BREAK check first (conservative: a bar that touches both SL and
        # a target is scored as the loss, per standard backtest convention).
        sl_touched = (bar["low"] <= sl_price) if direction == "LONG" else (bar["high"] >= sl_price)
        if sl_touched:
            realized_rr += remaining * (-1.0)
            remaining = 0.0
            sl_hit = True
            sl_hit_index = j
            break

        for tgt in list(order):
            if tgt not in [h.target for h in hits]:
                price, rr = targets[tgt]
                touched = (bar["high"] >= price) if direction == "LONG" else (bar["low"] <= price)
                if touched:
                    frac = fractions[tgt]
                    realized_rr += frac * rr
                    remaining -= frac
                    hits.append(TargetHit(
                        target=tgt, bar_index=j, timestamp=bar["time"], price=price, rr=rr,
                        fraction_closed=frac,
                    ))
        if remaining <= 1e-9:
            break

        # BIAS_FLIP check: recompute H4 bias as-of this bar via the same
        # unmodified evidence builder; if it now points the opposite way,
        # terminate per the frozen expiry rule (`kernel.evaluate_expiry`).
        rebuilt = build_evidence_bundle(mf_candles, j, spec, htf_candles=htf_candles, ltf_candles=ltf_candles)
        if rebuilt.htf_bias.valid and rebuilt.htf_bias.get("bias") not in (None,):
            flipped = (
                (direction == "LONG" and rebuilt.htf_bias.get("bias") == "BEARISH")
                or (direction == "SHORT" and rebuilt.htf_bias.get("bias") == "BULLISH")
            )
            if flipped:
                bias_flip_index = j
                break

    if sl_hit:
        termination = "SL_HIT"
    elif remaining <= 1e-9:
        termination = "ALL_TARGETS_HIT"
    elif bias_flip_index is not None:
        termination = "BIAS_FLIP"
    elif last_j >= n - 1:
        termination = "OPEN_AT_DATA_END"
    else:
        termination = "MAX_HOLD_REACHED"

    unrealized_rr = 0.0
    if remaining > 1e-9 and not sl_hit:
        last_close = mf_candles[last_j]["close"]
        signed = (last_close - entry_price) if direction == "LONG" else (entry_price - last_close)
        unrealized_rr = remaining * (signed / risk if risk else 0.0)

    return TradeLifecycle(
        entry_index=entry_index,
        entry_time=mf_candles[entry_index]["time"],
        direction=direction,
        entry_price=entry_price,
        sl_price=sl_price,
        targets={k: v[0] for k, v in targets.items()},
        hits=tuple(hits),
        sl_hit=sl_hit,
        sl_hit_index=sl_hit_index,
        bias_flip_index=bias_flip_index,
        bars_held=last_j - entry_index,
        remaining_fraction=remaining,
        realized_rr=realized_rr,
        unrealized_rr=unrealized_rr,
        termination=termination,
    )


def _default_warmup(mf_candles: Sequence[dict], ltf_candles: Sequence[dict]) -> int:
    ltf_start = ltf_candles[0]["time"]
    start_idx = bisect.bisect_left([c["time"] for c in mf_candles], ltf_start)
    return max(start_idx, 200)


def run_a3_replay(
    symbol: str,
    htf_candles: Sequence[dict],
    mf_candles: Sequence[dict],
    ltf_candles: Sequence[dict],
    spec=None,
    warmup_bars: Optional[int] = None,
    max_hold_bars: int = 500,
) -> dict:
    """Run the frozen v1.0.6 ST-C3 funnel bar-by-bar over `mf_candles`
    (M15, the driving series), simulating TradePlan lifecycle whenever S13
    is reached. Returns a dict of aggregated metrics plus per-bar logs.

    No new detection logic: identical `build_evidence_bundle`/`run_kernel`
    call pattern as `validation/run_st_c3_existence_check.py` (R-18). The
    only addition is post-signal lifecycle simulation and metrics rollup.
    """
    if warmup_bars is None:
        warmup_bars = _default_warmup(mf_candles, ltf_candles)

    logs: list[dict] = []
    rejections: dict[str, int] = {}
    states_reached_counts: dict[str, int] = {}
    session_counts: dict[str, int] = {}
    session_signal_counts: dict[str, int] = {}
    rr_samples: list[float] = []
    lifecycles: list[TradeLifecycle] = []

    bar_count = 0
    signal_count = 0
    n = len(mf_candles)

    for i in range(warmup_bars, n):
        bar_count += 1
        bundle = build_evidence_bundle(mf_candles, i, spec, htf_candles=htf_candles, ltf_candles=ltf_candles)
        result = run_kernel(bundle)

        for st in result.states_reached:
            states_reached_counts[st] = states_reached_counts.get(st, 0) + 1

        session = bundle.session_window.get("session") if bundle.session_window else None
        if session:
            session_counts[session] = session_counts.get(session, 0) + 1

        log_entry = {
            "i": i,
            "time": mf_candles[i]["time"],
            "outcome": result.outcome,
            "rejection_code": result.rejection.code if result.rejection else None,
            "session": session,
        }

        if result.outcome == "VALID":
            signal_count += 1
            if session:
                session_signal_counts[session] = session_signal_counts.get(session, 0) + 1
            lifecycle = _simulate_lifecycle(
                result.trade_plan, mf_candles, htf_candles, ltf_candles, spec, i, max_hold_bars,
            )
            lifecycles.append(lifecycle)
            if lifecycle.termination in ("SL_HIT", "ALL_TARGETS_HIT"):
                rr_samples.append(lifecycle.realized_rr)
            log_entry["trade_plan_direction"] = result.trade_plan.direction
            log_entry["lifecycle_termination"] = lifecycle.termination
            log_entry["realized_rr"] = lifecycle.realized_rr
        elif result.rejection is not None:
            rejections[result.rejection.code] = rejections.get(result.rejection.code, 0) + 1

        logs.append(log_entry)

    closed = [l for l in lifecycles if l.termination in ("SL_HIT", "ALL_TARGETS_HIT")]
    wins = [l for l in closed if l.realized_rr > 0]
    losses = [l for l in closed if l.realized_rr <= 0]

    metrics = {
        "symbol": symbol,
        "bar_count": bar_count,
        "warmup_bars": warmup_bars,
        "signal_count": signal_count,
        "signal_rate": (signal_count / bar_count) if bar_count else 0.0,
        "tradeplan_count": len(lifecycles),
        "closed_trade_count": len(closed),
        "open_at_end_count": sum(1 for l in lifecycles if l.termination in ("OPEN_AT_DATA_END", "MAX_HOLD_REACHED")),
        "bias_flip_count": sum(1 for l in lifecycles if l.termination == "BIAS_FLIP"),
        "win_rate": (len(wins) / len(closed)) if closed else None,
        "avg_rr": (sum(rr_samples) / len(rr_samples)) if rr_samples else None,
        "max_rr": max(rr_samples) if rr_samples else None,
        "min_rr": min(rr_samples) if rr_samples else None,
        "rejections_by_code": rejections,
        "states_reached_counts": states_reached_counts,
        "session_counts": session_counts,
        "session_signal_counts": session_signal_counts,
    }
    return {
        "metrics": metrics,
        "logs": logs,
        "lifecycles": [l.__dict__ | {"hits": [h.__dict__ for h in l.hits]} for l in lifecycles],
    }
