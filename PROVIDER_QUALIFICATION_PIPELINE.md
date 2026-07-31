# ST-C3 Provider Qualification Pipeline

Status: **ACTIVE / EVIDENCE COLLECTION**

Date: 2026-07-31

Recommendation: `CONTINUE_EVIDENCE_COLLECTION`

## Purpose

This document separates provider qualification from canonical dataset
construction. It is an execution-control artifact only; it does not change
ST-C3 strategy logic, replay logic, validators, dataset approval rules, or the
Dataset Contract.

## Pipeline A - Provider Qualification

Status: **ACTIVE**

Allowed work:

- Acquire the deterministic 100-day source-integrity evidence sample.
- Profile sequential acquisition and report measured bottlenecks.
- Use bounded parallelism only for download/cache operations.
- Run session-calendar qualification.
- Run cross-provider anomaly verification.
- Produce statistical source-integrity evidence.
- Produce provider scorecard evidence after the registered sample is complete.

Disallowed work:

- Build or approve the canonical dataset.
- Fill, fabricate, interpolate, or manually edit market data.
- Modify approval gates, replay gates, validation rules, or strategy logic.

Current evidence state:

- Deterministic sample cached complete: `30/100`
- Latest sequential baseline: `25.863669907174828` source hours/minute
- Latest bounded 2-worker download/cache batch:
  `49.87625709274107` source hours/minute with deterministic task order
  preserved
- Latest measured top bottlenecks: download/cache, then `.bi5`
  decompression/parse
- Prior bounded 4-worker download/cache batch: `108.79208711087463` source
  hours/minute, zero duplicate tasks, zero failed tasks

## Pipeline B - Canonical Dataset Construction

Status: **DISABLED**

This pipeline remains disabled until Provider Qualification produces one of the
existing governance outcomes:

- `ACCEPT_DUKASCOPY`
- `OPEN_DATA_GOVERNANCE_REVIEW`
- `REJECT_DUKASCOPY`

Only after provider acceptance may the project resume full canonical
construction:

- tick acquisition
- deterministic M1 reconstruction
- H4/M15/M3 aggregation
- manifest generation
- strict integrity validation
- dataset contract validation
- owner approval

## Execution Order

1. Sprint A: performance baseline.
2. Sprint B: bounded parallel acquisition for download/cache only.
3. Sprint C: parallel evidence processing only after download parallelism is
   proven deterministic.
4. Sprint D: keep provider qualification and canonical construction separate.
5. Sprint E: complete the registered 100-day sample plus separate anomaly
   queue evidence.
6. Sprint F: score the provider using fixed criteria and existing governance
   outcomes only.

## Guardrail

Replay remains `BLOCKED`, A3 remains `CLOSED`, and demo/live remain `BLOCKED`
until dataset approval and replay acceptance are achieved through the existing
governance path.
