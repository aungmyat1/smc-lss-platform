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
