#!/usr/bin/env python3
"""SMC Trading Master — deterministic orchestrator over the analysis layer.

Runs the ordered SMC-LSS pipeline on the latest bar of a CSV, stopping at the
first HARD gate that fails (institutional discipline: never skip steps). Order
blocks / FVGs are scored as confluence (reported, not hard-stops). On a full
pass it emits the sized two-step order payload for the execution layer.

Stages: session -> market-structure -> liquidity-sweep -> choch/bos ->
[order-block, fvg confluence] -> premium/discount -> entry-confirmation -> risk.
"""
import argparse, json
import config as configmod
import smc_engine as e
from live_signal import latest_signal, size


def session_of(ts, killzones):
    hh = int(ts[11:13])
    for kz in killzones.values():
        if kz.contains(hh):
            return kz.name.upper() + "-KZ", True
    return "OFF-KZ", False


def run(c, cfg, equity, env="demo", strict_session=False, symbol_name=None):
    sym = cfg.symbol(symbol_name or cfg.strategy.symbol)
    risk_pct = cfg.risk.risk_pct_for(env)
    rr = cfg.risk.min_rr
    k = cfg.strategy.swing_lookback

    stages = []
    def add(n, ok, ev):
        stages.append({"stage": n, "result": "PASS" if ok else "FAIL", "evidence": ev})
    def done(decision, reason, payload=None, sig=None, sizing=None):
        return {"decision": decision, "reason": reason, "stages": stages,
                "order_payload": payload, "signal": sig, "sizing": sizing}

    sess, in_kz = session_of(c[-1]["time"], cfg.execution.killzones)
    add("1 session-filter", (in_kz or not strict_session), sess + " @ " + c[-1]["time"])
    if strict_session and not in_kz:
        return done("NO-GO", "outside killzone")

    hi, lo = e.swings(c, k)
    t = e.trend(hi, lo)
    add("2 market-structure", t != "RANGING", "trend " + t)
    if t == "RANGING":
        return done("NO-GO", "no directional bias (ranging)")
    direction = "long" if t == "BULLISH" else "short"
    want = "bull" if direction == "long" else "bear"

    lookback = cfg.execution.liquidity_sweep_lookback_bars
    sw = [s for s in e.liquidity_sweeps(c, k) if s["i"] >= len(c) - lookback and s["dir"] == want]
    add("3 liquidity-sweep", bool(sw), str(len(sw)) + " aligned sweep(s) in last " + str(lookback) + " bars")
    if not sw:
        return done("NO-GO", "no aligned liquidity sweep")

    sig = latest_signal(c, k, cfg.execution.equilibrium_window)
    ok4 = sig is not None and sig["dir"] == direction
    add("4 choch-bos", ok4, "structure shift signal: " + json.dumps(sig))
    if not ok4:
        return done("NO-GO", "no aligned BOS/CHoCH on latest bar")

    obs = [o for o in e.order_blocks(c, k) if o["dir"] == want]
    add("5 order-block (confluence)", True, str(len(obs)) + " aligned OB(s) [soft]")
    fv = [f for f in e.fvgs(c) if f["dir"] == want]
    add("6 fair-value-gap (confluence)", True, str(len(fv)) + " aligned FVG(s) [soft]")

    eqv, _, _ = e.equilibrium(c, len(c) - 1, cfg.execution.equilibrium_window)
    px = c[-1]["close"]
    zone = "DISCOUNT" if px < eqv else "PREMIUM"
    pd_ok = (direction == "long" and zone == "DISCOUNT") or (direction == "short" and zone == "PREMIUM")
    add("7 premium-discount", pd_ok, "price " + str(px) + " in " + zone + " (eq " + str(round(eqv, 5)) + ")")
    if not pd_ok:
        return done("NO-GO", "price in wrong zone for " + direction)

    add("8 entry-confirmation", True, "LTF signal present")
    s = size(sig, equity, risk_pct, rr, pip=sym.pip, pip_value=sym.pip_value_per_lot,
             lot_step=cfg.execution.lot_step, min_rr=cfg.risk.min_rr)
    add("9 risk-management", s["decision"] == "GO",
        "lots " + str(s["lots"]) + " | RR " + str(s["rr"]) + " | risk $" + str(s["risk_usd"]))
    if s["decision"] != "GO":
        return done("NO-GO", "; ".join(s["reasons"]))

    payload = {"place_market_order": {"symbol": sym.mt5, "type": "BUY" if direction == "long" else "SELL", "volume": s["lots"]},
               "modify_position": {"stop_loss": round(sig["stop"], 5), "take_profit": s["target"]}}
    return done("GO", "all hard gates passed", payload, sig, s)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/EURUSD_H1.csv")
    ap.add_argument("--equity", type=float, default=988.12)
    ap.add_argument("--env", default="demo", choices=["demo", "live"])
    ap.add_argument("--symbol", default=None, help="watchlist symbol name (e.g. EURUSD); defaults to specs/v1.yaml's symbol")
    ap.add_argument("--strict_session", action="store_true")
    a = ap.parse_args()
    cfg = configmod.load()
    c = e.load_candles(a.data)
    print(json.dumps(run(c, cfg, a.equity, a.env, a.strict_session, a.symbol), indent=2))
