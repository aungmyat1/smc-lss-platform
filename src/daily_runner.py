#!/usr/bin/env python3
"""Daily-loop runner — deterministic multi-symbol SMC-LSS scan.

Reads config/watchlist.yaml, runs the analysis pipeline per ACTIVE symbol on
pre-fetched CSVs (data/<symbol>_<confirm_tf>.csv), and writes a combined
reports/daily_signals.json with a decision + sized order payload per symbol.

SAFETY: this script never sends orders. It is pure and deterministic (no network).
Live candles are fetched by the Cowork run via the MetaTrader MCP and written to
CSV first (see docs/daily-loop-runbook.md). Order transmission happens only in the
runbook, demo-only, and only when the strategy-of-record engine is ready.

Interlock: while watchlist.autonomy.engine_implements_spec is false, the strategy
of record (specs/v3.5.yaml) is NOT yet implemented in code. The runner then labels
every decision as PROPOSE (mode=propose) so nothing is auto-executed. The current
analysis uses the legacy v1 pipeline (smc_master) purely as a placeholder signal.

Usage:
  python src/daily_runner.py --equity 987.99 --env demo
  python src/daily_runner.py --equity 987.99 --env demo --tier all   # include pending symbols
"""
import argparse, json, os, datetime
import yaml
import smc_engine as e
import smc_master as m
import signal_v35 as v35


def load_cfg(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def run_symbol(sym, cfg, data_dir, equity, env, auto):
    tf = cfg["cadence"]["timeframes"]["confirm"]
    path = os.path.join(data_dir, f"{sym['name']}_{tf}.csv")
    if not os.path.exists(path):
        return {"symbol": sym["name"], "decision": "SKIP",
                "reason": f"missing data file {path} (fetch via MCP first)", "variants": sym.get("variants")}
    c = e.load_candles(path)
    risk_pct = cfg["risk"]["risk_pct_demo"] if env != "live" else cfg["risk"]["risk_pct_live"]
    res = m.run(c, equity, risk_pct, cfg["risk"]["min_rr"], strict_session=True,
                symbol=sym["mt5"], pip=sym["pip"], pip_value=sym["pip_value_per_lot"])
    # v3.5 engine read (parallel, propose-only): use H1 for bias if available
    h1p = os.path.join(data_dir, f"{sym['name']}_H1.csv")
    h1 = e.load_candles(h1p) if os.path.exists(h1p) else None
    try:
        res["v35"] = v35.analyze(sym["name"], c, h1)
    except Exception as ex:
        res["v35"] = {"decision": "ERROR", "reason": str(ex)}
    res["symbol"] = sym["name"]
    res["variants"] = sym.get("variants")
    res["env"] = env
    # Interlock: never mark as auto-executable until the spec engine is ready.
    res["mode"] = "auto" if (auto and env == "demo") else "propose"
    if res.get("decision") == "GO" and res["mode"] == "propose":
        res["decision"] = "PROPOSE"
        res["note"] = "GO gates passed; held in propose-mode (v3.5 engine not yet implemented / not demo-auto)"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/watchlist.yaml")
    ap.add_argument("--data", default="data")
    ap.add_argument("--equity", type=float, required=True)
    ap.add_argument("--env", default="demo", choices=["demo", "live"])
    ap.add_argument("--tier", default="active", choices=["active", "all"])
    a = ap.parse_args()

    cfg = load_cfg(a.config)
    auto = bool(cfg["autonomy"].get("engine_implements_spec")) and cfg["autonomy"].get("demo", "").startswith("auto")
    if a.env == "live":
        auto = False  # live is blocked by policy regardless
    syms = list(cfg["symbols"]["active"])
    if a.tier == "all":
        syms += list(cfg["symbols"].get("pending", []))

    results = [run_symbol(s, cfg, a.data, a.equity, a.env, auto) for s in syms]
    out = {
        "generated_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "strategy_spec": cfg.get("strategy_spec"),
        "env": a.env,
        "equity": a.equity,
        "auto_execute_enabled": auto,
        "actionable": [r["symbol"] for r in results if r.get("decision") in ("GO", "PROPOSE")],
        "results": results,
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/daily_signals.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
