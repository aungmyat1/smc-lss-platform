#!/usr/bin/env python3
"""Automated live-signal orchestrator.

Detects whether the LATEST closed bar triggers an SMC-LSS signal, sizes it with
the risk rules, and emits GO/NO-GO plus the exact two-step order payload. The
actual order is transmitted separately via the MetaTrader MCP, GO only, DEMO only.

Usage:
  python src/live_signal.py --data data/EURUSD_H1.csv --equity 988.12 --symbol EURUSD-VIP
"""
import argparse, json, math
import config
import smc_engine as e


def latest_signal(c, k, window):
    hi_all, lo_all = e.swings(c, k)
    i = len(c) - 1
    px = c[i]["close"]
    hi, lo = e.confirmed_before(hi_all, i, k), e.confirmed_before(lo_all, i, k)
    if not hi or not lo:
        return None
    eq, _, _ = e.equilibrium(c, i, window)
    sh, sl = hi[-1][1], lo[-1][1]
    if px > sh and px < eq and sl < px:
        return {"dir": "long", "entry": px, "stop": sl, "eq": round(eq, 5)}
    if px < sl and px > eq and sh > px:
        return {"dir": "short", "entry": px, "stop": sh, "eq": round(eq, 5)}
    return None


def size(sig, equity, risk_pct, rr, pip, pip_value, lot_step, min_rr):
    dist = abs(sig["entry"] - sig["stop"])
    stop_pips = dist / pip
    risk_usd = equity * risk_pct / 100
    lots = math.floor((risk_usd / (stop_pips * pip_value)) / lot_step) * lot_step if stop_pips else 0
    tgt = sig["entry"] + rr * dist if sig["dir"] == "long" else sig["entry"] - rr * dist
    reasons = []
    if rr < min_rr:
        reasons.append("R:R < " + str(min_rr))
    if lots <= 0:
        reasons.append("rounded lots = 0")
    return {"lots": round(lots, 2), "stop_pips": round(stop_pips, 1), "target": round(tgt, 5),
            "risk_usd": round(lots * stop_pips * pip_value, 2),
            "pct_equity": round(lots * stop_pips * pip_value / equity * 100, 2),
            "rr": rr, "decision": "GO" if not reasons else "NO-GO", "reasons": reasons}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/EURUSD_H1.csv")
    ap.add_argument("--symbol", default=None, help="watchlist symbol name (e.g. EURUSD); defaults to specs/v1.yaml's symbol")
    ap.add_argument("--equity", type=float, default=988.12)
    ap.add_argument("--env", default="demo", choices=["demo", "live"])
    a = ap.parse_args()
    cfg = config.load()
    sym = cfg.symbol(a.symbol or cfg.strategy.symbol)
    c = e.load_candles(a.data)
    sig = latest_signal(c, cfg.strategy.swing_lookback, cfg.execution.equilibrium_window)
    if not sig:
        out = {"signal": "NONE", "decision": "NO-GO", "reason": "no valid SMC setup on latest bar (stand aside)",
               "symbol": sym.mt5, "bars": len(c), "last_close": c[-1]["close"]}
    else:
        risk_pct = cfg.risk.risk_pct_for(a.env)
        s = size(sig, a.equity, risk_pct, cfg.risk.min_rr, pip=sym.pip, pip_value=sym.pip_value_per_lot,
                 lot_step=cfg.execution.lot_step, min_rr=cfg.risk.min_rr)
        out = {"signal": sig, "sizing": s, "symbol": sym.mt5,
               "order_payload": None if s["decision"] != "GO" else {
                   "place_market_order": {"symbol": sym.mt5, "type": "BUY" if sig["dir"] == "long" else "SELL", "volume": s["lots"]},
                   "modify_position": {"stop_loss": round(sig["stop"], 5), "take_profit": s["target"]}}}
    print(json.dumps(out, indent=2))
