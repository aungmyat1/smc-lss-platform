# ST-C1 v3.10 — Why E1 (D1 Gap-Reversal) Never Fires

Date: 2026-07-22
Status: Diagnosis only — **no code change made.** Ruled by
`project-governance-agent` as a design-change question, not a bug fix;
any change to the selection logic described below requires a six-question
RCR per `docs/RESEARCH-CHARTER.md` before it is backtested. This closes
the "diagnose why v3.10 never executes an E1 trade" item from
`NEXT_ACTION.md`.

## One-sentence verdict

E1 is not merely rare — it is **structurally locked out of ever being
selected** by `detect_e_trigger`'s tie-break rule, which was written for a
two-trigger (E2/E3) world and carried unchanged into v3.10's three-trigger
design without anyone deciding what should happen when E1 also qualifies.

## Method

Read-only instrumented scan (all three symbols, full local history, no
repo files touched): called `signal_v310._e1_trigger_reversal`,
`_e2_trigger_reversal`, and `_e3_trigger_reversal` individually at every
unique H1-bar evaluation point the replay engine actually checks (~6,640
points per symbol, matching the engine's own caching granularity), plus
`detect_e_trigger`'s actual combined selection. Initially run on EURUSD
only; extended to GBPUSD and XAUUSD per `project-governance-agent`'s
requirement that the evidence cover all three symbols before any RCR
relying on it is considered complete.

## Result — consistent across all three symbols

| Symbol | Checkpoints | E1 qualifies | E2 qualifies | E3 qualifies | E1 wins tie-break |
|---|---|---|---|---|---|
| EURUSD | 6,639 | 86 (1.30%) | 1,747 (26.31%) | 2,929 (44.12%) | 0/86 |
| GBPUSD | 6,640 | 138 (2.08%) | 1,731 (26.07%) | 2,890 (43.52%) | 0/138 |
| XAUUSD | 6,643 | 147 (2.21%) | 1,427 (21.48%) | 2,570 (38.69%) | 0/147 |
| **Total** | **19,922** | **371 (1.86%)** | **4,905 (24.62%)** | **8,389 (42.10%)** | **0/371 (0%)** |

**E1 loses `detect_e_trigger`'s selection to E2 or E3 100% of the time it
qualifies, in every symbol, with zero exceptions across 371 qualifying
checkpoints.** This is not symbol-specific or a EURUSD artifact — the same
mechanism holds identically everywhere the strategy trades.

Overall selection distribution across all checkpoints where anything
qualified, combined across symbols: E3 5,564, E2 2,828, **E1 0.**

## Root cause

`detect_e_trigger` (`src/signal_v310.py:418-428`):

```python
candidates = [t for t in (
    _e1_trigger_reversal(h1, d1, h4),
    _e2_trigger_reversal(h1, h4),
    _e3_trigger_reversal(h1, h4),
) if t is not None]
if not candidates:
    return None
return max(candidates, key=lambda t: t["confirm_i"])
```

Whichever qualifying trigger has the most recent confirmation bar
(`confirm_i`) wins. E1's confirmation is anchored to a reaction within a
bounded window (`E1_REACTION_WINDOW_H1_BARS=12`) after a D1 gap that can be
up to `E1_GAP_MAX_AGE_D1_BARS=20` bars old — structurally older than a live
E2/E3 continuation setup, which re-confirms off the most current price
action every time it's checked. Whenever E1 and E2/E3 both qualify at the
same checkpoint, E2/E3's `confirm_i` is almost always more recent, so E1
loses by construction, not by chance.

`src/signal_v39.py`'s `detect_e_trigger` docstring makes the rule's origin
explicit: *"E1 is disabled outright... only E2/E3 compete; freshest
wins."* This was a reasonable rule for a genuinely symmetric two-trigger
contest. v3.10 re-enabled E1 and carried the identical rule into a
three-trigger context without revisiting whether "freshest wins" still
made sense once one candidate is structurally staler by design. Neither
`src/signal_v310.py`'s `detect_e_trigger` docstring nor
`reports/audit/ST_C1_V310_REVERSAL_CAPTURE_RCR.md`'s Hypothesis or Success
Criteria sections address what should happen when E1 and E2/E3 qualify
concurrently — the RCR is silent on this exact question.

## Why this is ruled a design change, not a bug (per governance)

Per `docs/RESEARCH-CHARTER.md`'s own test (would a second engineer call
this a bug or a design change?): there is no already-agreed rule this
implementation contradicts. "Prefer E1 when it qualifies," "keep recency
regardless," and other tie-break shapes are all undecided design options —
choosing one now would be authoring new detection logic, not correcting an
implementation error against an existing agreement. This differs from the
`index_offset` dedup fix (which changed only which already-selected trades
got silently discarded by a bookkeeping key, not which signal was
selected) and the doji-candle fix in the RCR addendum (which corrected an
implementation against an explicitly intended, already-agreed behavior).
Changing the E1/E2/E3 selection rule changes which signal is chosen as the
trade in the first place — first-order detection-logic behavior.

## A related caveat on the existence check

`ST_C1_V310_REVERSAL_CAPTURE_RCR.md`'s existence-check success criterion
(">=1 qualifying signal per symbol") was reported cleared (367 trades
total, all three symbols). **That check did not validate the
reversal-capture-via-E1 thesis specifically** — none of those 367 trades
were E1-triggered (confirmed: `ST_C1_V39_VS_V310_COMPARISON.md`'s variant
breakdown shows zero E1* trades across all three symbols). The existence
check only confirmed the engine produces *some* signal under the new
H4-divergence gate, via E2/E3 — the same trigger families v3.9 already
uses. The reversal-capture mechanism v3.10 was purpose-built to test has
not actually fired once.

## What this does not establish

- No claim about whether E1 *should* win when it qualifies, or what the
  "correct" tie-break is — that's exactly the undecided design question
  flagged above.
- No code, spec, or parameter change made. `detect_e_trigger`'s selection
  logic is unchanged.
- Not a verdict on v3.10's overall viability beyond what
  `ST_C1_DEDUP_BUG_AND_CORRECTED_RESULTS.md` and
  `ST_C1_V39_VS_V310_COMPARISON.md` already established (net-losing in all
  three symbols).

## Recommended next step

Per `project-governance-agent`'s ruling on this diagnosis: since both
candidates already miss `ROADMAP.md`'s promotion bar by roughly an order
of magnitude in every symbol (v3.9 aggregate PF 0.138, v3.10 aggregate PF
0.469, versus a PF >= 1.3 bar), this RCR cannot be framed as fixing
v3.10's profitability — E1's ~1.9% combined solo-qualification rate bounds
any realistic population shift far too small to move the aggregate PF
meaningfully. It is worth doing only as a narrow, honestly-scoped
diagnostic: generating the first-ever E1-triggered trade population so the
reversal-capture thesis can be evaluated on its own terms at all, since it
has never once been observed. See
`reports/research_log.md`'s corresponding entry for the filed RCR.
