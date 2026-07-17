#!/usr/bin/env python3
"""Bulk historical loader for the SMC-LSS backtester.

Run LOCALLY on the machine where the MetaTrader 5 terminal + `MetaTrader5`
python package are installed (your Windows box). It downloads OHLC candles and
writes data/<SYMBOL>_<TF>.csv with columns: time,open,high,low,close.

Examples:
  python src/load_history.py --symbols EURUSD,GBPUSD,XAUUSD --timeframe H1 --bars 20000
  python src/load_history.py --symbols EURUSD --timeframe H4 --bars 5000
"""
import argparse, csv, os, sys, datetime as dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", required=True, help="comma-separated, e.g. EURUSD,GBPUSD")
    ap.add_argument("--timeframe", default="H1")
    ap.add_argument("--bars", type=int, default=20000)
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    try:
        import MetaTrader5 as mt5
    except ImportError:
        sys.exit("MetaTrader5 not installed. On Windows with the MT5 terminal: pip install MetaTrader5")
    TF = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
          "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
          "D1": mt5.TIMEFRAME_D1}
    if a.timeframe not in TF:
        sys.exit("timeframe must be one of " + ",".join(TF))
    if not mt5.initialize():
        sys.exit("mt5.initialize() failed: " + str(mt5.last_error()))
    os.makedirs(a.out, exist_ok=True)
    for sym in [s.strip() for s in a.symbols.split(",") if s.strip()]:
        mt5.symbol_select(sym, True)
        rates = mt5.copy_rates_from_pos(sym, TF[a.timeframe], 0, a.bars)
        if rates is None or len(rates) == 0:
            print("no data for", sym, mt5.last_error()); continue
        p = os.path.join(a.out, sym + "_" + a.timeframe + ".csv")
        with open(p, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["time", "open", "high", "low", "close"])
            for r in rates:
                t = dt.datetime.utcfromtimestamp(int(r["time"])).strftime("%Y-%m-%d %H:%M")
                w.writerow([t, r["open"], r["high"], r["low"], r["close"]])
        print("wrote", p, "(" + str(len(rates)) + " bars)")
    mt5.shutdown()


if __name__ == "__main__":
    main()
