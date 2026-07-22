# Reference: E-Trigger Positive Acceptance Fixtures (from the 9 Eg worked examples)

**Type:** Research-track reference / fixture *design*. NOT wired into any test suite.
**Status:** Definition only. Modifies no spec, no detection logic, no test file, no autonomy
flag. These describe what a correct E1/E2/E3 engine *should* recognize on three known-good
setups — a positive acceptance set. Converting them into executable `pytest` cases and
attaching them to the v3.9/v3.10 conformance suites is a **separate, gated step**: it touches
the PARKED ST-C1 line, so it needs the owner to re-activate that line (or fold it into the
ST-C2 conformance work) AND a green `python -m pytest -q` run before it counts as done.
**Source examples:** [`bullbear-9eg-example-trades.md`](bullbear-9eg-example-trades.md).
**Caveat carried forward:** these are hand-picked winners. Passing them proves the engine
*detects the intended shape*, NOT that the trigger is profitable (v3.9 PF 0.138 / v3.10 PF
0.471 on full population). Positive-detection fixtures only; never a profitability claim.

> Price levels below are read off chart axes and are **approximate** — for real fixtures the
> exact OHLC must come from the underlying data series, not the screenshot. Levels here are
> for geometry/shape assertions, not tick-exact matching.

---

## Point-in-time discipline

Every assertion is evaluated at or before the **confirmation bar** (the 5M CHoCH close).
Nothing may reference a bar after entry. The stop is defined by structural invalidation, not
a fixed distance. Each fixture states: HTF context → trigger event → LTF confirmation →
entry/stop/target — all knowable at decision time.

---

## FIX-E1 — 1D gap fill & react (long)  ·  from E1·M2, ETHUSD perp

```yaml
id: FIX-E1-gap-fill-react
trigger_family: E1            # platform E1 = D1 gap reaction
model: M2                     # Supply/Demand Shift
instrument: ETHUSD (illustrative)
direction: long
htf_context:                  # 1D check
  bias_origin: prior bearish displacement leg into a demand zone (~1120-1160)
  buy_side_liquidity: ~1680 (external high, draw)
  sell_side_liquidity: ~1080 (external low, protected)
  daily_gap: present; price fills into the gap zone and reacts up
trigger_event:                # what qualifies E1
  - price enters the 1D gap/demand region
  - bullish reaction (rejection + close back inside range)
ltf_confirmation:             # 5M confirm
  event: bullish CHoCH (break + close above most-recent internal lower-high)
entry:
  zone: reaction/demand ~1165 (approx)
  type: on 5M confirmation
stop:
  mode: structural_invalidation
  level: below reaction low ~1160 (approx)  # tight risk box in capture
targets:
  intraday: ~1218 (prior internal high)      # slide 60: 47 bars, 3h55m
  swing: toward buy-side liquidity ~1560-1680 # slide 62: 1D swing
accept_if:
  - engine flags an E1 (gap-reaction) signal at/near the reaction zone
  - direction == long
  - stop placed below the confirmation-bar invalidation low
  - at least one target maps to a higher liquidity draw
reject_if:
  - signal fires before the 5M confirmation close (repaint)
  - stop placed on a fixed distance rather than structure
```

## FIX-E2 — 1H POI react after inducement (short)  ·  from E2·M1, EUR/GBP

```yaml
id: FIX-E2-poi-inducement-choch
trigger_family: E2            # platform E2 = 1H POI continuation
model: M1                     # Character Change with Inducement
instrument: EURGBP (illustrative)
direction: short
htf_context:                  # 1H check
  session: London AM sets the high; midnight-open referenced
  inducement: internal high ~0.8710 taken (buy-side liquidity grab / IND label)
  sell_side_liquidity: ~0.8645 (draw below)
trigger_event:
  - price reacts down from a 1H POI directly after the inducement sweep
ltf_confirmation:             # 5M confirm
  event: bearish CHoCH (break + close below internal higher-low)
entry:
  zone: POI ~0.8705-0.8715 (approx)
  type: on 5M confirmation
stop:
  mode: structural_invalidation
  level: above the inducement high ~0.8720 (approx)
targets:
  swing: sell-side liquidity ~0.8655-0.8660  # slide 70: 135 bars, 11h15m
accept_if:
  - engine flags an E2 (1H POI) signal after an inducement above prior high
  - direction == short
  - stop above the inducement high
  - target draws toward sell-side liquidity
reject_if:
  - signal fires without a prior inducement/liquidity grab
  - confirmation taken from a wick, not a close
```

## FIX-E3 — liquidity sweep reversal (long)  ·  from E3·M2, GBP/JPY

```yaml
id: FIX-E3-sweep-reversal
trigger_family: E3            # platform E3 = liquidity-sweep entry
model: M2                     # Supply/Demand Shift
instrument: GBPJPY (illustrative)
direction: long
htf_context:                  # 1H check
  prior_swing_low: ~171.30 (sell-side liquidity resting below)
trigger_event:
  - price spikes below the prior swing low (sweeps sell-side liquidity)
  - closes back above the swept level (failed breakdown)
ltf_confirmation:             # 5M confirm
  event: bullish CHoCH + supply/demand shift after the sweep
entry:
  zone: reclaim above the sweep ~171.55 (approx)
  type: on 5M confirmation
stop:
  mode: structural_invalidation
  level: below the sweep low ~171.40 (approx)
targets:
  intraday: ~172.30 (prior internal high)   # slide 85: 56 bars, 4h40m, Vol 28k
accept_if:
  - engine flags an E3 (sweep) signal only after close-back-above the swept level
  - direction == long
  - stop below the sweep extreme
reject_if:
  - signal fires on the sweep spike before the reclaim close (repaint)
  - no prior resting liquidity identified at the swept level
```

---

## Coverage & next step

| Fixture | E-family | Source capture | Status |
|---|---|---|---|
| FIX-E1 | E1 gap reaction | E1·M2 (viewed) | defined |
| FIX-E2 | E2 1H POI | E2·M1 (viewed) | defined |
| FIX-E3 | E3 sweep | E3·M2 (viewed) | defined |
| — | E1·M1, E1·M3, E2·M2, E2·M3, E3·M1, E3·M3 | not yet viewed | pending capture review |

**To promote these to real tests (gated):**
1. Owner re-activates the ST-C1 line, or the ST-C2 RCR adopts an E-trigger acceptance suite.
2. Extract exact OHLC for each example from the data series (not the screenshot).
3. Encode as `pytest` cases against `src/signal_v39.py` / `signal_v310.py` (or the ST-C2
   engine), asserting `accept_if` and `reject_if`.
4. `python -m pytest -q` green before marking done.

Until then this stays a design reference — additive, reversible, authority-free.
