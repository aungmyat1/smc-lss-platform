# ST-C2 Owner-Decision Brief — G4, G7, and RCR Pre-Registration Gaps

Date: 2026-07-23
Author: Claude (governance synthesis; read-only documentation drafting)
Status: DRAFT FOR OWNER DECISION — nothing here is decided, closed, or approved.

## Purpose and scope

This brief prepares the owner for a decision session on the three remaining
blockers that stand between ST-C2 "Hybrid Liquidity-First Unified SMC Pipeline"
and *implementation authorization*:

1. **G4** — premium/discount location semantics (entirely open at decision
   level).
2. **G7** — stop-distance minimum/maximum sanity bounds (open residual after the
   2026-07-23 correction).
3. **RCR pre-registration gaps** — primary/secondary metrics, allowed parameter
   changes, max experiment count, multiple-testing controls, OOS calendar
   boundaries.

Every option below is grounded in material already on record in the repository.
Where the repo contains no prior proposal for an item, this brief says so
explicitly rather than inventing strategy design. This document decides nothing;
it lays out options, tradeoffs, and — only where the repo's own evidence
supports one — a recommended default the owner may accept, reject, or amend.

Sources this brief is grounded in:
- `reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md` (RCR + 2026-07-23 addendum
  + G7 correction)
- `reports/audit/ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md` (audit + post-addendum
  status)
- `docs/RESEARCH-CHARTER.md` (six-question pre-registration template)
- `specs/st-c2.yaml` (the filed candidate spec)
- Generic supporting material where noted: `.claude/skills/premium-discount/SKILL.md`,
  `docs/reference/smc-8step-entry-model-dailypriceaction.md`

---

## 1. G4 — Premium/Discount Location

### 1.1 What G4 actually gates

G4 requires that an entry sit on the correct side of the dealing-range
equilibrium for its direction (long only in discount, short only in premium),
with OTE bounding the acceptable retracement. The gate is expressed in two
places in `specs/st-c2.yaml`.

`ote_stage` (verbatim):

```yaml
ote_stage:
  fib_anchor_mode: swing_extremes
  discount_threshold: 0.5
  premium_threshold: 0.5
  long_only_in_discount: true
  short_only_in_premium: true
  max_retrace_pct: 0.786
```

and the paired `htf_bias_stage.bias_rules` (verbatim):

```yaml
bias_rules:
  long_bias_requires_discount: true
  short_bias_requires_premium: true
```

The governance audit's G4 row (`ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md` §F)
states the gate's defined evidence and its missing rules verbatim:

> G4 premium/discount | `fib_anchor_mode: swing_extremes`,
> `discount/premium_threshold: 0.5`, `max_retrace_pct: 0.786` | Dealing-range
> anchor tie-break; equilibrium (exactly 0.5) treatment; range
> invalidation/reselection | Positive/negative/boundary(0.5 exact) |
> `WRONG_PREMIUM_DISCOUNT`

So the *thresholds* exist (anchor mode = swing extremes, split at 0.5, max
retrace 0.786), but three deterministic sub-decisions are undefined:

- **(a) dealing-range anchor tie-break** — which two swing extremes anchor the
  fib when more than one candidate pair exists;
- **(b) equilibrium exactly-0.5 treatment** — what happens when price sits
  precisely at the 50% line;
- **(c) range invalidation/reselection** — when the active dealing range is
  discarded and a new one selected.

### 1.2 State of the record for G4

The ST-C2 research trail (RCR + addendum + audit) has **not drafted any
decision-level option** for these three sub-decisions. Both source documents
say so explicitly:

- RCR addendum, G4 section (verbatim): "**Not closed by any of the 12
  decisions.** Dealing-range anchor tie-break, equilibrium (exactly 0.5)
  treatment, and range invalidation/reselection remain fully open. This is the
  least-addressed gate in this addendum."
- Post-addendum audit table (verbatim): "G4 | **NOT DEFINED** | entirely open —
  no owner decision addresses dealing-range anchors, equilibrium treatment, or
  reselection".

**Therefore: no ST-C2-specific option is on record for the owner to pick from.**
G4's three sub-decisions require fresh owner input, not a selection among
pre-drafted ST-C2 alternatives.

### 1.3 Generic repo material that could seed options (NOT yet proposed for ST-C2)

The repo does contain generic, platform-level premium/discount material that the
owner (or a later implementation step) could *choose to adopt* as ST-C2's G4
rule. It is surfaced here so the owner knows candidate definitions exist to draw
on — but none has been proposed, endorsed, or wired to ST-C2, and adopting any
of it is itself an owner decision.

- `.claude/skills/premium-discount/SKILL.md` defines a generic method:
  - dealing range = "the valid dealing range (last impulse leg)" — note this is
    a *different* anchor definition from the spec's `fib_anchor_mode:
    swing_extremes`; the owner would need to reconcile "last impulse leg" vs
    "swing extremes" if this material is adopted;
  - equilibrium = `(high + low) / 2`;
  - exactly-at-equilibrium treatment: "Price at equilibrium -> no directional
    edge, wait" (i.e. a no-trade / reject outcome — a candidate answer to
    sub-decision (b));
  - undefined range: "request market-structure output" (a partial answer toward
    sub-decision (c), but not a reselection trigger);
  - OTE band 0.62–0.79 (the spec instead caps retrace at 0.786).
- `docs/reference/smc-8step-entry-model-dailypriceaction.md` Step 4 (verbatim):
  "Use a modified Fibonacci with the 50% level as the dividing line." This is
  the teaching source ST-C2's 0.5 split is modeled on; it does not resolve
  anchor tie-break or reselection.

Tradeoff note on these generic sources: they were written as discretionary
human-analyst guidance, not as point-in-time deterministic engine rules. The
"last impulse leg" range definition in particular is under-specified for a
no-look-ahead engine (what counts as the current impulse leg, and when it
rolls, is itself a swing-definition question — the same G1/G2 swing-definition
blocker the addendum lists as open). So they can *seed* the anchor and
equilibrium decisions but do not close them.

### 1.4 Minimum decision the owner needs to make to unblock G4

Three concrete choices, none currently drafted for ST-C2:

- **(a) Anchor definition + tie-break:** confirm or replace `swing_extremes`,
  and state the rule for choosing the anchor swing pair when multiple qualify
  (e.g. most-recent confirmed swing pair; widest qualifying range; a specific
  lookback). No ST-C2 candidate exists — this is fresh input.
- **(b) Equilibrium exactly-0.5 handling:** decide whether price exactly at 0.5
  is DISCOUNT, PREMIUM, or NO-TRADE/reject. The generic skill's "wait"
  (no-trade) is available as a candidate to adopt; the spec's `>= 0.5` /
  `<= 0.5` thresholds currently overlap at exactly 0.5 and must be disambiguated.
- **(c) Range invalidation/reselection:** state when the active dealing range is
  discarded and a new one anchored (e.g. on a new confirmed HTF swing beyond the
  range extreme, or on bias change). No candidate on record.

### 1.5 Recommended default for G4

**No recommendation issued.** The repo's ST-C2 evidence does not point to one
option over another for any of the three sub-decisions — the trail explicitly
records G4 as entirely open. Issuing a default here would be authoring strategy
design, which this brief must not do. The generic premium-discount material in
§1.3 is offered as candidate input the owner may adopt, not as a recommendation.

---

## 2. G7 — Stop-Distance Min/Max Sanity Bounds

### 2.1 What the 2026-07-23 correction found

An earlier version of the RCR addendum stated G7 was "fully closed." The
2026-07-23 correction reversed that. The correction text in the RCR addendum's
G7 section reads (verbatim):

> **G7 — structural invalidation/stop. PARTIAL at the complete-contract level**
> (correction, 2026-07-23 — an earlier version of this addendum stated G7 was
> "fully closed"; that was inaccurate and is corrected here). Decision 6 closes
> the stop anchor and buffer rule: anchor = beyond the liquidity-sweep extreme,
> buffer = 2 broker-native points (resolving the pips-vs-points ambiguity the
> audit flagged), direction = rounded outward, precision = XAUUSD symbol
> precision. **Not closed**: explicit minimum and maximum stop-distance sanity
> bounds. The audit's original gate table
> (`ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md` §F) listed "min/max distance" as a
> required rule for G7 alongside anchor/buffer/precision — it was not, as the
> earlier version of this addendum incorrectly stated, something "no one flagged
> as required." None of the 12 decisions supplies a minimum or maximum
> stop-distance bound, so this residual remains open and is carried into the
> consolidated remaining-blockers list below, not treated as non-blocking.

The consolidated remaining-blockers list restates the residual (verbatim):

> **G7 — minimum and maximum stop-distance sanity bounds remain an
> owner/specification decision.** Decision 6 fixes the stop anchor, buffer,
> rounding direction, and precision, but not distance limits — a setup with an
> anchor-derived stop that is unrealistically tight or unrealistically wide has
> no rule to reject or flag it.

So: **the stop *anchor* is fully specified (decision 6); the *sanity bounds* on
the resulting distance are not.** Without them, a computed stop that is
absurdly tight (e.g. inside the spread) or absurdly wide (e.g. destroying RR)
has no rule to reject it.

### 2.2 Proposed bounds on record

**None.** No minimum or maximum stop-distance bound is proposed anywhere in the
ST-C2 research trail. The RCR addendum, the audit §F table, and the post-addendum
consolidated blocker list all state that none of the 12 owner decisions supplies
one, and no numeric bound appears in `specs/st-c2.yaml` (which defines only
`stop.mode: structural_invalidation` and `stop.buffer_pips: 2`). This item is
**genuinely blank** — fresh owner input, not a selection among candidates.

Available *context* the owner may want in the room when setting a minimum (this
is context, not a proposed bound): the audited XAUUSD cost profile is
`config/research_costs.yaml` v1 — spread 25.0 points, slippage 5.0 points
(`ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md` §C). A minimum stop distance below
spread + slippage would be economically incoherent; that is a natural floor to
reason from, but the repo does not state it as a rule and this brief does not
set it.

### 2.3 The specific remaining decision

The owner needs to specify two numbers (or a rule that yields them), in XAUUSD
broker-native units, with fail-closed behavior:

- **Minimum stop distance** — below which a setup is rejected (candidate reasoning
  anchor: not tighter than spread + slippage, i.e. > 30 points on the audited
  cost profile — but the exact floor is the owner's to set).
- **Maximum stop distance** — above which a setup is rejected (a wide stop
  collapses achievable RR and position size; the value is the owner's to set).
- **Rejection behavior** — confirm both bounds fail closed with an explicit
  rejection code (the audit assigns G7 the code `STOP_INVALID`), consistent with
  the platform-wide fail-closed discipline decision 10 already established.

---

## 3. RCR Pre-Registration Gaps

For each item: what `docs/RESEARCH-CHARTER.md` requires by default, what ST-C2's
RCR currently has, and the minimum choice the owner must make.

The charter's six-question template requires, per field (verbatim headings):
"Why", "Evidence", "Hypothesis", "Expected improvement" (which demands "A
number, before running anything"), "Success criteria" (an "OOS-backed bar…tie to
`backtest-researcher`'s ACCEPT/REJECT gate"), and "Rollback criteria". It also
requires (verbatim) that "The log's entry count IS the trial count
`optimization`/deflated-Sharpe should use as an input once that infrastructure
exists."

### 3.1 Primary / secondary metrics

- **Charter default:** the "Expected improvement" field demands a *number* stated
  before running, and "Success criteria" demands an OOS-backed bar tied to the
  ACCEPT/REJECT gate. The template implies named, quantified metrics but does not
  itself enumerate which.
- **ST-C2 RCR current state:** the audit's RCR completeness matrix records
  "Primary/secondary metrics | NOT IMPLEMENTED | Not named". So the RCR field is
  **blank** — the metrics are not named in the ST-C2 RCR.
- **Repo material to draw from (exists):** the platform promotion bar is
  well-defined elsewhere — `ROADMAP.md` / `docs/CHARTER.md`: PF >= 1.3,
  expectancy >= +0.2R, DD <= 15%, >= 30 trades; and owner decision 12 adds the
  population floors (>= 30 for feasibility, >= 100 before any statistical claim).
  These are the metrics that already gate promotion; the RCR simply has not
  *designated* which are primary vs secondary for ST-C2.
- **Minimum owner choice:** designate primary metric(s) (candidate: expectancy in
  R and Profit Factor as co-primary, matching the promotion bar) and secondary
  metric(s) (candidate: win rate, DD, trade count, avg RR). This is a *selection
  and labeling* of metrics already defined in the repo, not fresh design.

### 3.2 Allowed parameter changes

- **Charter default:** the charter governs *when a parameter change is allowed*
  (the six-question gate must be answered first) but does not pre-list which
  parameters a given candidate may vary.
- **ST-C2 RCR current state:** audit matrix — "Allowed parameter changes | NOT
  IMPLEMENTED | Not addressed". The one thing on record is a *negative*
  constraint from the RCR's "Expected improvement" section (verbatim): "`min_rr:
  3.0` and `per_trade_risk_pct: 0.5` remain hard floors from the filed spec; this
  RCR does not propose changing either." So: one constraint stated (these two are
  fixed), no positive list of what *may* be swept. **Mostly blank.**
- **Minimum owner choice:** state the allowed-to-vary parameter set (or state
  "none — fixed spec, existence test only" for the first pass). This is largely
  fresh input; the only fixed points on record are `min_rr` and
  `per_trade_risk_pct`, which stay frozen.

### 3.3 Max experiment count

- **Charter default:** the charter ties trial count to the research-log entry
  count and expects it to feed deflated-Sharpe "once that infrastructure exists",
  but sets no per-candidate cap.
- **ST-C2 RCR current state:** audit matrix — "Max experiment count | NOT
  IMPLEMENTED | Not addressed". **Blank**, and no candidate value anywhere in the
  ST-C2 trail. **Genuinely blank — fresh owner input.**
- **Minimum owner choice:** pick a maximum number of backtest experiments /
  parameter trials permitted for ST-C2 before the multiple-testing penalty
  forces a stop or a discount (a single integer, e.g. "N experiments, logged to
  `reports/research_log.md`"). No value is on record to select from.

### 3.4 Multiple-testing controls

- **Charter default:** the charter states the intended mechanism (verbatim): the
  research-log entry count "IS the trial count `optimization`/deflated-Sharpe
  should use as an input once that infrastructure exists", motivated by the
  deflated-Sharpe rationale in `reports/quant_research_audit.md` §13.
- **ST-C2 RCR current state:** audit matrix — "Multiple-testing controls | NOT
  IMPLEMENTED | Not addressed". So the platform *intent* exists but is **not
  instantiated for ST-C2**, and the deflated-Sharpe infrastructure the charter
  refers to does not yet exist.
- **Minimum owner choice:** decide the concrete control to apply to ST-C2 — e.g.
  commit to deflated-Sharpe keyed to the ST-C2 research-log trial count once
  built, or an interim rule (Bonferroni-style discount, or a hard trial cap per
  §3.3). Partially seedable from the charter's stated intent; the concrete
  instantiation is the owner's decision.

### 3.5 OOS calendar boundaries

- **Charter default:** "Success criteria" requires an OOS-backed bar; the
  template does not itself fix calendar partitions.
- **ST-C2 RCR current state:** audit matrix records Development / Validation /
  Sealed OOS periods all as "NOT IMPLEMENTED | Not stated". BUT owner **decision
  11** sets the *policy* (verbatim): "Existing XAUUSD history is not pristine
  sealed OOS. It may support development and walk-forward diagnostics only. A new
  future period must be locked for genuine forward/OOS evidence before
  promotion." The post-addendum audit confirms decision 11 "sets the policy, not
  the dates." So the **policy is fixed; the exact calendar boundaries are blank.**
- **Minimum owner choice:** convert the policy into concrete boundaries — either
  (a) name a cutoff date splitting existing history into development vs.
  walk-forward, plus the start date of the locked forward/OOS window, or (b)
  specify a fixed holdout (e.g. lock all data after date D as sealed OOS; use a
  fixed % of the remainder for walk-forward validation). Policy already decided;
  only the dates/percentages are needed.

---

## 4. Session Agenda

Ordered to unblock the most downstream work first, with an estimate of effort
based on how much is already drafted vs. blank, and an explicit "done" target.

1. **G4 — premium/discount location (FIRST; longest).** Rationale: G4 is the
   *only* item that is entirely open at decision level with no ST-C2-specific
   option drafted — it needs three fresh decisions (anchor+tie-break, exactly-0.5
   handling, reselection). It also gates the largest downstream surface: the OTE
   stage sits mid-pipeline and every qualifying entry must pass it, so leaving it
   open blocks the whole conjunctive pipeline's determinism. Likely the longest
   discussion (candidate material from §1.3 exists to seed it, but reconciling
   "swing extremes" vs "last impulse leg" and defining reselection is real
   design work). **Done =** the three G4 sub-decisions written down as
   deterministic rules ready to be encoded into an ST-C2 spec fragment.
2. **G7 — stop-distance min/max bounds (SECOND; short).** Rationale: fully
   isolated (anchor already fixed by decision 6), affects only stop sanity, and
   reduces to specifying two numbers plus a rejection behavior. No candidate
   values on record, but the decision surface is small and the cost-profile
   context (§2.2) gives a natural floor to reason from. **Done =** minimum and
   maximum stop distance specified numerically in XAUUSD broker-native units,
   both fail-closed with the `STOP_INVALID` code.
3. **RCR pre-registration fields (THIRD; medium, mostly fill-in-the-blank).**
   Rationale: these gate *validity of eventual evidence*, not pipeline
   determinism, so they can follow the strategy-semantics decisions; four of the
   five draw on material already in the repo (§3.1 promotion bar, §3.4 charter
   intent, §3.5 decision-11 policy, plus the negative constraint in §3.2), so
   most of the time is designation and dates rather than fresh design. The two
   genuinely-blank sub-items (max experiment count §3.3; the positive
   allowed-parameter list §3.2) are quick single-value calls. **Done =** all five
   RCR fields filled: primary/secondary metrics designated, allowed-parameter set
   stated, max experiment count set, multiple-testing control chosen, OOS
   cutoff date or holdout % fixed.

**What should exist in the repo after the session:** a further RCR addendum (or
a fresh owner-decision record) capturing (i) the three G4 rules, (ii) the two G7
bound numbers, and (iii) the five completed RCR pre-registration fields — filed
per `docs/RESEARCH-CHARTER.md`, documentation-only, with `specs/st-c2.yaml`
still unmutated and `engine_implements_spec: false`. Per the addendum's own
closing note, versioning a new spec file (e.g. carrying the closed contract) is a
separate, still-open path question — not something the session is obligated to
produce.

---

## 5. What Does NOT Get Unblocked By This Session

Closing G4, G7, and the RCR pre-registration gaps authorizes **only** the
*implementation* of ST-C2 (i.e. it gives a future, separately-authorized
engineering step a deterministic contract to build against). It explicitly does
**not**:

- **NOT** authorize any backtest result to pass the promotion bar. Closing the
  contract says nothing about whether ST-C2 makes money.
- **NOT** predict or guarantee that ST-C2 will clear the evidence gates. Those
  gates remain: **PF >= 1.3, expectancy >= +0.2R, out-of-sample validation, max
  DD <= 15%, >= 30 trades** (and, per owner decision 12, >= 100 completed trades
  before any statistical performance claim — a result below 100 is
  INSUFFICIENT/OVERFILTERED, not evidence). This brief cannot and does not
  forecast that outcome.
- **NOT** authorize M3 execution-layer work. M3 remains not-yet-sequenced under
  `MASTER_PLAN.md` / `ROADMAP.md`; ST-C2 research sits in M2.
- **NOT** authorize demo or live trading. Demo autonomy stays `proposal_only`,
  live autonomy stays `disabled`, `promote_to_live: false` — unchanged by this
  brief and unchanged by the session it prepares.

Implementation authorization itself still requires an explicit
`project-governance-agent` / owner decision *after* the contract is closed; a
closed contract is a precondition for that decision, not the decision itself.

---

## Provenance and non-authority note

This brief is a synthesis of existing repository artifacts. It creates no
authority, closes nothing, and approves nothing. It does not appear in the
document-authority hierarchy in `CLAUDE.md`. No option, default, or agenda item
in it is an owner decision until the owner records one. No word "CLOSED" or
"APPROVED" is asserted about any gate herein.
