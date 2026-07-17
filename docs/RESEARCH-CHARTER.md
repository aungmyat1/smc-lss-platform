# SMC-LSS Research Charter

**Status:** governance template, effective 2026-07-18.
**Relationship to other docs:** `docs/CHARTER.md` governs *operational* safety
(when the system is allowed to trade, what gates it). This document governs
*research* discipline (when a rule/spec/parameter change is allowed to be
made, and how it must be justified). `reports/quant_research_audit.md` §1
flagged the absence of a pre-registered change process as a driver of
threshold-shopping risk — this is that process.

## The rule

**No change to `specs/*.yaml`, `src/signal_v35.py` detection logic, or any
`[TUNABLE]` constant may be made without first answering the six questions
below, in writing, before looking at the result.** Answering them after
seeing whether the change "worked" defeats the purpose — the whole point is
to commit to a falsifiable expectation first.

This applies to intentional research changes. It does not apply to pure bug
fixes (e.g. this session's no-DOL-target rejection fix, the `_e3_trigger`
one-sided-swing bug) where the "before" behavior was never intended and the
"after" behavior is just correcting an implementation error against an
already-agreed spec — those go through normal code review, not this
process. If a "bug fix" also changes strategy behavior in a way that isn't
obviously just correcting an error (judgment call: would a second engineer
independently describe it as a bug, or as a design change?), treat it as a
research change and use this template.

## Required fields (fill in BEFORE running the backtest)

```markdown
## Change: <short name>  (spec version: vX.Y -> vX.Z)
Date:
Author:

### Why
What prompted this change? (a specific backtest finding, a spec ambiguity,
an owner request — not "seemed worth trying")

### Evidence
What existing data/finding motivates the hypothesis that this will help?
Cite the specific report/number (e.g. "reports/backtest_v35_XAUUSD.json:
816 trades, 22.8% win rate — hypothesis: POI max-age too permissive").

### Hypothesis
State the mechanism, not just the expected direction. "Tightening
e2_poi_max_age_h1_bars from 60 to 30 will reduce trade count and raise win
rate by excluding stale POIs whose original cause is no longer relevant" —
not "this should help."

### Expected improvement
A number, before running anything. "Expectancy improves from -0.166R to
better than -0.05R" or "trade count drops from 816 toward 100-300 while
win rate rises above 30%." Vague directional claims ("should be better")
are not acceptable here — if you can't state a number, the hypothesis
isn't sharp enough yet.

### Success criteria
The OOS-backed bar that must be cleared to keep the change (tie to
`backtest-researcher`'s ACCEPT/REJECT gate — e.g. "OOS expectancy > 0 AND
OOS >= 0.5 * IS expectancy, per validation skill's existing rule").

### Rollback criteria
What result reverts this change automatically, no further discussion?
("OOS expectancy negative" or "trade count drops below 30 -- INCONCLUSIVE,
revert and try a smaller step".)
```

## Where these live

Append each filled template to `reports/research_log.md` (create on first
use) in date order — never overwrite a prior entry, even a rejected one.
Rejected changes are evidence too; a log with only accepted changes hides
how much was tried, which is exactly the multiple-testing risk deflated
Sharpe (`reports/quant_research_audit.md` §13) exists to correct for. The
log's entry count IS the trial count `optimization`/deflated-Sharpe should
use as an input once that infrastructure exists.

## Relationship to `backtest-researcher`

This charter is the precondition; `backtest-researcher`'s existing workflow
(freeze spec version -> backtest -> optimize if params changed -> validation
gate) is the execution. Concretely: fill in the six fields above, freeze the
spec version, THEN invoke `backtest-researcher`. Its ACCEPT verdict becomes
this entry's resolution; a REJECT verdict is recorded in the same log entry,
not discarded.

## What this prevents

Not creativity — hypothesis generation is still free-form. What it prevents
is the silent kind of overfitting where five parameter nudges get tried,
four are quietly discarded because they "didn't look right," and the fifth
gets reported as *the* result — with no record that it was 1-of-5, and no
account taken of that when judging whether +0.2R OOS is signal or noise.
