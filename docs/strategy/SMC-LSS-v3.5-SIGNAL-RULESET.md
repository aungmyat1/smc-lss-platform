# SMC-LSS v3.5 — Consolidated Signal Ruleset (Addendum to v3.4)

**Status:** `RESEARCH_CANDIDATE` (unchanged) — this document does not change governance, live-trading, or approval status in §1 of v3.4. It (a) adds the missing `E2M3` variant, (b) consolidates all nine variants into one decision procedure a code agent can implement directly, and (c) re-states the SL/TP verification already run against every source screenshot so it lives in one place.

---

## 1. Unified signal-generation procedure

Every variant collapses to the same three-stage decision, only the formulas differ per model:

```text
STAGE 1 — E-trigger (higher-timeframe cause, sets bias + invalidation context)
  E1: D1 gap fill/reaction at H1 context
  E2: H1 price reaction at a marked POI (supply/demand/liquidity)
  E3: H1 sweep + reclaim of external liquidity

STAGE 2 — M-model (M5 confirmation + entry anchor)
  M1: inducement + character change -> entry at pullback/FVG midpoint
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
| E1M1 | XAUUSD | SELL | M1 pullback/FVG midpoint | `max(anchor_high, inducement_high, swept_bsl)+buffer` | Intraday SSL | INTRADAY | ✅ Source-verified |
| E1M2 | ETHUSDT | BUY | M2 OB/FVG midpoint | `min(ob_low, fvg_low, swept_ssl)-buffer` | H1 external | INTRAWEEK | ✅ Source-verified |
| E1M3 | EURUSD | SELL | M3 IFVG midpoint (≥50% retrace) | `max(ifvg_high, swept_high, displacement_origin)+buffer` | M5 SSL + H1 runner | MULTI_HORIZON | ✅ Source-verified |
| E2M1 | EURGBP | SELL | M1 pullback/FVG midpoint | `max(anchor_high, inducement_high, swept_bsl)+buffer` | Intraday SSL / midnight-open | INTRADAY | ✅ Source-verified |
| E2M2 | CHFJPY | BUY | M2 OB/FVG midpoint | `min(ob_low, fvg_low, swept_ssl)-buffer` | Next-session/H1 BSL | OVERNIGHT | ✅ Source-verified |
| **E2M3** | **BTCUSDT** | **SELL** | **M3-style midpoint (H1-resolution zone)** | `max(zone_high, swept_high, displacement_origin)+crypto_buffer` | **H1 external SSL (intra-week)** | **INTRAWEEK** | ✅ Source-verified |
| E3M1 | GBPJPY | BUY | M1 pullback/FVG midpoint | `min(anchor_low, inducement_low, e3_swept_ssl)-buffer` | Intraday BSL | INTRADAY | ✅ Source-verified |
| E3M2 | GBPJPY | BUY | M2 OB/FVG midpoint | `min(ob_low, fvg_low, associated_sweep)-buffer` | Intraday BSL | INTRADAY | ✅ Compatible (v3.4 §21.7, no new chart supplied) |
| E3M3 | EURUSD | SELL | M3 IFVG midpoint (≥50% retrace) | `max(ifvg_high, local_sweep, displacement_origin)+buffer` | Intraday SSL | INTRADAY | ✅ Source-verified |

---

## 3. E2M3 (BTC/USDT) — now source-verified, horizon corrected

The `1H Intra-Week Target Chart` supplied for this trade shows the entry/stop/target zones directly at H1 resolution (the same way E1M2 was accepted without a raw M5 overlap). Reading it:

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

## 4. SL/TP conformance recap (already checked against your screenshots)

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

All nine source-observed variants (`E1M1, E1M2, E1M3, E2M1, E2M2, E2M3, E3M1, E3M2, E3M3`) are now covered. Seven are pixel-checked against screenshots (E3M2 carries over from v3.4 text only, no new chart supplied yet).

---

## 5. Recommended next step for implementation (per v3.4 §22)

1. Freeze §1's Stage 1–3 procedure exactly as written above — this is now the single source of truth for signal generation across all E×M combinations, replacing the need to special-case each variant in code.
2. Implement it as one parameterized function `generate_signal(e_trigger, m_model, instrument_profile)` rather than nine separate handlers — the E-trigger supplies bias/context, the M-model supplies entry/stop/TP1 formula, the instrument profile supplies buffer size and tick/point conversion.
3. `E2M3` is now `SOURCE_VERIFIED` at the H1 zone level and can enter the fixture set alongside the other eight; note in the fixture metadata that its sub-M5 structure wasn't independently confirmed, same as E1M2.
4. Everything else from v3.4 — governance (§1), instrument profiles (§2.1), session policy (§2.2), holding modes (§2.3) — carries over unchanged.
