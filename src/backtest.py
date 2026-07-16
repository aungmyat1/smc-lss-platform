"""Deterministic SMC-LSS backtest runner (skeleton).
Loads a CSV dataset and a YAML spec, replays bar-by-bar (close-only, no
look-ahead) and writes metrics. Fill in atomic rule calls from .claude/skills.
"""
import argparse, csv, statistics, json, sys

def load_candles(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def run(spec_path, data_path):
    candles = load_candles(data_path)
    if len(candles) < 30:
        return {"status": "LOW_SAMPLE", "bars": len(candles)}
    # TODO: implement market-structure / choch-bos / poi / entry rules here.
    trades = []  # each: {"r": float}
    if not trades:
        return {"status": "NOT_IMPLEMENTED",
                "reason": "Rule engine not yet wired; provide dataset + implement atomic rules.",
                "bars": len(candles)}
    rs = [t["r"] for t in trades]
    wins = [r for r in rs if r > 0]
    exp = statistics.mean(rs)
    return {"status": "OK","trades": len(rs),"expectancy_R": round(exp,3),
            "win_rate": round(len(wins)/len(rs),3)}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--spec", required=True); p.add_argument("--data", required=True)
    a = p.parse_args()
    print(json.dumps(run(a.spec, a.data), indent=2))
