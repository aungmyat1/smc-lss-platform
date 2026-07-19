#!/usr/bin/env python3
"""Daily-loop runner — deterministic multi-symbol SMC-LSS scan.

Loads configuration through src/config.py only, runs the analysis pipeline per
ACTIVE symbol on pre-fetched CSVs (data/<symbol>_<confirm_tf>.csv), and writes a
combined reports/daily_signals.json with a decision + sized order payload per
symbol.

SAFETY: this script never sends orders. It is pure and deterministic (no network).
Live candles are fetched by the Cowork run via the MetaTrader MCP and written to
CSV first (see docs/daily-loop-runbook.md). Order transmission happens only in the
runbook, demo-only, and only when the approved strategy / execution gates allow it.

Interlock: until the execution layer is ready, the runner labels every decision as
PROPOSE (mode=propose) so nothing is auto-executed. The current analysis uses the
legacy v1 pipeline (smc_master) purely as a placeholder signal.

Usage:
  python src/daily_runner.py --equity 987.99 --env demo
  python src/daily_runner.py --equity 987.99 --env demo --tier all   # include pending symbols
"""
import argparse, json, os, datetime
import config as configmod
import smc_engine as e
import smc_master as m
import signal_v35 as v35


def run_symbol(sym, cfg, data_dir, equity, env, auto):
    tf = cfg.cadence.timeframes["confirm"]
    path = os.path.join(data_dir, f"{sym.name}_{tf}.csv")
    if not os.path.exists(path):
        return {"symbol": sym.name, "decision": "SKIP",
                "reason": f"missing data file {path} (fetch via MCP first)", "variants": list(sym.variants)}
    c = e.load_candles(path)
    res = m.run(c, cfg, equity, env=env, strict_session=True, symbol_name=sym.name)
    # v3.5 engine read (parallel, propose-only): use H1+D1 for E-trigger if available
    h1p = os.path.join(data_dir, f"{sym.name}_H1.csv")
    h1 = e.load_candles(h1p) if os.path.exists(h1p) else None
    d1p = os.path.join(data_dir, f"{sym.name}_D1.csv")
    d1 = e.load_candles(d1p) if os.path.exists(d1p) else None
    try:
        res["v35"] = v35.analyze(sym.name, c, h1, d1)
    except Exception as ex:
        res["v35"] = {"decision": "ERROR", "reason": str(ex)}
    res["symbol"] = sym.name
    res["variants"] = list(sym.variants)
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

    cfg = configmod.load(watchlist_path=a.config)
    auto = bool(cfg.autonomy.engine_implements_spec) and cfg.autonomy.demo.startswith("auto")
    if a.env == "live":
        auto = False  # live is blocked by policy regardless
    syms = list(cfg.symbols_active)
    if a.tier == "all":
        syms += list(cfg.symbols_pending)

    results = [run_symbol(s, cfg, a.data, a.equity, a.env, auto) for s in syms]
    out = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "strategy_spec": cfg.strategy_spec,
        "research_spec": cfg.research_spec,
        "schema_version": cfg.schema_version,
        "config_version": cfg.config_version,
        "registry_version": cfg.registry_version,
        "config_hash": cfg.config_hash,
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
