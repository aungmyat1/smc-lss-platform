#!/usr/bin/env python3
"""SMC-LSS end-to-end DRY RUN harness.

Runs the full pipeline (market-structure -> choch-bos -> liquidity ->
premium/discount -> validator -> risk sizing -> order payload) on real MT5
candle data and prints the EXACT order it WOULD transmit. It never sends an
order. Flipping to live execution = replacing the print at the end with the two
metatrader MCP calls, and ONLY on a DEMO account.

Data below was pulled live from the connected MetaTrader MCP (EURUSD, 2026-07-16).
"""
import math, json, csv, os

PIP = 0.0001
EURUSD_PIP_VALUE_PER_LOT = 10.0  # USD per pip per 1.0 lot (USD-quote major).
                                 # Real risk-management skill pulls tick_value per symbol.

# time, open, high, low, close  (chronological)
H4 = [
 ("2026-07-13 20:00",1.13887,1.13908,1.13775,1.13801),
 ("2026-07-14 00:00",1.13799,1.13894,1.13782,1.13848),
 ("2026-07-14 04:00",1.13848,1.13967,1.13846,1.13907),
 ("2026-07-14 08:00",1.13906,1.14059,1.13842,1.13997),
 ("2026-07-14 12:00",1.13996,1.14624,1.13898,1.14460),
 ("2026-07-14 16:00",1.14460,1.14590,1.14242,1.14318),
 ("2026-07-14 20:00",1.14319,1.14334,1.14161,1.14207),
 ("2026-07-15 00:00",1.14189,1.14341,1.14168,1.14331),
 ("2026-07-15 04:00",1.14331,1.14424,1.14324,1.14369),
 ("2026-07-15 08:00",1.14370,1.14438,1.14199,1.14243),
 ("2026-07-15 12:00",1.14244,1.14302,1.14062,1.14284),
 ("2026-07-15 16:00",1.14288,1.14423,1.14238,1.14421),
 ("2026-07-15 20:00",1.14422,1.14826,1.14420,1.14627),
 ("2026-07-16 00:00",1.14577,1.14747,1.14577,1.14737),
 ("2026-07-16 04:00",1.14737,1.14741,1.14601,1.14662),
 ("2026-07-16 08:00",1.14663,1.14763,1.14623,1.14659),
 ("2026-07-16 12:00",1.14659,1.14707,1.14470,1.14476),
 ("2026-07-16 16:00",1.14479,1.14591,1.14365,1.14427),
]
M15 = [
 ("2026-07-16 14:15",1.14604,1.14632,1.14583,1.14603),
 ("2026-07-16 14:30",1.14603,1.14664,1.14601,1.14646),
 ("2026-07-16 14:45",1.14646,1.14689,1.14565,1.14686),
 ("2026-07-16 15:00",1.14686,1.14707,1.14636,1.14647),
 ("2026-07-16 15:15",1.14648,1.14653,1.14599,1.14635),
 ("2026-07-16 15:30",1.14634,1.14650,1.14511,1.14527),
 ("2026-07-16 15:45",1.14527,1.14560,1.14470,1.14476),
 ("2026-07-16 16:00",1.14479,1.14536,1.14445,1.14534),
 ("2026-07-16 16:15",1.14530,1.14584,1.14509,1.14582),
 ("2026-07-16 16:30",1.14583,1.14591,1.14534,1.14536),
 ("2026-07-16 16:45",1.14537,1.14562,1.14497,1.14497),
 ("2026-07-16 17:00",1.14498,1.14539,1.14450,1.14483),
 ("2026-07-16 17:15",1.14482,1.14524,1.14470,1.14493),
 ("2026-07-16 17:30",1.14493,1.14521,1.14424,1.14448),
 ("2026-07-16 17:45",1.14450,1.14462,1.14400,1.14429),
 ("2026-07-16 18:00",1.14429,1.14431,1.14365,1.14418),
 ("2026-07-16 18:15",1.14418,1.14439,1.14399,1.14404),
 ("2026-07-16 18:30",1.14404,1.14468,1.14400,1.14465),
 ("2026-07-16 18:45",1.14466,1.14496,1.14455,1.14470),
 ("2026-07-16 19:00",1.14469,1.14471,1.14423,1.14429),
]

ACCOUNT = {"equity": 988.12, "currency": "USD", "type": "real"}  # live-read from MCP
PRICE = {"bid": 1.14426, "ask": 1.14426}
CFG = {"risk_pct": 1.0, "min_rr": 2.0, "max_positions": 3, "daily_loss_pct": 3.0}
OPEN_POSITIONS = 0

def swings(c, k=2):
    hi, lo = [], []
    for i in range(k, len(c)-k):
        h = c[i][2]; l = c[i][3]
        if all(h >  c[j][2] for j in range(i-k,i)) and all(h >= c[j][2] for j in range(i+1,i+k+1)):
            hi.append((c[i][0], h))
        if all(l <  c[j][3] for j in range(i-k,i)) and all(l <= c[j][3] for j in range(i+1,i+k+1)):
            lo.append((c[i][0], l))
    return hi, lo

def trend(hi, lo):
    if len(hi) >= 2 and len(lo) >= 2:
        hh = hi[-1][1] > hi[-2][1]; hl = lo[-1][1] > lo[-2][1]
        lh = hi[-1][1] < hi[-2][1]; ll = lo[-1][1] < lo[-2][1]
        if hh and hl: return "BULLISH"
        if lh and ll: return "BEARISH"
    return "RANGING"

def ltf_choch(c, direction):
    """Bullish CHoCH = close above the most recent swing high; bearish = mirror."""
    hi, lo = swings(c, 2)
    last_close = c[-1][4]
    if direction == "long" and hi:
        return last_close > hi[-1][1], hi[-1][1]
    if direction == "short" and lo:
        return last_close < lo[-1][1], lo[-1][1]
    return False, None

def validate(direction):
    h_hi, h_lo = swings(H4)
    t = trend(h_hi, h_lo)
    swing_low = min(x[1] for x in h_lo) if h_lo else None
    swing_high = max(x[1] for x in h_hi) if h_hi else None
    rng_hi = max(x[2] for x in H4); rng_lo = min(x[3] for x in H4)
    eq = (rng_hi + rng_lo) / 2
    price = PRICE["ask"]
    zone = "PREMIUM" if price > eq else "DISCOUNT" if price < eq else "EQUILIBRIUM"
    choch_ok, choch_lvl = ltf_choch(M15, direction)

    checks = []
    bias_ok = (t == "BULLISH" and direction=="long") or (t == "BEARISH" and direction=="short")
    checks.append(("HTF bias aligned", bias_ok, f"H4 trend {t}; swing low {swing_low}, high {swing_high}"))
    checks.append(("Liquidity target", swing_high is not None, f"draw on liquidity at H4 high {swing_high}"))
    checks.append(("Market structure shift (M15)", choch_ok, f"LTF {direction} CHoCH vs {choch_lvl}: {'yes' if choch_ok else 'no'}"))
    checks.append(("Confirmation", choch_ok, "uses the same LTF close-based CHoCH trigger"))
    pd_ok = (zone=="DISCOUNT" and direction=="long") or (zone=="PREMIUM" and direction=="short")
    checks.append(("Premium/Discount", pd_ok, f"price {price} in {zone} (eq {round(eq,5)})"))
    verdict = all(ok for _,ok,_ in checks)
    return verdict, checks, {"trend":t,"zone":zone,"eq":round(eq,5),"swing_high":swing_high,"swing_low":swing_low}

def size(entry, stop, target, direction):
    dist = abs(entry-stop)
    stop_pips = dist/PIP
    rr = abs(target-entry)/dist if dist else 0
    risk_usd = ACCOUNT["equity"]*CFG["risk_pct"]/100
    raw_lots = risk_usd/(stop_pips*EURUSD_PIP_VALUE_PER_LOT) if stop_pips else 0
    lots = math.floor(raw_lots*100)/100  # round down to 0.01
    actual_risk = lots*stop_pips*EURUSD_PIP_VALUE_PER_LOT
    reasons = []
    if rr < CFG["min_rr"]: reasons.append(f"R:R {rr:.2f} < {CFG['min_rr']}")
    if lots <= 0: reasons.append("rounded lots = 0 (stop too wide for account)")
    if OPEN_POSITIONS >= CFG["max_positions"]: reasons.append("max positions reached")
    decision = "APPROVED" if not reasons else "REFUSED"
    return {"decision":decision,"reasons":reasons,"lots":lots,"stop_pips":round(stop_pips,1),
            "rr":round(rr,2),"risk_usd":round(actual_risk,2),
            "pct_equity":round(actual_risk/ACCOUNT["equity"]*100,2)}

def order_payload(symbol, direction, s, entry, stop, target):
    side = "BUY" if direction=="long" else "SELL"
    return {
      "step_1_place_market_order": {"symbol":symbol,"type":side,"volume":s["lots"]},
      "step_2_modify_position":   {"symbol":symbol,"stop_loss":stop,"take_profit":target,
                                   "_note":"MCP place_market_order takes no SL/TP; attach via modify_position"}
    }

def line(): print("-"*68)

print("="*68); print("SMC-LSS END-TO-END DRY RUN  (no order transmitted)"); print("="*68)
print(f"Account: {ACCOUNT['type'].upper()} equity ${ACCOUNT['equity']} {ACCOUNT['currency']} | open positions {OPEN_POSITIONS}")
print(f"EURUSD price {PRICE['ask']}  (live-read 2026-07-16)")

# ---- STAGE 1: live evaluation (long) ----
line(); print("STAGE 1 - LIVE VALIDATION: EURUSD long")
v, checks, ctx = validate("long")
for name, ok, ev in checks:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:28} - {ev}")
print(f"  VERDICT: {'VALID' if v else 'INVALID -> stand aside'}")
print(f"  (context: {ctx})")

# ---- STAGE 2: synthetic DEMO setup to exercise the full order path ----
line(); print("STAGE 2 - SYNTHETIC DEMO SETUP (exercises sizing + order payload)")
print("  NOTE: not a live signal; a constructed setup to prove the execution chain.")
entry, stop, target, direction, symbol = 1.14426, 1.14300, 1.14700, "long", "EURUSD"
s = size(entry, stop, target, direction)
print(f"  Setup: {direction.upper()} {symbol} entry {entry} stop {stop} target {target}")
print(f"  Sizing -> decision {s['decision']} | lots {s['lots']} | stop {s['stop_pips']} pips | "
      f"R:R {s['rr']} | risk ${s['risk_usd']} ({s['pct_equity']}% equity)")
if s["reasons"]: print("  Refusal reasons:", "; ".join(s["reasons"]))
if s["decision"] == "APPROVED":
    print("  ORDER PAYLOAD THE SYSTEM WOULD TRANSMIT (DEMO ONLY):")
    print(json.dumps(order_payload(symbol, direction, s, entry, stop, target), indent=4))
    print("  >>> DRY RUN: payload built, NOT sent. Switch to a demo account to transmit.")

# ---- STAGE 3: write the live candles to data/ for backtesting reuse ----
line(); out = os.environ.get("OUT_DIR", "/tmp")
os.makedirs(os.path.join(out,"data"), exist_ok=True)
for name, rows in (("EURUSD_H4", H4), ("EURUSD_M15", M15)):
    p = os.path.join(out,"data",name+".csv")
    with open(p,"w",newline="") as f:
        wtr = csv.writer(f); wtr.writerow(["time","open","high","low","close"])
        wtr.writerows(rows)
    print(f"  wrote {p} ({len(rows)} bars)")
print("DONE.")
