# ADR-0004 — Intake of ST-C3 as a New Strategy Candidate (Daily Price Action Funnel)

**Status:** Accepted — 2026-07-24, direct owner instruction in the active
session (see conversation record; owner supplied the full funnel description
and confirmed the source documents).
**Deciders:** Project Owner (Aung Myat); project-governance-agent (reviewed,
recommended this ADR before any drafting).
**Depends on / interacts with:** ADR-0001 (Accepted) — two-track lifecycle,
extended here by precedent rather than reopened. `MASTER_PLAN.md`'s existing
`LKZ-1` classification ("new candidate intake only; cannot supersede ST-C2
without a new RCR and Stage A restart") is the direct precedent this ADR
applies.

---

## Context

The owner supplied a complete, deterministic SMC entry-confirmation workflow
(HTF bias -> external liquidity sweep -> displacement/BOS -> OTE ->
FVG/order-block confluence -> LTF CHoCH -> entry window -> structural stop ->
TP1/TP2/TP3 -> expiry), explicitly cross-referencing "both SMC documents" and
asking for it to become a new tradeable candidate ("completely change the
strategy, add new candidate"). The request initially framed this as changes
to "the ST-C2 funnel."

Two governance facts make that framing impossible as stated:

1. `specs/st-c2_v1.2.0.yaml` is **frozen** (`status: frozen`,
   `implementation_authorization: scoped_reference_implementation_granted`
   for S1-G2 reference-implementation work only). Hard rule: "Approved
   strategies are immutable... every strategy revision requires a new
   candidate."
2. The owner's ruleset is not a parameter/threshold revision of ST-C2's
   contract. It defines its own stage sequence, its own evidence-ID system,
   and its own rejection-code system with **different meanings attached to
   the same `R1`-`R7` labels ST-C2 already uses** (verified against
   `specs/st-c2_v1.2.0.yaml` §6: ST-C2's `R1` = `liquidity_stage_failed`,
   `R2` = `htf_bias_failed`, etc. — the owner's `R1` = "HTF bias unclear,"
   `R2` = "no external sweep." These do not merely differ, they invert which
   stage each code number points at). This is a new lineage, not a lineage
   edit — same category as the parked `LKZ-1` branch.

Source-document verification: the owner confirmed (in-session) that "both SMC
documents" are the two files already committed at
`docs/reference/smc-definitive-guide-dailypriceaction.md` and
`docs/reference/smc-8step-entry-model-dailypriceaction.md`. Both are
Daily Price Action / Justin Bennett material, captured 2026-07-22, already
marked "external reference material — NOT an authoritative spec... any use
... must go through an RCR." The 8-step file's own cross-reference table
already identifies ST-C2 as "the platform candidate most structurally similar
to this liquidity->bias->OTE->FVG->LTF-CHoCH sequence" — confirming the
owner's funnel is a formalization of that same reference material, not
independent new source content.

A second collision was found during governance review: ST-C1's existing
scenario taxonomy in `specs/v3.9.yaml`/`specs/v3.10.yaml` already uses
`E1`/`E2`/`E3` for a different meaning (E1 = D1 gap reaction, E2 = POI, E3 =
liquidity sweep 5M) close enough to the owner's "E1 = FVG/OB 1D, E2 = POI 1H,
E3 = sweep 5M" to corrupt cross-candidate audit trails if reused unchanged.

## Decision

**Accept the owner's funnel as a new strategy candidate: `ST-C3`, version
`1.0.0`, status `draft`.** It does not supersede, mutate, or pause ST-C2. It
enters its own Stage A from scratch (no inherited A1/S1-G2 progress) per
`MASTER_PLAN.md` Governance Rule 6 ("new strategy branches require a new
candidate version and repeat Stage A").

### 1. Naming and label collisions — resolved

- **Rejection codes:** namespaced as `ST-C3-R1` .. `ST-C3-R7`, never bare
  `R1`-`R7`, to avoid collision with ST-C2's `specs/st-c2_v1.2.0.yaml` §6
  codes.
- **Funnel-stage cluster labels:** the owner's "E1/E2/E3 master guide"
  shorthand is renamed `F1`/`F2`/`F3` ("funnel stages") for ST-C3 — same
  ordering and meaning the owner described (F1 = 1D FVG/OB reaction, F2 = 1H
  POI reaction, F3 = 5M liquidity sweep) — to avoid collision with ST-C1's
  existing `E1`/`E2`/`E3` scenario-cluster taxonomy. If the owner intended
  the original `E1`-`E3` labels specifically, that requires an explicit
  correction; this ADR records `F1`-`F3` as the working default.
- **Evidence IDs** (`HTF_BIAS_ID`, `SWEEP_ID`, `BOS_ID`, etc.) carry no
  collision with existing ST-C1/ST-C2 identifiers and are adopted as
  proposed.

### 2. Source-document basis

`docs/reference/smc-definitive-guide-dailypriceaction.md` and
`docs/reference/smc-8step-entry-model-dailypriceaction.md` are the RCR
Evidence basis for ST-C3 (see the accompanying `reports/research_log.md`
entry). Both remain non-authoritative reference material; nothing in this
ADR promotes them to spec status — ST-C3's own draft spec is the only
artifact with rule authority, and only once frozen.

### 3. Required artifacts, in order (binding)

1. This ADR (accepted).
2. RCR intake entry in `reports/research_log.md` (six-question template,
   filed alongside this ADR).
3. Draft candidate spec `specs/st-c3_v1.0.0.yaml`, `status: draft`,
   `engine_implements_spec: false`, `implementation_authorization: null`.
   Numeric thresholds not explicitly supplied by the owner are marked
   `UNRESOLVED`, not invented.
4. Only after those three exist: ST-C3 may begin its own S1-G1 spec-audit
   process. No implementation code, kernel module, or engine work is
   authorized by this ADR.

### 4. Parallel-track confirmation

`NEXT_ACTION.md` continues to name S1-G2 closure on frozen ST-C2 v1.2.0
GBPUSD as the sole active *execution* milestone. This ADR authorizes
**documentation-only** ST-C3 intake work (ADR + RCR + draft spec) to proceed
in parallel, on the same precedent as ADR-0001's track separation: research
on one candidate never blocks or is blocked by governance/documentation work
on another, only implementation capacity is one-at-a-time per
`NEXT_ACTION.md`. `NEXT_ACTION.md` itself is not amended by this ADR — it
still points at ST-C2 S1-G2. A future `NEXT_ACTION.md` change to add ST-C3
S1-G1 work requires its own governance step, not an implicit consequence of
this ADR.

## Consequences

- (+) The owner's funnel proposal gets a real governance path instead of
  being silently implemented against a frozen spec or silently dropped.
- (+) Rejection-code and evidence-cluster collisions with ST-C1/ST-C2 are
  caught and resolved before any spec content is frozen, not after.
- (+) ST-C2's S1-G2 work continues completely unaffected.
- (-) ST-C3 restarts Stage A from zero — no A1/A2 credit carries over from
  ST-C2, even though the underlying SMC concepts overlap heavily. This is a
  deliberate cost of the "approved strategies are immutable" rule, not an
  oversight.
- (-) No numeric thresholds are frozen yet; `specs/st-c3_v1.0.0.yaml` is
  intentionally incomplete (`UNRESOLVED` fields) pending its own S1-G1 audit.

## Alternatives considered

- **Treat this as an ST-C2 v1.3.0 revision.** Rejected — ST-C2 v1.2.0 is
  frozen and immutable, and the ruleset differs enough (own rejection codes,
  own TP model, own evidence system) that calling it a "revision" would
  misrepresent it as an incremental tweak rather than a new design.
- **Implement directly from the owner's prompt without RCR/ADR.** Rejected —
  this is exactly the "silent override" CLAUDE.md's conflict-handling rule
  prohibits, and defeats `docs/RESEARCH-CHARTER.md`'s commit-before-look
  discipline.
- **Reuse the owner's literal `R1`-`R7` and `E1`-`E3` labels.** Rejected —
  verified direct collision with ST-C2's and ST-C1's existing, differently
  defined codes/labels; would corrupt audit trails across candidates.

## Notes

This ADR does not authorize any engine, kernel module, backtest run, or
execution-layer work for ST-C3. It authorizes exactly three documentation
artifacts (this ADR, the RCR entry, the draft spec) and nothing beyond them.
Any future step (S1-G1 spec freeze, reference implementation, etc.) follows
the same Stage A gate sequence ST-C1 and ST-C2 already went through, under
its own `NEXT_ACTION.md` milestone when authorized.
