# Research Change Request — ST-C2 "Hybrid Liquidity-First Unified SMC Pipeline"

Filed per `docs/RESEARCH-CHARTER.md` before any new backtest runs, code, or
conformance-kernel work. Owner supplied a fully specified pipeline
(`specs/st-c2.yaml`) directly, in the same mode `specs/v3.9.yaml`'s "Clean
SMC" preset and `specs/v3.10.yaml`'s "Reversal Capture" preset were both
supplied — this RCR documents it before any code is written, per the
`project-governance-agent` ruling recorded in `NEXT_ACTION.md` (2026-07-22,
"file the ST-C2 RCR before any implementation") and echoed in `ROADMAP.md`'s
Phase 2 section and `PROJECT_STATUS.md` §5.

## Change: ST-C2 "Hybrid Liquidity-First Unified SMC Pipeline" (new candidate: `specs/st-c2.yaml` v1.0.0, `engine_implements_spec: false`)
Date: 2026-07-22
Author: Claude (research agent), on behalf of owner-supplied spec

### Why
The ST-C1 v3.9/v3.10 line was parked earlier today: both candidates are
net-losing in every symbol tested (v3.9 aggregate net PF 0.138, v3.10
aggregate net PF 0.471), roughly 10x below `ROADMAP.md`'s PF >= 1.3 /
expectancy >= +0.2R promotion bar, with no further open diagnostic
plausibly rescuing either under the validated cost model (`PROJECT_STATUS.md`
§5, `reports/audit/ST_C1_V39_VS_V310_COMPARISON.md`). Both are structurally
the same family: an HTF-bias-then-disjunctive-branching design (E1/E2/E3
triggers competing via tie-break, M1/M2/M3 confirmation). The owner directed
a new candidate testing a *different architecture* rather than a further
parameter nudge to ST-C1: a conjunctive, all-stages-must-pass sequential
pipeline (liquidity/inducement -> HTF bias -> OTE -> FVG alignment -> LTF
CHoCH -> execution) intended to replicate the entry sequencing seen in
visual SMC teaching material more directly than ST-C1's branching-trigger
design ever attempted to. This is a materially different trade thesis, not
an edit to any ST-C1 spec — hence a new candidate ID (`ST-C2`) rather than a
v3.11 continuation of the parked line.

### Evidence
- `PROJECT_STATUS.md` §5 / `ROADMAP.md` Phase 2 (2026-07-22 entries): the
  ST-C1 v3.9/v3.10 parked-line evidence is the reason a structurally
  different design is being tried now rather than continuing to tune ST-C1.
- `specs/st-c2.yaml` (owner-supplied, reproduced verbatim, already committed
  at `1704725`) is the direct specification for this change: H4/M15/M3
  timeframe triple, six conjunctive pipeline stages (liquidity/inducement,
  HTF bias, OTE, FVG alignment, LTF confirmation, execution), `min_rr: 3.0`,
  `per_trade_risk_pct: 0.5`, only XAUUSD currently `enabled: true`
  (EURUSD/GBPUSD both `enabled: false` in the filed spec).
- No prior backtest evidence exists for this exact design (unlike v3.9,
  which had the v3.7/v3.8 funnel diagnosis to react to) — **this is
  disclosed as a limitation, not concealed.** The "expected improvement"
  below is therefore a design/existence intent, not a number derived from
  this repo's own prior backtest data, matching the same disclosed-limitation
  pattern `ST_C1_V310_REVERSAL_CAPTURE_RCR.md` used for v3.10.

### Hypothesis
Requiring ALL of: (a) an external liquidity sweep/inducement reaction at
HTF (H4) before anything else is evaluated; (b) H4 bias confirmed via a
close-confirmed BOS/CHoCH with displacement (body-ratio >= 0.6); (c) MF
(M15) premium/discount placement (OTE, max 78.6% retrace) consistent with
that bias direction; (d) an HTF FVG with an overlapping MF FVG, plus an LTF
FVG required at entry; (e) an LTF (M3) CHoCH with displacement (body-ratio
>= 0.5) and a stronger-CHoCH confirmation — will together identify
liquidity-engineered SMC setups that are structurally invisible to ST-C1's
design, because ST-C1 never required joint multi-timeframe alignment across
all of liquidity, bias, location, and confirmation simultaneously — it
accepted any one of E1/E2/E3 firing independently. The conjunctive,
sequence-enforced structure is the mechanism under test, not any single
stage's threshold value.

### Expected improvement
Stated before running anything, as design/existence intent rather than a
number derived from prior data (see Evidence's disclosed limitation),
matching v3.10's RCR precedent:
1. The engine produces at least one qualifying signal on XAUUSD's local
   history — the only symbol `specs/st-c2.yaml` currently enables. This is
   an existence/non-triviality check, not a population-size claim.
2. A population-feasibility floor (trade count sufficient for a
   statistically meaningful funnel) is deferred to a follow-up RCR
   addendum once initial signal counts are observed, exactly as v3.10's RCR
   deferred its own — no floor is precommitted here because none can yet be
   justified from data.
3. `min_rr: 3.0` and `per_trade_risk_pct: 0.5` remain hard floors from the
   filed spec; this RCR does not propose changing either.

**Scope decision on symbol coverage (resolved here, not left implicit):**
this RCR and its resulting engine test **XAUUSD only**, matching the spec
as filed. Enabling EURUSD/GBPUSD (both `enabled: false` in `specs/st-c2.yaml`)
to pursue a multi-symbol population-feasibility criterion (as ST-C1's >=5-
per-symbol-in->=2-symbols bar was) is an explicit scope expansion requiring
its own RCR addendum before those symbols are enabled and backtested — not
a silent extension once the XAUUSD engine exists.

### Success criteria
(a) Engine implements the full six-stage pipeline with point-in-time,
no-look-ahead, closed-candle-only detection and deterministic tie-breaks,
passing positive/negative/mirror golden-case tests per stage (liquidity
sweep, HTF bias, OTE, FVG alignment, LTF CHoCH, execution/stop/target); (b)
`min_rr: 3.0` and `per_trade_risk_pct: 0.5` enforced unchanged from the
filed spec; (c) at least a qualitative existence check (>=1 signal) on
XAUUSD; (d) no fail-open or look-ahead defect in any of the six pipeline
stages; (e) `engine_implements_spec` stays `false` until the full
conformance suite passes, matching this repo's established convention for
every prior ST-C1 candidate at this stage.

### Rollback criteria
- Zero qualifying signals on XAUUSD across its full local history ->
  REJECTED within these exact parameters; report the full per-stage funnel
  (liquidity_events -> bias_pass -> location_pass -> fvg_pass -> choch_pass
  -> entry_ready) and escalate to the owner for parameter reconsideration
  rather than ad hoc loosening.
- Any fail-open/look-ahead defect found in any stage -> stop, fix, and
  re-verify before any run is treated as evidence.
- Any attempt to enable EURUSD/GBPUSD or otherwise expand scope beyond
  XAUUSD without a follow-up RCR addendum -> non-compliant with this RCR,
  must be reverted or covered by a new addendum before proceeding.

---
Logged to `reports/research_log.md` in date order alongside this entry, per
`docs/RESEARCH-CHARTER.md`. No backtest was run and no code was written
before this template was filed. `specs/st-c2.yaml` is retained as filed
(`status: candidate`, `engine_implements_spec: false`) — this RCR does not
itself constitute a backtest run or an ACCEPT verdict, and does not
authorize implementation on its own. Per precedent
(`ST_C1_V310_E1_TIEBREAK_RCR.md`), this RCR is filed and then awaits explicit
`project-governance-agent`/owner authorization before any conformance-kernel,
detector, or backtest work begins.

---

## Addendum: owner decisions recorded, deterministic gap closure (2026-07-23)

Filed per `docs/RESEARCH-CHARTER.md`, following the read-only governance/
conformance audit `reports/audit/ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md`
(2026-07-22), which classified this RCR and `specs/st-c2.yaml` as
`RCR_ADDENDUM_REQUIRED` — population-feasibility floor deferred, an
unresolved internal `rr_min` conflict (2.0 vs 3.0), and most of gates
G1-G10 plus the entry/order-simulation rules lacking exact deterministic
formulas, tie-breaks, freshness/invalidation rules, and rejection codes.

The owner (Aung) reviewed that audit and issued the following explicit
written authorization, recorded verbatim:

> "I authorize documentation-only closure of the ST-C2 RCR gaps. This does
> not authorize strategy-engine implementation, backtesting, optimization,
> demo execution, live execution, promotion, or broker operations."

This addendum is **documentation-only**. No code was written. No spec file
was mutated — `specs/st-c2.yaml` is unchanged, `engine_implements_spec`
stays `false`. No backtest was run. No execution/demo/live/promotion/
approval state was changed. This addendum does not itself authorize
implementation; it closes the semantic gaps the audit identified so that a
future, separately-authorized implementation step has a deterministic
contract to build against — and it explicitly identifies what still isn't
closed, per the instruction not to fill any remaining gap without an owner
decision behind it.

### Owner decisions (recorded verbatim below; exactly 12, no additions)

1. T1 must provide at least 2.0R. A setup is entry-eligible only if a
   preselected T2 also provides at least 3.0R net after costs.
2. The limit-entry price is the proximal boundary of the qualifying LTF
   FVG, representing first touch. Confirmation must close first. The
   earliest eligible fill is the following bar.
3. When several external liquidity pools qualify, select the nearest by
   absolute price distance. Tie-break by most recent confirmation
   timestamp, then stable identifier.
4. An FVG is eligible while mitigation is below 50% of its price depth.
   Penetration of 50% or more invalidates it. The formula, boundaries and
   rounding must be stated explicitly.
5. BOS and CHOCH must be mutually exclusive based on the prior confirmed
   bias. A discretionary same-bar priority is forbidden.
6. Stop anchor is beyond the liquidity-sweep extreme plus two
   broker-native points, rounded outward to XAUUSD symbol precision.
7. T1 and T2 must be selected before entry. T1 is the partial-take
   objective; T2 is the runner objective. A trade without both valid
   objectives is rejected.
8. An unfilled limit expires after 15 closed M3 bars, or earlier upon FVG
   invalidation, structural invalidation, bias change or session
   ineligibility.
9. Fill eligibility starts on the next bar. When entry, stop and target
   ordering cannot be inferred from available bar data, apply stop-first
   resolution.
10. Reward eligibility is net after spread, slippage, commission and
    applicable swap using the versioned XAUUSD row in
    `config/research_costs.yaml`. Missing cost-profile identity or symbol
    metadata fails closed.
11. Existing XAUUSD history is not pristine sealed OOS. It may support
    development and walk-forward diagnostics only. A new future period
    must be locked for genuine forward/OOS evidence before promotion.
12. Require >=30 completed trades for population feasibility and >=100
    completed trades before making a statistical performance claim. A
    result below 100 is INSUFFICIENT/OVERFILTERED, not evidence of
    profitability.

### Gate-by-gate closure (using ONLY the 12 decisions above)

**G1 — HTF bias.** Decision 5 closes the BOS/CHoCH same-bar ambiguity: the
two are mutually exclusive, determined by the prior confirmed bias, with no
discretionary priority rule permitted. **Not closed** by any of the 12: the
underlying HTF swing definition (lookback/pivot rule) and the
protected-structure creation/invalidation lifecycle. These remain
unresolved — listed below as remaining blockers, not filled here.

**G2 — external/protected structure.** Decision 3 closes multi-candidate
liquidity-pool selection: nearest by absolute price distance; tie-break by
most recent confirmation timestamp, then a stable identifier. **Not
closed**: the external-vs-internal swing distinction, and the exact
protected high/low creation/invalidation lifecycle (decision 3 governs
*selecting among qualifying pools*, not *what makes a pool/protected level
exist or expire* in the first place). Also not closed: the exact
composition of the "stable identifier" itself (decision 3 says to use one
as a final tie-break but does not define its fields).

**G3 — close-confirmed BOS/CHoCH.** Decision 5's mutual-exclusivity rule
closes the same-bar classification ambiguity between BOS and CHoCH
(applies to G1 and G3 alike, since G3 is where that classification is
mechanically applied). **Not closed**: the exact wick-probe-rejection
mechanics beyond the spec's existing `close_beyond_structure_required: true`
field, and the first-counter-trend-break-vs-later-shift distinction across
multiple CHoCH events over time.

**G4 — premium/discount location.** **Not closed by any of the 12
decisions.** Dealing-range anchor tie-break, equilibrium (exactly 0.5)
treatment, and range invalidation/reselection remain fully open. This is
the least-addressed gate in this addendum.

**G5 — fresh/valid HTF POI/FVG.** Decision 4 closes the freshness/
invalidation *rule* precisely: an FVG is eligible while mitigation is below
50% of its own price depth (i.e. `penetration_pct = mitigated_depth /
total_zone_depth`, computed against the zone's own proximal/distal
boundaries), and is invalidated the instant `penetration_pct >= 50%` (the
50% boundary itself invalidates — inclusive, not exclusive, per "50% or
more invalidates"). Rounding: since decision 4 requires the formula,
boundaries and rounding to be "stated explicitly" and gives no numeric
rounding convention beyond XAUUSD symbol precision (which decision 6
separately pins for stops only), the rounding step for this penetration
ratio is **not fully closed** — a rounding convention (e.g. round-half-up
to broker point precision before comparing to 50%) still needs an explicit
owner or engineering-spec decision at implementation time; flagged as a
residual, non-blocking-for-documentation-purposes but blocking-for-
implementation detail below. **Not closed at all**: the 3-candle FVG
formation formula itself (which candles bound the gap, minimum size/
displacement formula beyond the existing `min_displacement_bars: 3` count)
and multi-zone tie-break when several FVGs qualify simultaneously. These
are not addressed by any of the 12 decisions and are not inferred from
other candidates' engines here, per instruction not to invent semantics
beyond the 12 decisions.

**G6 — LTF sweep + structure confirmation.** Decisions 2 and 9 close fill
timing precisely (confirmation must close first; earliest eligible fill is
the following bar). Decision 8 closes the expiry/cancellation window (15
closed M3 bars, or earlier on FVG invalidation, structural invalidation,
bias change, or session ineligibility). **Not closed**: the exact
reclaim-close timing rule for the liquidity sweep itself (which specific
bar's close satisfies `close_back_in_range_required: true`), the
relationship between `max_setup_bars: 20` (existing spec field) and the
15-bar expiry window now set by decision 8, and first-qualifying-bar
behavior for the LTF CHoCH detection step itself (as opposed to fill
timing, which decisions 2/9 do cover).

**G7 — structural invalidation/stop.** **PARTIAL at the complete-contract
level** (correction, 2026-07-23 — an earlier version of this addendum
stated G7 was "fully closed"; that was inaccurate and is corrected here).
Decision 6 closes the stop anchor and buffer rule: anchor = beyond the
liquidity-sweep extreme, buffer = 2 broker-native points (resolving the
pips-vs-points ambiguity the audit flagged), direction = rounded outward,
precision = XAUUSD symbol precision. **Not closed**: explicit minimum and
maximum stop-distance sanity bounds. The audit's original gate table
(`ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md` §F) listed "min/max distance"
as a required rule for G7 alongside anchor/buffer/precision — it was not,
as the earlier version of this addendum incorrectly stated, something "no
one flagged as required." None of the 12 decisions supplies a minimum or
maximum stop-distance bound, so this residual remains open and is carried
into the consolidated remaining-blockers list below, not treated as
non-blocking.

**G8 — net reward after costs.** **Fully closed.** Decision 1 resolves the
`rr_min` conflict the audit flagged (GC-4 / P1 defect): T1 >= 2.0R and a
preselected T2 >= 3.0R net after costs are both required for entry
eligibility — `t1_liquidity.rr_min: 2.0` and `risk.min_rr: 3.0` are not in
conflict once read this way; they describe two different, both-mandatory
thresholds (T1's own floor, and the overall trade's floor via T2). Decision
10 closes the cost model: net after spread, slippage, commission, and
applicable swap, using the versioned XAUUSD row in
`config/research_costs.yaml`; missing cost-profile identity or symbol
metadata fails closed (satisfies the fail-closed requirement already
established platform-wide by `docs/RESEARCH-CHARTER.md` and
`src/config.py`'s loader discipline). The evaluation point for net-R
(evaluated against the actual fill price under decision 2's entry
convention, not a theoretical entry) follows directly from decisions 1, 2,
and 10 taken together and is not a new invented rule.

**G9 — logical target before entry.** **Fully closed** by decisions 1 and
7: T1 and T2 are both selected and validated before entry; T1 is the
partial-take objective, T2 is the runner objective; a trade lacking either
valid objective is rejected outright. This also resolves the "can a 2R T1
coexist with a 3R minimum" question the audit raised: yes, as two separate,
jointly-mandatory objectives, not as alternates.

**G10 — precommitted trade management.** Decision 8 closes the *unfilled
limit order's* expiry/cancellation triggers. The spec's existing
`break_even_activation_r: 1.5`, `partial_take_r: 2.0`,
`partial_take_fraction: 0.5`, `runner_enabled: true` remain unchanged and
apply to a filled position's management, consistent with decisions 1/7's
T1/T2 framing. **Not closed by any of the 12 decisions**: a time stop or
session-close rule for an *already-filled, open* position (decision 8
covers only the pre-fill limit order, not post-fill management), and any
emergency-exit rule.

**Entry/order-simulation rules.** Substantially closed by decisions 2, 8,
9, and 10 taken together: exact limit price (proximal FVG boundary, first
touch), placement/confirmation-close timing, earliest eligible fill (next
bar), limit expiry (15 closed M3 bars or the four listed early-cancellation
triggers), and same-bar entry/stop/target ambiguity (stop-first
resolution, decision 9). **Not closed**: bid/ask treatment (which side of
the spread the FVG boundary and fill price are measured against),
gap-through handling (price gapping past the limit level between bars),
partial-fill policy, and one-position/duplicate-setup behavior when more
than one qualifying setup exists concurrently (decision 3's tie-break
governs *selecting among liquidity pools*, not *concurrent trade
candidates* generally).

### Remaining blockers (explicitly outside the 12 decisions — not filled here)

1. **G1/G2** — HTF/external swing definition (lookback/pivot rule),
   external-vs-internal swing distinction, and protected high/low
   creation/invalidation lifecycle.
2. **G2** — exact composition of the "stable identifier" used as the final
   tie-break in decision 3.
3. **G3** — wick-probe-rejection mechanics beyond the existing
   `close_beyond_structure_required` field; first-counter-trend-break vs.
   later-shift distinction across multiple CHoCH events.
4. **G4** — dealing-range anchor tie-break, equilibrium (0.5 exact)
   treatment, range invalidation/reselection. Entirely open — no decision
   among the 12 addresses G4.
5. **G5** — 3-candle FVG formation/size formula (zone boundary
   definition itself); multi-zone tie-break; explicit rounding convention
   for the decision-4 penetration ratio.
6. **G6** — liquidity-sweep reclaim-close timing (which bar's close
   satisfies `close_back_in_range_required`); relationship between the
   existing `max_setup_bars: 20` field and decision 8's 15-bar expiry;
   first-qualifying-bar behavior for LTF CHoCH detection itself.
7. **G7** — minimum and maximum stop-distance sanity bounds remain an
   owner/specification decision. Decision 6 fixes the stop anchor, buffer,
   rounding direction, and precision, but not distance limits — a setup
   with an anchor-derived stop that is unrealistically tight or unrealistically
   wide has no rule to reject or flag it.
8. **G10** — time stop / session-close / emergency-exit rules for an
   already-filled open position (distinct from decision 8's pre-fill limit
   expiry).
9. **Entry/order-simulation** — bid/ask treatment, gap-through handling,
   partial-fill policy, concurrent duplicate-setup handling.
10. **RCR pre-registration items untouched by the 12 decisions**: primary/
   secondary metrics beyond the population thresholds in decision 12,
   allowed parameter changes, maximum experiment count, multiple-testing
   controls. Decision 11 resolves the *policy* on OOS integrity (existing
   history = development/walk-forward only; a new future period must be
   locked before promotion) but does not itself fix the exact calendar
   boundaries of development/validation/sealed-OOS partitions — that
   remains a mechanical detail for whenever implementation is separately
   authorized, not a semantic gap, and is non-blocking for this
   documentation-only addendum.

### Status after this addendum

`specs/st-c2.yaml` is unchanged (not touched by this addendum, per the
owner's documentation-only authorization). `engine_implements_spec` stays
`false`. This addendum does **not** authorize strategy-engine
implementation, backtesting, optimization, demo execution, live execution,
promotion, or broker operations — matching the owner's authorization text
verbatim. G4 is entirely undefined; G1, G2, G3, G5, G6, G7, G10, and the
entry/order-simulation rules are each PARTIAL, with specific residuals
listed above (G7's residual: minimum/maximum stop-distance sanity bounds).
Only G8 and G9 are fully closed by the recorded owner decisions. Per the
owner's own instruction, none of these gaps is filled by inference — they
are listed above rather than resolved. A further RCR addendum (or a fresh set of
owner decisions) is required to close the remaining blockers before
implementation can be authorized. Once the strategy-semantics contract is
fully closed, the next authorized action is to version and publish a new
spec file reflecting the closed contract (see the governance report for
the recommended path) — that file is not created by this addendum.

---

## Second addendum (2026-07-23, owner-decision session round 2)

Documentation-only, per the same owner authorization scope as the first
addendum: does **not** authorize strategy-engine implementation,
backtesting, optimization, demo execution, live execution, promotion, or
broker operations. `specs/st-c2.yaml` remains unchanged and unread-only
referenced below; `engine_implements_spec` stays `false`. This session
closes G4, G7's stop-distance residual, and all five outstanding RCR
pre-registration items. It does **not** close G5 in full (see below), nor
G1, G2, G3, G6, G10, or the entry/order-simulation residuals already listed
above — those remain open exactly as stated in the first addendum.

### G4 — Premium/discount location (now CLOSED)

1. **Swing source:** the dealing range's anchoring swing is
   `liquidity_stage`'s external-liquidity swing pair (the same swing
   `detect_external_liquidity` already computes for the H4, 300-bar
   lookback) — not a separately-computed swing, and not
   `htf_bias_stage`'s BOS/CHoCH-confirmed swing.
2. **Range update policy:** the range **freezes** once identified at the
   triggering external swing; it is never recalculated for that setup even
   if a later, more-recent qualifying swing appears before entry.
3. **Anchoring-swing invalidation:** if the anchoring external swing is
   later invalidated (e.g., a subsequent BOS breaks through it) before
   entry triggers, the **entire setup is invalidated immediately** — no
   persistence on the stale swing, no re-anchoring.
4. **Equilibrium boundary:** exact point at 0.5, **zero-width** — matching
   `.claude/skills/premium-discount/SKILL.md`'s literal "no directional
   edge, wait" wording, not a tolerance band. No band width (e.g., an
   earlier-discussed ±0.02) is adopted; any such tolerance would be a new
   number requiring its own RCR if wanted later.
5. **OTE band:** the tradeable zone is **`[0.5, 0.786]`** — i.e., from the
   equilibrium threshold (`ote_stage.discount_threshold` /
   `premium_threshold: 0.5`) up to `ote_stage.max_retrace_pct: 0.786`.
   There is **no separate refinement floor** (the skill's generic 0.62
   lower bound is explicitly **not** inherited, since it does not appear
   anywhere in `specs/st-c2.yaml`).

G4's original residual ("dealing-range anchor tie-break, equilibrium
treatment, range invalidation/reselection — entirely open") is resolved by
decisions 1-5 above.

### G5 — Fresh, valid HTF POI/FVG (PARTIAL — not fully closed)

The following four rules are decided and recorded as **new rules added by
owner decision, not rules already present in `specs/st-c2.yaml`**:

1. **HTF↔MTF directional alignment:** full alignment required — HTF
   bullish requires MTF bullish, HTF bearish requires MTF bearish; any
   divergence kills the setup immediately.
2. **LTF placement:** the LTF FVG must sit entirely inside the HTF-MTF
   confluence zone (not extend beyond either boundary, not contradict
   directional bias). **This is a new rule** — `specs/st-c2.yaml` today
   only states `mf_fvg.must_overlap_htf_fvg: true` /
   `max_distance_pips: 10`; there is no equivalent
   `ltf_fvg.must_overlap_mf_fvg`-style field. If this is to be enforced,
   it is an owner-decided addition, not an existing spec rule being
   applied.
3. **FVG size validation:** use only `specs/st-c2.yaml`'s existing
   per-timeframe threshold fields (`htf_fvg`, `mf_fvg`, `ltf_fvg`
   min-size/age/distance values); never infer fib-based or
   volatility-based adjustments.
4. **Multi-FVG behavior:** no stacking/weighting heuristics — all
   qualifying FVGs must collapse into a single confluence zone; no
   "two consecutive FVGs imply stronger bias"-style logic.
5. **FVG invalidation:** if any FVG in the confluence chain is
   invalidated, the entire FVG-alignment result fails and the setup dies
   immediately — no fallback to the next-nearest FVG, no recalculation.
   Consistent with G4 decision 3's invalidation behavior.

**Still open, NOT resolved by the above:** the **3-candle FVG
formation/size formula itself** (i.e., the actual price-boundary formula
an FVG's zone is computed from — `specs/st-c2.yaml` only has
`min_displacement_bars`/`max_age_bars`/overlap-distance fields, never the
gap-boundary formula itself) and the **rounding convention for the G4
(now-closed) 50%-mitigation penetration ratio**. Both residuals are
carried forward unresolved — nothing in this session's discussion touched
them.

### G7 — Structural invalidation and stop (now CLOSED)

1. **Stop buffer (anchor rule) — reconfirmed, unchanged:** 2 broker-native
   points beyond the liquidity-sweep extreme, rounded outward to XAUUSD
   symbol precision, matching owner decision 6 (first addendum) and
   `specs/st-c2.yaml`'s `execution_stage.stop.buffer_pips: 2` exactly (not
   5 — an earlier draft of this session's discussion briefly misquoted
   this as `buffer_points: 5` under a non-existent `invalidation_stage`
   key; corrected before being recorded here).
2. **Minimum stop distance: 35 points.** Rationale: XAUUSD's cost profile
   (`config/research_costs.yaml`) is spread 25 points + slippage 5 points
   = a 30-point cost-noise floor; 35 gives a 5-point margin above that
   floor so the stop cannot sit inside pure transaction-cost noise.
3. **Maximum stop distance: 150 points.** Rationale: a fixed ceiling,
   deliberately not ADR/ATR/volatility-derived, chosen to reject
   structurally-incoherent stops (RR-breaking, "no real stop" distances)
   while remaining well below typical XAUUSD H4 swing spans.
4. **Behavior:** compute `stop_distance = |entry - stop|` from the
   structural anchor + 2-point buffer; if `stop_distance < 35` or
   `stop_distance > 150`, the setup dies immediately; otherwise the stop
   is valid.

These are **owner decisions enforced by the engine internally**, not new
`specs/st-c2.yaml` fields. Adding `min_stop_distance_points` /
`max_stop_distance_points` to the spec itself would require a separate RCR.

G7's original residual ("minimum and maximum stop-distance sanity bounds
remain an owner/specification decision") is resolved by decisions 1-4
above.

### RCR pre-registration — all five remaining items (now CLOSED)

1. **Primary metric: net profit factor (PF).** Matches the `docs/CHARTER.md`
   promotion gate (PF ≥ 1.3) and is the metric most robust to trade-count
   variation. **Secondary metrics:** expectancy, max drawdown, trade count
   — these assess stability of a PF result, they cannot independently
   promote a strategy that fails the PF gate.
2. **Multiple-testing control: deflated Sharpe ≥ 0.3**, keyed to the
   research-log entry (trial) count, per the mechanism `docs/RESEARCH-CHARTER.md`
   already names (lines 73-77: deflated Sharpe corrects for the
   multiple-testing risk of an accept-and-reject log; the log's entry
   count is the trial-count input). Any experiment below this threshold is
   rejected as statistically indistinguishable from overfit noise,
   regardless of its PF.
3. **OOS calendar boundary: prospective lock at 2026-07-23** (the date of
   this owner-decision session) — **not** a retroactive historical split.
   All data before 2026-07-23 is development/walk-forward-diagnostic only,
   never treated as OOS. All data from 2026-07-23 forward is genuine OOS.
   This corrects an earlier draft of this session's discussion that
   proposed a retroactive 2025-01-01 cutoff, which was rejected as
   violating owner decision 11 (first addendum): existing history —
   including everything after 2025-01-01 — has already been used
   diagnostically across the ST-C1 line and cannot be treated as pristine
   OOS regardless of which historical date is chosen as the boundary. Only
   a genuinely future-collected period satisfies decision 11's "new future
   period must be locked" requirement. Promotion requires PF ≥ 1.3 on OOS
   data only.
4. **Maximum experiment count: 12.** No prior value existed anywhere in
   the repo for this item; chosen as small enough to keep the deflated-Sharpe
   trial-count correction meaningful while allowing legitimate iteration.
   If ST-C2 exceeds 12 logged experiments without meeting the PF ≥ 1.3
   gate, the research track is terminated (not silently continued).
5. **Allowed parameter changes (positive list).** During research, only
   these five parameter families may be varied: FVG size thresholds, the
   OTE `max_retrace_pct` value, session-filter windows, spread-gate
   values, and the G7 stop-distance bounds (35/150, decided above).
   Everything else remains frozen, including (explicitly): `min_rr`,
   `per_trade_risk_pct`, any liquidity-stage logic, any HTF bias logic, any
   structural-invalidation logic, any OTE threshold below 0.5, any
   volatility-adaptive parameter, and any symbol-set expansion — all of
   which require a new RCR to change, not researcher discretion.

### Status after this second addendum

Closed this session: **G4 (fully)**, **G7 (fully)**, **all 5 RCR
pre-registration items**. **G5 remains PARTIAL** — four new alignment/
placement/stacking/invalidation rules are recorded, but the FVG
formation/size formula and the mitigation-rounding convention residual
(both already listed in the first addendum) are untouched. **G1, G2, G3,
G6, G10, and the entry/order-simulation residuals remain exactly as listed
in the first addendum** — nothing in this session addressed them.

This addendum does not, by itself, satisfy either of the two remaining
implementation gates: (a) `specs/st-c2.yaml` is still self-declared
`status: candidate`, not an owner-verified canonical/approved spec, and (b)
no `IMPLEMENTATION AUTHORIZATION: GRANTED` string exists anywhere in the
repo. Both remain open, separate owner acts — recording these decisions is
not the same as authorizing implementation, per the owner's own stated
gate structure for this work.

---

## Third addendum (2026-07-24, owner-decision session round 3 — remaining 7-item blocker list)

Documentation-only, same restriction as the first two addenda: does **not**
authorize strategy-engine implementation, backtesting, optimization, demo
execution, live execution, promotion, or broker operations. `specs/st-c2.yaml`
is unchanged; `engine_implements_spec` stays `false`. No code written, no
backtest run, no execution/demo/live/promotion state changed.

**Provenance note, stated plainly because it differs from the first two
sessions:** the first two addenda's decisions were derived from
`specs/st-c2.yaml` and the owner's own strategy document only. This session's
rationale additionally cites external SMC teaching material ("ICT" concepts,
"MentFX") as justification for several implications. That is disclosed here,
not smoothed over — the decisions below are recorded as owner decisions
regardless of their sourcing, exactly as previously scoped, but a reader
should know the reasoning chain now includes external reference material,
not just this repo's own filed documents.

This session answers the 15-question set from
`docs/audit/2026-07-24-st-c2-gate-sequencing-review` (the governance
sequencing review's draft question list), grouped in the same four clusters,
plus records two items from that review's "Phase 1" findings that needed no
owner input at all.

### Phase 1 — closed by existing convention, not owner decision (carried in from the 2026-07-24 governance sequencing review)

- **G3 wick-probe-rejection**: already answered by
  `close_beyond_structure_required: true` plus
  `.claude/skills/choch-bos/SKILL.md`'s existing "close beyond level, not
  just wick" rule. No new decision needed.
- **G6 `displacement_body_ratio_min: 0.5`** and **`break_structure_close_required`**:
  already implemented by `src/smc_engine.py`'s `displacement_move()` (the
  same body-ratio formula `signal_v39.py`/`signal_v310.py` already reuse at
  a different threshold) and the same close-beyond-structure rule as G3.
  No new decision needed.

### Cluster 1 — Swing / Structure (Q1-Q4)

1. **H4 fractal confirmation window (`k`):** `k = 3`.
2. **External vs. internal swing:** external = liquidity outside the
   current dealing range; internal = liquidity inside the current dealing
   range (swept before BOS).
3. **Protected high/low lifecycle:** a protected level invalidates when an
   opposite CHoCH occurs; otherwise it persists.
4. **Multi-CHoCH sequencing:** a second CHoCH confirms continuation; a
   third CHoCH signals trend acceleration or re-classification.

Resolves G1/G2's swing-definition/protected-lifecycle residual and G3's
multi-CHoCH-sequencing residual. Per the 2026-07-24 sequencing review, this
was the load-bearing decision — it also unblocks `internal_bos_required`
(G6) via decision 2 above, and is a precondition for finally verifying
whether the existing `structure_key`/`index_offset` identifier convention
(G2's remaining item, see "Not addressed" below) generalizes to ST-C2.

### Cluster 2 — G6 Timing (Q5-Q7)

5. **`max_setup_bars` (20) vs. `entry_window_bars` (15):** the entry window
   is a subset of the setup window.
6. **First-qualifying-bar tie-break:** the first bar that produces a clean
   CHoCH close wins.
7. **Sweep reclaim-close timing:** a single-bar reclaim close is
   sufficient (no multi-bar confirmation required).

Resolves G6's `max_setup_bars`/`entry_window_bars` relationship,
first-qualifying-bar behavior, and sweep reclaim-close timing residuals.

### Cluster 3 — FVG (Q8-Q10)

8. **`min_displacement_bars: 3` semantic:** fixed 3-candle FVG geometry
   (not a separate variable-length displacement-run concept).
9. **Multi-zone FVG tie-break:** highest timeframe wins (an HTF FVG
   dominates over MF/LTF FVGs when more than one qualifies).
10. **Mitigation-ratio rounding:** round-half-up to broker precision.

Resolves G5's FVG-formation-semantic ambiguity, multi-zone tie-break, and
mitigation-rounding residuals. The FVG age/overlap/distance mechanics
(`max_age_bars`, `max_distance_pips`, `must_overlap_htf_fvg`) remain, per
the sequencing review, "implementation-ready, no decision required" —
mechanical work against numbers the spec already supplies, not a gap
needing an owner answer.

### Cluster 4 — G10 + Order Simulation (Q11-Q14 answered; Q15 NOT answered, see below)

11. **Time stop:** none — management remains structure-based/R-multiple
    only, per the existing trade-management skill.
12. **Emergency exit:** immediate market exit, triggered by spread spikes,
    connection loss, or volatility shocks (illustrative values given:
    spread-spike threshold 20 points, connection-loss threshold 60
    seconds — these are examples in the source material, not yet
    confirmed as the final numeric decision; see open item below).
13. **Bid/ask treatment:** mid-price for FVG boundaries and fills.
14. **Gap-through handling:** fill at open.
15. **Partial-fill policy:** accept partial fills; scale stop/target
    accordingly.

Resolves G10's post-fill time-stop/emergency-exit residual and three of
the four order-simulation residuals (bid/ask, gap-through, partial-fill).

### Not addressed by this session — do not treat as decided

- **Duplicate/concurrent-setup handling** (the fourth order-simulation
  residual, originally Q15 in the governance review's draft list) has
  **no corresponding decision or rationale** in what was provided this
  session. A field-level draft supplied alongside these answers proposes
  `duplicate_setup_policy: one_position_at_a_time`, but no "Q/implication"
  reasoning backs that value the way it does for every other field above —
  it is recorded here as an **unconfirmed proposal**, not an owner
  decision, and must not be treated as closed until the owner explicitly
  confirms it the same way the other 14 items were confirmed.
- **G2's stable-identifier composition** (whether the existing
  `structure_key`/`index_offset` convention from
  `validation/historical_replay_engine_v39.py`/`_v310.py` generalizes to
  ST-C2's H4/M15/M3 structure) is now unblocked by Cluster 1's decisions
  but was not itself verified this session — still open, and per the
  sequencing review this is an engineering-verification task, not a
  further owner-decision question.
- **Emergency-exit numeric thresholds** (spread-spike points,
  connection-loss seconds): recorded above as illustrative examples from
  the session's source material, not confirmed as final by the owner in
  the same explicit way the other values were. Flagged so a future reader
  doesn't treat "20 points / 60 seconds" as equivalent in authority to,
  say, decision 6's "35/150 points" stop-distance bounds from the second
  addendum, which were both stated and reasoned as the actual decision.

### Field-level spec draft (reference only — NOT applied to `specs/st-c2.yaml`)

A field-level YAML draft implementing decisions 1-14 above (new
`htf_structure`/`management` blocks, plus additions to
`ltf_confirmation_stage`, `liquidity_stage.detect_sweep`, `fvg_stage`, and
`execution_stage.entry`) was supplied alongside these decisions and is
preserved verbatim in `reports/research_log.md`'s entry for this addendum
for future reference. Consistent with how the first two addenda's closed
decisions (G4, G7, G8, G9) were never written into `specs/st-c2.yaml`
itself, this draft is **not** applied to the spec file here. Folding it in
— whether as an edit to `specs/st-c2.yaml` or as a new versioned file such
as `specs/st-c2_v1.1.0.yaml` — is exactly the still-open
"canonical-specification-path question" flagged in the first addendum's
closing note, and remains a separate, explicit owner/governance act.

### Status after this third addendum

Closed this session: Cluster 1 (G1/G2 swing definition, G3 multi-CHoCH),
Cluster 2 (G6 timing residuals), Cluster 3 (G5 FVG-formula/tie-break/
rounding residuals), and three of four Cluster 4 items (G10 time-stop/
emergency-exit concept, bid/ask, gap-through, partial-fill). Also closed
via existing-convention verification (not owner decision): G3
wick-probe-rejection, G6 displacement/close-confirmation fields.

**Still open:** G2's stable-identifier generalization (engineering
verification, now unblocked); duplicate/concurrent-setup handling (no
decision given, only an unconfirmed proposed value); emergency-exit's
exact numeric thresholds (illustrative, not confirmed as final).

This addendum does not, by itself, satisfy either of the two remaining
implementation gates: (a) `specs/st-c2.yaml` is still self-declared
`status: candidate`, not an owner-verified canonical/approved spec, and (b)
no `IMPLEMENTATION AUTHORIZATION: GRANTED` string exists anywhere in the
repo. Both remain open, separate owner acts — recording these decisions is
not the same as authorizing implementation, per the owner's own stated
gate structure for this work.
