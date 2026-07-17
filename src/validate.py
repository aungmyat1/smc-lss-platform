#!/usr/bin/env python3
"""Walk-forward validation for the SMC-LSS strategy (powers the `validation` skill).

Splits each dataset chronologically into IN-SAMPLE (first `frac`) and
OUT-OF-SAMPLE (remainder), backtests each, and returns an objective verdict:

  ACCEPT       edge is positive IN-sample AND holds OUT-of-sample (OOS >= 0.5*IS)
  REJECT       edge does not persist out-of-sample
  INCONCLUSIVE total trades < min_trades (no statistical basis)

Usage:
  python src/validate.py --all --frac 0.7 --rr 2.0
"""
import argparse, glob, json, os
import smc_engine as e
from backtest import collect, metrics


def split_run(path, frac, rr, k, window):
    c = e.load_candles(path)
    if len(c) < 3 * k + 5:
        return None
    n = int(len(c) * frac)
    return collect(c[:n], rr, k, window), collect(c[n:], rr, k, window)


def run(paths, frac=0.7, rr=2.0, k=2, window=40, min_trades=30):
    IS, OOS, per = [], [], {}
    for p in sorted(paths):
        r = split_run(p, frac, rr, k, window)
        if r is None:
            per[os.path.basename(p)] = {"status": "NEEDS_MORE_DATA"}
            continue
        is_r, oos_r = r
        IS += is_r
        OOS += oos_r
        per[os.path.basename(p)] = {"in_sample": metrics(is_r, rr), "out_sample": metrics(oos_r, rr)}
    ism, oosm = metrics(IS, rr), metrics(OOS, rr)
    total = len(IS) + len(OOS)
    if total < min_trades:
        verdict, reason = "INCONCLUSIVE", str(total) + " total trades (<" + str(min_trades) + "); insufficient evidence."
    else:
        is_exp = ism.get("expectancy_R") or 0
        oos_exp = oosm.get("expectancy_R") or 0
        if is_exp > 0 and oos_exp > 0 and oos_exp >= 0.5 * is_exp:
            verdict, reason = "ACCEPT", "edge is positive in-sample and persists out-of-sample."
        else:
            verdict, reason = "REJECT", "edge does not persist out-of-sample (overfit or no edge)."
    return {"verdict": verdict, "reason": reason, "split_frac": frac,
            "total_trades": total, "in_sample": ism, "out_sample": oosm, "per_file": per}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--frac", type=float, default=0.7)
    ap.add_argument("--rr", type=float, default=2.0)
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--window", type=int, default=40)
    a = ap.parse_args()
    paths = sorted(glob.glob("data/*.csv")) if a.all or not a.data else [a.data]
    res = run(paths, a.frac, a.rr, a.k, a.window)
    os.makedirs("reports", exist_ok=True)
    with open("reports/validation_result.json", "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))
