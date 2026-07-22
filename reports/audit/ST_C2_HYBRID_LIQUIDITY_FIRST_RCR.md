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
