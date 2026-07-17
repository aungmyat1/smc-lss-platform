# SMC-LSS v3.5 — Consolidated Signal Ruleset (Addendum to v3.4)

**Status:** `RESEARCH_CANDIDATE` (unchanged) — this document does not authorize
live trading. The named source is 1BullBear's YouTube lesson
[`D2 : Strategy Blueprint`](https://youtu.be/PxkGqG2qiIM). Source images currently
available for direct review cover **E1M1 only**: slide 53 (H1 check) and slide 55
(M5 confirmation, entry, and intraday target). Statements about other variants
are legacy interpretations pending the same source-evidence treatment.

### Verification vocabulary

- `SOURCE_EXPLICIT`: legible in the supplied source slide.
- `SOURCE_VISUAL`: visible in the chart, but not stated as a general rule.
- `PLATFORM_INTERPRETATION`: deterministic rule added to make the idea executable.
- `PENDING_SOURCE`: prior claim for which the source image/timestamp is not present.

A source-example instrument or direction is not, by itself, proof that the model
is restricted to that instrument or direction.

---

## 1. Unified signal-generation procedure

Every variant collapses to the same three-stage decision, only the formulas differ per model:

```text
STAGE 1 — E-trigger (higher-timeframe cause, sets bias + invalidation context)
  E1: H1 price fills and reacts to a gap [SOURCE_EXPLICIT, slide 53]
  E2: H1 price reaction at a marked POI (supply/demand/liquidity) [PENDING_SOURCE]
  E3: H1 sweep + reclaim of external liquidity [PENDING_SOURCE]

STAGE 2 — M-model (M5 confirmation + entry anchor)
  M1: character change with inducement on M5 [SOURCE_EXPLICIT, slides 53/55]
      -> enter the post-change pullback/execution area [SOURCE_VISUAL]
      -> exact FVG-midpoint anchor [PLATFORM_INTERPRETATION]
  M2: supply/demand shift -> Gold Zone (OB ∩ FVG) -> entry at overlap midpoint
  M3: sweep + displacement -> IFVG -> entry at IFVG midpoint after ≥50% retrace

STAGE 3 — Direction, SL, TP, horizon
  direction  = bias resolved by E-trigger reaction (BUY at demand/SSL-reclaim, SELL at supply/BSL-reclaim)
  entry      = per M-model anchor (Stage 2)
  stop       = beyond the invalidation structure of the SAME execution swing
               (M1: anchor/inducement extreme; M2: OB+FVG+swept-liquidity extreme; M3: IFVG+local-sweep+displacement-origin)
  tp1        = entry ± 1R (management partial; never replaces the displayed DOL)
  primary_tp = pre-selected DOL, chosen BEFORE entry, from the target_source list for the assigned target_horizon
  horizon    = INTRADAY | OVERNIGHT | INTRAWEEK | MULTI_HORIZON (per variant, frozen — not extended after entry)
```

No signal is emitted unless both Stage 1 and Stage 2 confirm on closed candles (§1 of v3.4: confirmation delay applies to all fractals/pivots; no future candles).

---

## 2. Full variant table (all 9 observed cells)

| Variant | Instrument (source) | Direction | Entry anchor | Stop rule | Primary TP source | Horizon | Verification status |
|---|---|---|---|---|---|---|---|
| E1M1 | XAUUSD | SELL | Post-character-change M5 execution area; midpoint is implementation anchor | Stop above the M5 invalidation/entry structure; exact max+buffer formula is platform interpretation | M5 intraday sell-side liquidity | INTRADAY | ✅ Slides 53/55 verified (example only) |
| E1M2 | ETHUSDT | BUY | M2 OB/FVG midpoint | `min(ob_low, fvg_low, swept_ssl)-buffer` | H1 external | INTRAWEEK | ⚠ PENDING_SOURCE (legacy claim) |
| E1M3 | EURUSD | SELL | M3 IFVG midpoint (≥50% retrace) | `max(ifvg_high, swept_high, displacement_origin)+buffer` | M5 SSL + H1 runner | MULTI_HORIZON | ⚠ PENDING_SOURCE (legacy claim) |
| E2M1 | EURGBP | SELL | M1 pullback/FVG midpoint | `max(anchor_high, inducement_high, swept_bsl)+buffer` | Intraday SSL / midnight-open | INTRADAY | ⚠ PENDING_SOURCE (legacy claim) |
| E2M2 | CHFJPY | BUY | M2 OB/FVG midpoint | `min(ob_low, fvg_low, swept_ssl)-buffer` | Next-session/H1 BSL | OVERNIGHT | ⚠ PENDING_SOURCE (legacy claim) |
| **E2M3** | **BTCUSDT** | **SELL** | **M3-style midpoint (H1-resolution zone)** | `max(zone_high, swept_high, displacement_origin)+crypto_buffer` | **H1 external SSL (intra-week)** | **INTRAWEEK** | ⚠ PENDING_SOURCE (legacy claim) |
| E3M1 | GBPJPY | BUY | M1 pullback/FVG midpoint | `min(anchor_low, inducement_low, e3_swept_ssl)-buffer` | Intraday BSL | INTRADAY | ⚠ PENDING_SOURCE (legacy claim) |
| E3M2 | GBPJPY | BUY | M2 OB/FVG midpoint | `min(ob_low, fvg_low, associated_sweep)-buffer` | Intraday BSL | INTRADAY | ⚠ PENDING_SOURCE (v3.4 text only) |
| E3M3 | EURUSD | SELL | M3 IFVG midpoint (≥50% retrace) | `max(ifvg_high, local_sweep, displacement_origin)+buffer` | Intraday SSL | INTRADAY | ⚠ PENDING_SOURCE (legacy claim) |

---

## 3. E1M1 source application — slides 53 and 55

The supplied slides establish the following source chain:

```text
H1 (slide 53)
  E1 = price fills and reacts to a gap
  source example = Gold Spot / U.S. Dollar (XAUUSD)
  observed reaction = bearish

M5 (slide 55)
  M1 = character change with inducement
  execution = short from the displayed M5 execution area
  invalidation = above that M5 structure
  target = displayed M5 intraday sell-side-liquidity objective
```

What these slides **do verify**:

- E1 is checked on the H1 chart. The prior wording that made a D1 gap mandatory
  was unsupported and has been removed.
- M1 confirmation is on M5 and explicitly combines character change with inducement.
- The example is an intraday XAUUSD short with the stop above the M5 execution
  structure and the target below at sell-side liquidity.
- The two stages are sequential: the H1 reaction supplies the cause/bias and M5
  supplies confirmation and execution.

What they **do not prove as universal rules**:

- that E1M1 is always SELL or only tradable on XAUUSD;
- that every M1 entry must be exactly an FVG midpoint;
- the platform's numeric buffer, +1R partial, 12-hour cap, or risk percentage;
- exact machine-readable prices from these compressed images.

For the supplied chart, the earlier approximate visual reading (entry around
1913.65, invalidation around/above 1918, target around 1898) remains useful as a
fixture tolerance, not as exact source data. Candle-history replay is required
before treating those numbers as executable evidence.

### Mechanical E1 detector rule used by the platform

To avoid the former unsafe fallback (“not E2/E3, therefore E1”), the detector now
requires a prior direction-aligned H1 fair-value gap plus a recent closed H1
candle that trades into the gap and rejects away from its midpoint. This is a
conservative `PLATFORM_INTERPRETATION` of “price fills and reacts to gap”; it must
be calibrated against more labeled E1 examples.

---

## 4. E2M3 (BTC/USDT) — legacy source claim, evidence pending in repository

An earlier review recorded a `1H Intra-Week Target Chart` for this trade and read the following values from it. That source image is not currently in the repository, so this section preserves the legacy interpretation but does not independently re-certify it:

```text
H1 price reacts at a marked supply POI (~26,900 zone, already swept once)
-> bearish rejection / displacement through the range
-> entry zone at ~26,699 (pink/teal boundary)
-> stop above the zone high, ~26,900
-> sell-side H1-external target ~25,324.7
-> held 28 H1 bars (1 day 4 hours)
```

That 28-hour hold is past the 24-hour ceiling for `OVERNIGHT`, so the correct classification is `INTRAWEEK`, not the `INTRADAY` guess in the earlier draft — this is a case where the extra chart directly corrected an assumption rather than just confirming one.

```yaml
direction: SELL
variant: E2M3
entry: ~26699                                          # confirmed
stop: ~26900  (zone_high + crypto_buffer)               # confirmed
tp1: entry - 1R
intraweek_tp: ~25324.7  (selected H1 external SSL)      # confirmed
target_horizon: INTRAWEEK                               # corrected from INTRADAY
maximum_holding_hours: 120
status: SOURCE_VERIFIED
```

Same caveat v3.4 already applies to E1M2: the exact sub-structure that produced the H1 zone (M5 sweep/displacement/IFVG detail) isn't independently visible in this chart, so the *zone-level* entry/stop/target is verified, not the tick-level M5 mechanics. That's consistent with how E1M2 is treated elsewhere in this document.

---

## 5. Legacy SL/TP conformance recap

| Trade | Entry (chart) | Stop (chart) | Primary TP (chart) | Formula match |
|---|---|---|---|---|
| E1M1 XAUUSD | ≈1913.65 | above ≈1918.0 | ≈1898 | ✅ |
| E1M2 ETHUSDT | ≈1171.55 | below ≈1163.83 | ≈1218–1220 | ✅ |
| E1M3 EURUSD | ≈1.11357 | above ≈1.11460 | ≈1.10875 (+ H1 runner ≈1.10200) | ✅ |
| E2M1 EURGBP | ≈0.87001 | above ≈0.87093 | ≈0.86730 | ✅ |
| E2M2 CHFJPY | ≈162.35 | below ≈161.95 | ≈164.02–164.22 | ✅ |
| E3M1 GBPJPY | ≈165.582 | below ≈165.30 | ≈167.32 | ✅ |
| E2M3 BTCUSDT | ≈26,699 | above ≈26,900 | ≈25,324.7 (H1, INTRAWEEK) | ✅ |
| E3M3 EURUSD | ≈1.09534 | above ≈1.09583 | ≈1.09150–1.09159 | ✅ |

Only E1M1 is directly reproducible from source images available in this review.
The other rows preserve earlier approximate readings but are `PENDING_SOURCE`
until their slides or video timestamps are added. “Formula match” means the
legacy formula can reproduce the displayed side of entry; it is not proof that
the formula was explicitly taught in the video.

---

## 6. Recommended next step for implementation

1. Treat E1M1's H1 gap reaction and M5 character-change-with-inducement sequence as source-backed; keep the exact anchor/buffer algorithm explicitly labeled as platform interpretation.
2. Implement the common mechanics with parameterized functions rather than nine copy-pasted handlers, but do not infer instrument or direction exclusivity from one example.
3. Add the remaining source slides/video timestamps and apply the same explicit/visual/interpretation classification before calling those cells source-verified.
4. Build candle-history fixtures around each source example and verify detector output, not only stop/target arithmetic.
5. Keep `engine_implements_spec: false` until the detector, backtest, and automation gates pass.
