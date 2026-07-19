# SMC-LSS v3.6 — Machine-Testable Signal Specification

**Status:** `RESEARCH_CANDIDATE` — spec only, no engine implements this yet.
**Supersedes:** v3.5 (`docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md`), which stays as the
historical chart-verification record for the 9 example trades. v3.6 does not
discard those examples; it replaces the qualitative language around them with
numeric, testable rules so the same 9 examples become regression fixtures
instead of the only ground truth.

## Why this document exists

v3.5 is chart-verified but not implementable deterministically: terms like
"a marked POI," "external liquidity," "strong displacement," and "reaction"
have no numeric definition, no freshness bound, and no specified order of
events. The current code (`src/signal_v35.py`) filled those gaps with
generic proxies — *any* H1 sweep counts as E3, *any* H1 order block counts as
E2, direction is hard-locked per variant from a single historical example
instead of read live, a missing target silently passes the R:R gate instead
of rejecting. Backtested on ~7–13 months of real EURUSD/XAUUSD/BTCUSD history
(2026-07-18), that produced 231–816 trades per symbol at a 10–23% win rate
and negative expectancy on every symbol — overtrading on noise, not a
strategy with a small sample problem. This spec is the fix: every rule below
is stated so a fixture can assert pass/fail without a human judgment call.

Every numeric threshold below is marked **[FIXED]** (structural, not meant to
be tuned) or **[TUNABLE]** (an initial default; changes must go through
`backtest-researcher` → `validation`, never edited ad hoc per the charter).

All bar indices below are **closed-candle indices**: bar `i` is only usable
once bar `i` has closed. No rule may reference an in-progress candle.

---

## 0. Shared primitives (referenced throughout)

| Primitive | Definition |
|---|---|
| `swings(tf, k=2)` | Fractal swing high/low, confirmed `k` bars after the pivot (existing `smc_engine.swings`, unchanged). |
| `ATR(tf, n=14)` | Standard 14-period true range average on timeframe `tf`, computed on **closed** candles only. |
| `wick_ratio(candle, side)` | `(body_edge − wick_extreme) / (high − low)` for the wick on `side`. Reused from `liquidity_sweeps`' existing `min_wick_ratio` convention so E1/E2/E3 all judge "rejection" the same way. |
| `mitigation_status(zone, from_i)` | `FRESH` (never touched) → `MITIGATED` (touched, not invalidated) → `INVALIDATED` (closed through the far side). Existing `smc_engine.mitigation_status`, extended to POIs (§3) and IFVGs (§6). |
| UTC normalization | **[FIXED]** All timestamps MUST be normalized to UTC before any rule in this spec runs. This is a hard precondition, not a per-rule detail — see §9. |

---

## 1. Direction: neutral, not locked

**v3.5 problem:** `VARIANT_TABLE` hard-codes one direction per variant
(e.g. `E1M1: SELL`) because each variant was reverse-engineered from a single
historical chart. The runtime then only fires a variant when that fixed
direction agrees with the live HTF bias — meaning e.g. E1M1 can *structurally
never* trade BUY even in a bull regime. That's an artifact of a 1-example
fixture set, not a strategy rule.

**v3.6 rule [FIXED]:** all 9 E×M cells are **direction-neutral**. Direction
is a **Stage-3 output**, computed live from the E-trigger's reaction
(§2–§4), never a lookup. `VARIANT_TABLE` in code drops the `direction` key
entirely; only `horizon` stays per-variant (horizon is a timing property of
the E×M combination, not a bias artifact — E1M3's `MULTI_HORIZON` runner
behavior applies whether the setup is long or short).

The 9 historical examples in v3.5 §2 remain valid regression fixtures for
**one direction each** (the direction that was actually observed) — v3.6
fixtures must add the **mirror-direction case** for at least 3 variants
(synthetic, since no chart exists) to prove the engine isn't silently still
direction-locked.

---

## 2. E1 — D1 gap, precise definition

**v3.5 problem:** "D1 gap fill/reaction at H1 context" — no definition of
what constitutes a gap (true price gap only exists at the weekly open for
FX; continuous-trading crypto never gaps), no freshness bound, no reaction
criteria.

**v3.6 rule:**

1. **Gap object [FIXED].** A D1 gap is a 3-candle D1 imbalance (D1 FVG),
   using the existing `fvgs()` algorithm applied to the D1 series:
   bullish gap when `D1[i-2].high < D1[i].low`; bearish when
   `D1[i-2].low > D1[i].high`. This is asset-agnostic (works for FX, metals,
   and 24/7 crypto alike), unlike a literal open≠prior-close gap which only
   exists for FX/metals at the weekly open.
2. **Freshness [TUNABLE, default `e1_gap_max_age_d1_bars = 10`].** The gap
   must have formed within the last 10 D1 bars (~2 trading weeks) and not be
   `INVALIDATED` per `mitigation_status` (a D1 close fully through the far
   boundary kills it).
3. **H1 reaction [TUNABLE, default `e1_reaction_window_h1_bars = 6`].**
   E1 confirms on the H1 bar where price **first** enters the gap zone
   `[lower, upper]` (per D1 series) AND, within the next
   `e1_reaction_window_h1_bars` H1 closed candles (inclusive of the touch
   bar), an H1 candle closes back outside the zone toward the gap's origin
   side with `wick_ratio >= 0.4` **[TUNABLE, `e1_wick_ratio_min = 0.4`]** on
   the zone-side wick. If no qualifying reaction closes within the window,
   the touch is spent — no retry on the same gap.
4. **Bias:** reaction closing back below the zone (bearish gap origin) → SELL
   context; back above (bullish gap origin) → BUY context. This bias feeds
   Stage 3 (§1), it is not itself the trade direction until an M-model
   confirms.

---

## 3. E2 — POI creation, freshness, mitigation, invalidation

**v3.5 problem:** "H1 price reaction at a marked POI (supply/demand/
liquidity)" — doesn't say which structure type counts as a POI, doesn't
define when a POI expires or how many times it can be traded.

**v3.6 rule:**

1. **POI object [FIXED].** Primary POI type = H1 Order Block, using the
   existing `order_blocks(k=2)` algorithm unchanged (last opposite-color
   candle before a confirmed H1 BOS). Zone = `[ob.low, ob.high]`.
2. **Creation index [FIXED]:** the OB's `i` from `order_blocks()`.
3. **Freshness / mitigation / invalidation [FIXED, reuses
   `mitigation_status`]:**
   - `FRESH`: no H1 candle has traded into `[low, high]` since creation.
   - `MITIGATED`: at least one H1 candle has traded into the zone without a
     close fully through the far boundary.
   - `INVALIDATED`: an H1 candle **closed** beyond the far boundary (price
     accepted through the zone, structure broken). An invalidated POI can
     never fire E2 again.
4. **Max age [TUNABLE, default `e2_poi_max_age_h1_bars = 60`]** (~2.5
   weeks). A POI older than this expires even if still `FRESH` — a
   HTF cause that old is no longer a credible reason for a fresh reaction.
5. **Firing condition [FIXED]:** E2 confirms on the **first** H1 candle
   that both (a) trades into the POI zone and (b) closes back out of the
   zone on the reaction side with `wick_ratio >= 0.4` (same threshold as
   §2.3, for consistency). This is necessarily the transition
   `FRESH → MITIGATED`; a POI already `MITIGATED` from a prior untraded
   touch does not re-fire (§12, one-signal-per-structure).

---

## 4. E3 — external liquidity, precise definition + reclaim window

**v3.5 problem:** "H1 sweep + reclaim of external liquidity" doesn't
distinguish external (range-boundary) liquidity from internal
liquidity/inducement (§ below, used by M1), and doesn't bound how long after
the sweep wick the reclaim close must happen.

**v3.6 rule:**

1. **Dealing range [TUNABLE, default `e3_range_lookback_h1_bars = 40`].**
   The current H1 dealing range is `[low, high]` of the most recent
   confirmed swing low and swing high within the last 40 H1 bars
   (~1.5 weeks).
2. **External level [FIXED]:** a swing point qualifies as *external*
   liquidity only if it **is** the extremity of that dealing range (the
   most recent confirmed swing high for BSL, swing low for SSL within the
   lookback) — not a minor swing sitting inside the range (that's internal
   liquidity / inducement, reserved for M1, §5).
3. **Sweep [FIXED]:** an H1 candle's wick pierces the external level
   (`high > level` for a BSL sweep, `low < level` for SSL) with
   `wick_ratio >= 0.5` on the piercing side (existing `liquidity_sweeps`
   default, unchanged for continuity).
4. **Reclaim window [TUNABLE, default `e3_reclaim_window_h1_bars = 1`].**
   The close must move back inside the range within the sweep bar itself
   or the **immediately next** H1 bar. A close that only reclaims 2+ bars
   later is a different structure (a slow range-reclaim, not a sweep) and
   does not qualify as E3.
5. **Bias:** BSL sweep+reclaim → SELL context; SSL sweep+reclaim → BUY
   context.

---

## 5. Displacement threshold (ATR-normalized, no qualitative terms)

**v3.5 problem:** "displacement" appears in M1 (character change) and M3
(sweep + displacement → IFVG) with no threshold at all.

**v3.6 rule [FIXED mechanism, TUNABLE constants]:**

A **displacement move** starting at M5 bar `s` is the maximal run of
same-direction M5 candles beginning at or within
`displacement_start_offset_bars = 2` **[TUNABLE]** bars of the triggering
sweep, where:

- each candle in the run has `body_ratio = |close-open|/(high-low) >= 0.5`
  **[TUNABLE, `displacement_body_ratio_min = 0.5`]**,
- the run is at most `displacement_max_bars = 3` **[TUNABLE]** candles long,
- and the **cumulative directional range** (from the first candle's open to
  the last candle's close, in the move direction) satisfies:

```
cumulative_range >= displacement_atr_mult * ATR(M5, 14)
```

with `displacement_atr_mult = 1.5` **[TUNABLE]**.

If no run starting within the offset window satisfies this, there is no
displacement — the setup is void (no M1/M3 structure can form without it).
This replaces every instance of "strong displacement" in the source
material with a single reusable, numeric test.

---

## 6. IFVG inversion, precise definition

**v3.5 problem:** "sweep + displacement → IFVG, entry after ≥50% retrace" —
doesn't define what makes an FVG "inverted," or how old the FVG can be when
it inverts.

**v3.6 rule [FIXED mechanism, TUNABLE constants]:**

1. **Source FVG:** an M5 FVG per existing `fvgs()`, formed during or
   immediately after a qualifying displacement move (§5) — the FVG's index
   must fall within `[s, s + displacement_max_bars + 1]` where `s` is the
   displacement start bar (§7 ties this to the required sequence).
2. **Inversion [FIXED]:** a bullish FVG `[lower, upper]` inverts to bearish
   when an M5 candle **closes** below `lower` (a full close, not a wick)
   within `ifvg_max_age_m5_bars = 20` **[TUNABLE]** bars of FVG formation.
   Mirror for bearish → bullish (close above `upper`). No close-through
   within the age window → the FVG never becomes tradeable as an IFVG and
   expires as a plain FVG.
3. **Retrace entry [FIXED, matches existing code convention]:** after
   inversion, price must retrace back to at least the zone **midpoint**
   `(lower+upper)/2` — i.e. ≥50% of the zone width, measured from either
   boundary, which are equivalent since midpoint is exactly 50% — within
   `ifvg_retrace_max_bars = 30` **[TUNABLE]** bars of the inverting close.
   Entry anchor = the midpoint (unchanged from v3.5/current code).

---

## 7. Required event order

**v3.5 problem:** stated as prose ("sweep + displacement → IFVG, entry
after retrace") with no explicit index constraints, so nothing stops the
detector from matching a sweep and a displacement that happened days apart,
or a zone that formed before the sweep that supposedly caused it.

**v3.6 rule [FIXED]**, using bar indices (all same timeframe unless noted):

```
i_sweep                                        <- liquidity taken (§4 or the
                                                   inducement sweep for M1)
i_sweep < i_disp_start <= i_sweep + displacement_start_offset_bars
i_disp_start <= i_disp_end <= i_disp_start + displacement_max_bars - 1
i_disp_start <= i_zone_creation <= i_disp_end + 1     (FVG/OB/Gold-Zone must
                                                        form during/right
                                                        after displacement)
i_zone_creation < i_entry <= i_zone_creation + max_retrace_wait_bars
i_entry = the FIRST bar meeting the retrace/overlap condition (no scanning
          ahead for a "better" later touch — first qualifying bar wins)
```

`max_retrace_wait_bars` is model-specific: `ifvg_retrace_max_bars = 30` for
M3 (§6), and the same 30-bar default **[TUNABLE,
`m1_m2_retrace_max_bars = 30`]** for M1/M2 pullback and Gold-Zone entries,
for consistency unless backtesting shows a model-specific value is needed.

Any candidate structure that violates this ordering (e.g. a zone that
predates its sweep) is rejected outright, not scored lower.

---

## 8. Maximum age of every setup component

Consolidated from the per-section limits above, plus the cross-stage bound:

| Component | Parameter | Default | Type |
|---|---|---|---|
| D1 gap (E1) → H1 reaction | `e1_reaction_window_h1_bars` | 6 | TUNABLE |
| D1 gap itself | `e1_gap_max_age_d1_bars` | 10 | TUNABLE |
| H1 POI (E2) | `e2_poi_max_age_h1_bars` | 60 | TUNABLE |
| External liquidity range (E3) | `e3_range_lookback_h1_bars` | 40 | TUNABLE |
| Sweep → reclaim (E3) | `e3_reclaim_window_h1_bars` | 1 | TUNABLE |
| Sweep → displacement start | `displacement_start_offset_bars` | 2 | TUNABLE |
| Displacement run length | `displacement_max_bars` | 3 | TUNABLE |
| FVG → IFVG inversion | `ifvg_max_age_m5_bars` | 20 | TUNABLE |
| Inversion → retrace entry | `ifvg_retrace_max_bars` | 30 | TUNABLE |
| Zone creation → M1/M2 entry | `m1_m2_retrace_max_bars` | 30 | TUNABLE |
| **E-trigger (Stage 1) → M-model (Stage 2)** | `max_e_to_m_h1_bars` | 12 | TUNABLE |

The last row is a new cross-stage bound not implied by any per-component
limit: an H1 E-trigger that confirmed 12+ H1 bars ago is stale context even
if its own component ages (above) haven't individually expired — the causal
link between "why we're biased this way" and "why we're entering now" gets
weaker the further apart they are. A stale E-trigger requires a fresh
Stage-1 re-confirmation, not a reused old one.

---

## 9. Session and timezone rules

**v3.5 problem:** silent on both. Master Plan gap #3 already flags that
broker candle timestamps ≠ UTC.

**v3.6 rule:**

1. **UTC normalization [FIXED, hard precondition].** Every rule in this
   spec operates on UTC-normalized timestamps. `broker_offset_hours` must be
   resolved and applied (existing `backtest_v35.normalize_time`) before any
   detection or session check runs. A pipeline that skips this step is not
   spec-compliant regardless of what else it gets right.
2. **Session windows [TUNABLE]:**
   - London: `06:00–10:00 UTC`
   - New York: `11:30–15:00 UTC`
   - An M-model entry (§10) is only valid if its trigger bar's UTC time
     falls inside one of these windows. Outside them → the setup is
     discarded (NO-GO), regardless of pattern quality.
3. **Weekday only [FIXED]:** Monday–Friday UTC. The Friday-close→Sunday-open
   weekend gap is excluded from all timeframes (no signal evaluation on
   candles spanning the weekend close).
4. **DST [FIXED, documented approximation]:** session windows are **fixed
   UTC clock times**, not shifted for US/UK daylight saving. Real killzone
   liquidity behavior tracks local exchange-open times which do drift by an
   hour twice a year; a fixed-UTC window is a deliberate simplification
   (killzones are multi-hour wide, so a 1-hour seasonal drift is a partial-
   window effect, not a total miss). Flagged here so it isn't silently
   assumed correct.
5. **News filter:** explicitly **out of scope** — the charter already
   excludes "news-driven or fundamental trading" from the system, so v3.6
   defines no red-folder exclusion calendar.

---

## 10. Entry type

**v3.5 problem:** "entry at pullback/FVG midpoint" doesn't say whether that
means a resting limit order at the midpoint (better fill, needs tick-level
fill monitoring the pipeline doesn't have), an immediate market fill the
instant intra-candle price touches the midpoint (acts on unclosed-candle
information), or a confirmation-close-based entry.

**v3.6 rule [FIXED]:** **confirmation-close, executed at next-bar-open.**
The entry anchor condition (retrace to midpoint / zone entry, per M1/M2/M3)
must be satisfied by a bar's **close** (not an intra-bar touch). The order
is then placed as a market order at the **open of the following bar**. This
matches the existing `backtest_v35.py` convention
(`entry = m5[i+1]["open"]`) and the charter's `closed_candles_only`
principle — it deliberately trades a small amount of fill-price precision
for not requiring sub-bar tick data or resting-limit-order fill simulation,
which the current pipeline has neither the data granularity nor the MT5
plumbing to model correctly. Live execution mirrors this: no resting limit
orders at the theoretical midpoint; a market order fires once the M5
confirmation candle has closed.

---

## 11. Target selection hierarchy + no-DOL behavior

**v3.5 problem:** "pre-selected DOL from target_source" names a source per
horizon but not a search algorithm, and the current code has a real defect:
when no DOL is found, `primary_tp` is `None`, `realized_rr` is computed as
`None`, and `generate_signal`'s gate (`ok = (realized_rr is None) or
(realized_rr >= min_rr)`) treats `None` as **passing** — i.e. a setup with
literally no valid target currently clears the R:R gate. That's backwards.

**v3.6 rule [FIXED]**, in priority order:

1. **Primary:** nearest opposing **external** liquidity level (§4 definition
   — the current dealing-range extremity, not an internal swing) beyond
   entry in the trade direction, on H1 (INTRADAY/OVERNIGHT variants) or with
   D1-context extension (INTRAWEEK/MULTI_HORIZON variants), that has not
   already been swept, searched within
   `target_search_lookback_h1_bars = 100` **[TUNABLE]** bars.
2. **Fallback:** if none found in (1), nearest un-swept M5 swing extremum
   beyond entry within the M5 window (existing `_dol_target` logic,
   unchanged).
3. **No-DOL [FIXED — corrects the v3.5 defect]:** if neither (1) nor (2)
   finds a qualifying target, the setup is **rejected** (`decision:
   "REJECT_NO_TARGET"`), not passed through with `realized_rr = None`
   treated as satisfying `min_rr`. A trade with no identified destination is
   not a trade, regardless of how clean the entry structure looks.

`tp1 = entry ± 1R` is unaffected by this — it's a management partial, not
gated by DOL existence, since it's derived purely from the stop distance
that's already been validated by the time TP1 is computed.

---

## 12. Signal expiry + one-signal-per-structure

**v3.5 problem:** no expiry rule, and no de-duplication — the same POI/zone
can fire repeatedly on every scan that happens to touch it again, which is
the direct mechanism behind the observed overtrading (231–816 trades across
7–13 months on real backtests, roughly 1–2 per day for a strategy meant to
wait for a specific HTF cause).

**v3.6 rule [FIXED]:**

1. **Signal expiry:** once Stage 1 + Stage 2 both confirm and an entry
   anchor is set, the signal is valid for exactly **one** fill attempt: the
   next bar's open (§10). If that bar is missed for any operational reason
   (system down, MT5 disconnected, Telegram/ops failure), the signal
   **expires** — it is not re-attempted on a later bar. `signal_ttl_bars =
   1` **[FIXED]**.
2. **One-signal-per-structure:** each unique structure — keyed by
   `(symbol, variant, structure_type, creation_index)` where
   `structure_type ∈ {d1_gap, h1_poi, h1_sweep_level, ifvg}` — may produce
   **at most one** signal across its entire lifetime, even if price returns
   to it multiple times before it expires (§8 ages) or gets invalidated
   (§2–§4 mitigation rules). A persistent "consumed structures" record
   (symbol, variant, structure key) must be checked before evaluating a
   candidate structure and updated the moment a signal fires from it —
   independent of whether that signal is ultimately filled, rejected by
   risk (§ risk gates), or expires unfilled. This is a hard cap on
   opportunities per structure, not a per-scan or per-day cap.

---

## 14. Strategy state machine

The strategy must run through an explicit lifecycle rather than ad hoc
signal handling. The canonical state machine is:

```text
WAIT_HTF
  ↓
WAIT_EVENT
  ↓
WAIT_MODEL
  ↓
WAIT_ENTRY
  ↓
OPEN_POSITION
  ↓
MANAGE_POSITION
  ↓
EXIT
  ↓
COOLDOWN
  ↺
NO_GO
  ↺
ERROR
  ↺
```

| State | Inputs | Outputs | Allowed transitions | Invalid transitions | Timeout |
|---|---|---|---|---|---|
| `WAIT_HTF` | UTC-normalized HTF candles | E-trigger context | `WAIT_EVENT` when HTF bias is established | Any entry check before HTF bias | Expire when HTF context ages beyond §8 |
| `WAIT_EVENT` | HTF bias + live candles | Candidate E1/E2/E3 event | `WAIT_MODEL` on first valid event | Reusing an expired structure | Expire when component ages fail |
| `WAIT_MODEL` | Event + M5 confirmation window | Model candidate | `WAIT_ENTRY` when M-model confirms | Confirming without closed-candle evidence | Expire at `max_e_to_m_h1_bars` |
| `WAIT_ENTRY` | Confirmed model + entry anchor | Entry intent | `OPEN_POSITION` on next-bar open fill | Resting-limit improvisation | Expire after `signal_ttl_bars` |
| `OPEN_POSITION` | Filled entry | Managed trade record | `MANAGE_POSITION` immediately | Missing stop or journal | Immediate fail-safe if SL absent |
| `MANAGE_POSITION` | Live position + management rules | Adjusted stop / partials | `EXIT` when rule closes trade | Widening stop or unmanaged drift | Timeout per management rule |
| `EXIT` | Close event | Closed trade record | `COOLDOWN` after journal | Reopening same structure | None |
| `COOLDOWN` | Closed trade + consumed structure | No new entry | `WAIT_HTF` when fresh structure appears | Re-entering same consumed structure | Cooldown = structure-specific |
| `NO_GO` | Rejected signal, risk rejection, or invalid setup | Rejection record | `WAIT_HTF` on next evaluation cycle | Any broker call or entry attempt | None; terminal for that cycle |
| `ERROR` | Runtime fault, missing data, broker disconnect, invariant failure | Error record + alert | `WAIT_HTF` after recovery/reset | Any trade continuation without recovery | Immediate fail-closed |

The engine must persist state transitions and reject invalid transitions as
spec violations.

`NO_GO` is the explicit deterministic rejection state for validly evaluated
setups that fail a signal, risk, or execution gate. `ERROR` is the explicit
fail-closed state for runtime faults and invariant breaches.

---

## 15. Formal risk model

The strategy risk model is fixed and deterministic.

- Maximum risk per trade: `0.5%` fixed.
- Maximum daily loss: `2%`.
- Maximum weekly loss: `5%`.
- Maximum concurrent trades: `1` unless a later version explicitly allows more.
- Correlation rule: do not exceed the daily risk limit across positively
  correlated symbols that share the same bias.
- Equity protection: block new entries when drawdown exceeds the configured cap.
- Kill switch: immediate global no-trade state on risk breach, reconciliation
  failure, or execution failure.

Every candidate trade must return one of:

- `APPROVED`
- `REJECTED_RISK`
- `REJECTED_SESSION`
- `REJECTED_SPREAD`
- `REJECTED_DRAWDOWN`
- `REJECTED_MARGIN`
- `REJECTED_ENVIRONMENT`

Every rejection must include a machine-readable reason code.

---

## 16. Trade management

Trade management is part of the strategy, not an afterthought.

- Initial stop loss is mandatory before entry.
- Break-even move after `+1R` if the trade structure remains valid.
- Partial profit taking is allowed only if defined in the versioned spec.
- Trailing stop is optional, but if present it must never widen risk.
- Time stop: exit when the maximum holding horizon is exceeded.
- Weekend exit: close before the weekend if the trade is still open and the
  strategy disallows weekend carry.
- Forced exit: close immediately on invalidation or kill-switch activation.
- Manual override: allowed only in the runtime wrapper, never inside the
  strategy rule itself.

Exit reasons:

- `TARGET_HIT`
- `STOP_HIT`
- `BREAK_EVEN`
- `PARTIAL_TAKE`
- `TIME_STOP`
- `WEEKEND_EXIT`
- `INVALIDATION_EXIT`
- `FORCED_EXIT`

---

## 17. Position sizing

Position sizing must be deterministic and broker-compatible.

```text
risk_amount = equity × risk_percent
lot_size = risk_amount ÷ stop_value_per_lot
```

Where `stop_value_per_lot` is computed from the broker's actual contract size,
tick size, tick value, and volume step.

- Round down to the nearest valid volume step.
- Reject if the minimum valid lot would exceed risk limits.
- Reject if broker contract specification is unavailable or stale.
- Use the same calculation in backtest, replay, demo, and live modes.

---

## 18. Market regime filter

The strategy should know when not to trade.

- `TRENDING`
- `RANGING`
- `EXPANDING`
- `CONTRACTING`
- `VOLATILE`
- `QUIET`

Regime guidance:

- `RANGING` favors E3-style liquidity sweeps.
- `TRENDING` favors bias-aligned continuation or pullback structures.
- `VOLATILE` reduces size or blocks entry if spread and slippage expand.
- `QUIET` can block entry if price movement is insufficient to justify risk.

Regime classification must be deterministic and based on closed-candle data.

---

## 19. Strategy confidence score

Signals may carry a `0-100` confidence score to support ranking and filtering.
The score must never override hard invalidation rules.

Example weights:

- HTF alignment: 25
- POI quality: 20
- Liquidity quality: 20
- Displacement quality: 15
- Session fit: 10
- Risk-reward quality: 10

Decision bands:

- `>= 85` → trade
- `70–84` → optional / requires policy allowance
- `< 70` → reject

The score is advisory only. Hard rules still win.

---

## 20. Parameter registry

All tunable values must be listed in one registry rather than scattered through
the document.

The registry is the sole authoritative source for tunable values, units, and
version history. Every parameter used by the strategy must appear exactly once.

| parameter | type | units | default | range | owner | tunable | version | last_changed | reason |
|---|---|---|---|---|---|---|---|---|---|

Examples:

- `e1_gap_max_age_d1_bars`
- `e2_poi_max_age_h1_bars`
- `e3_range_lookback_h1_bars`
- `displacement_atr_mult`
- `ifvg_retrace_max_bars`
- `max_e_to_m_h1_bars`
- `max_daily_loss_pct`
- `max_concurrent_trades`

The code must read tunable values only from this registry. If a parameter is not
listed here, it is not part of the approved specification.

---

## 21. Research protocol and validation gates

Any material change to the strategy must follow the research workflow below:

```text
Hypothesis
  ↓
Backtest
  ↓
Walk-forward
  ↓
Monte Carlo
  ↓
Sensitivity
  ↓
Out-of-sample
  ↓
Approval
```

Minimum validation gates:

- Minimum trades: `500`
- Profit factor: `> 1.30`
- Sharpe: `> 1.40`
- Maximum drawdown: `< 12%`
- CAR/MDD: `> 0.5`
- OOS profit factor: `> 1.20`
- Monte Carlo stability: `95%`
- Bootstrap: pass
- Walk-forward: pass

These are approval gates, not optimization goals.

---

## 22. Multi-timeframe synchronization

The engine must synchronize D1, H1, and M5 deterministically.

- D1 updates daily.
- H1 updates hourly.
- M5 updates every five minutes.
- HTF refresh invalidates stale lower-timeframe assumptions.
- POI freshness and signal TTL are enforced at the state-machine level.
- Cache lifetime must never outlive the component ages defined in §8.

If a higher timeframe changes, lower-timeframe candidates derived from the old
context must be re-evaluated.

---

## 23. Execution layer behavior

The strategy spec defines the behavior expected from execution, even before the
execution layer exists.

Required execution flow:

```text
Signal
  ↓
Risk
  ↓
Order
  ↓
Broker
  ↓
Fill / Reject / Partial Fill
  ↓
Journal
```

This is the canonical decision pipeline for the strategy: every candidate
must either progress through the pipeline or terminate in `NO_GO` or `ERROR`.

Execution rules:

- One canonical execution path only.
- Duplicate-order prevention is mandatory.
- Rejected orders must be logged with reason codes.
- Partial fills must be represented as partial fills, not full fills.
- MT5 disconnects must fail closed.
- Execution may never invent new strategy logic.

---

## 24. Audit logging

Every trade must be reconstructable from the audit trail.

Required fields:

- execution ID
- signal ID
- strategy version
- approval status
- parameter snapshot
- parameter registry version
- configuration hash
- dataset version
- code commit / build identifier
- HTF state
- POI or liquidity structure IDs
- entry
- stop
- target
- reason codes
- decision
- runtime
- broker response
- hash / checksum

Logs must be append-only and deterministic enough for retrospective review.

Each closed trade record must be sufficient to reproduce the decision path from
market data + specification + parameter registry alone.

---

## 25. Version governance

Strategy versions must follow a lifecycle:

```text
RESEARCH_CANDIDATE
  ↓
EXPERIMENTAL
  ↓
VALIDATED
  ↓
APPROVED
  ↓
PRODUCTION
  ↓
DEPRECATED
```

Each version must carry:

- approval date
- approval package reference
- validation report
- validation dataset version
- performance summary
- changelog entry
- owner approval reference

The approval package must contain:

- strategy version
- parameter registry snapshot
- dataset version
- backtest summary
- walk-forward summary
- Monte Carlo summary
- OOS summary
- reviewer / owner sign-off

Approved versions are immutable. Any rule change creates a new version.

---

## 26. What v3.6 changes vs. current code (implementation checklist)

Not part of the spec itself — a pointer for the implementation pass this
document is gating:

- [ ] `VARIANT_TABLE`: drop per-variant `direction`; compute live (§1).
- [ ] `detect_e_trigger`: replace "any H1 sweep/OB" with §2 (D1 gap + H1
      reaction), §3 (POI freshness/mitigation state machine), §4 (external
      vs internal liquidity distinction + reclaim window).
- [ ] Wire the currently-unused `d1` parameter of `signal_v35.analyze()`
      into the E1 path (§2).
- [ ] Add ATR-normalized displacement check (§5) — currently absent
      entirely; M1/M3 structure detection has no displacement gate.
- [ ] Add IFVG inversion + age check (§6) — `detect_structure_m3` currently
      checks retrace but not the inversion close or its age.
- [ ] Add explicit bar-index sequencing validation (§7) — currently
      structures are matched by "exists somewhere in the window," not by
      order.
- [ ] Add per-component age checks (§8) — currently the bounded lookback
      windows (from the perf fix) are a backtest-speed mechanism, not a
      spec-driven freshness rule; they need to become the latter.
- [ ] Add UTC normalization as a hard precondition + session-window gate
      (§9) — `broker_offset` exists but is optional/manual, not enforced.
- [ ] Confirm entry mechanism matches §10 (it already does — document only).
- [ ] Fix the no-DOL defect (§11) — `REJECT_NO_TARGET` when no target found.
- [ ] Add signal expiry + consumed-structures tracking (§12) — this is
      expected to be the single biggest lever on the observed overtrading.

This checklist is the input to the next `backtest-researcher` cycle: harden
detection to this spec, re-run `backtest_v35.py` on the same
EURUSD/XAUUSD/BTCUSD history used for the v3.5 baseline
(377/816/231 trades, 10–23% win rate, all negative expectancy), and compare
before/after. `engine_implements_spec` stays `false` until that comparison
is done and reviewed — implementing this spec doesn't itself clear the M2
exit gate, passing the backtest on locked out-of-sample data does.
