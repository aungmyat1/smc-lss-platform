---
name: session-filter
description: >-
  Filter trades by session/killzone. Trigger on 'session', 'killzone',
  'London/NY/Asian', 'time filter'.
---

# session-filter

## Purpose
Allow trades only inside configured sessions/killzones and block low-liquidity windows.

## Inputs
- current UTC time (bash date)
- session config (Asian/London/NY windows, killzones)

## Outputs
- active session, in-killzone (bool), trade-allowed (bool)

## Workflow
1. Read current UTC.
2. Map to session windows.
3. Flag London (07-10 UTC) and NY (12-15 UTC) killzones.
4. trade-allowed = inside an enabled killzone.

## Decision rules
- Outside killzone -> block by default.
- Avoid the London/NY overlap only if config says so.

## Validation checklist
- [ ] time source is live UTC
- [ ] windows applied from config, not hardcoded ad hoc

## Failure handling
- Weekend/market-closed -> trade-allowed = false.
- Config missing -> use documented defaults and warn.

## Examples
18:37 UTC = NY afternoon, outside killzone => trade-allowed = false.

## Acceptance criteria
- [ ] Returns active session + allowed flag
- [ ] deterministic from the clock

## Coded logic (this platform)
`smc_master.session_of(timestamp)` -> active session + killzone flag
(London 07-10 UTC, NY 12-15 UTC). Used as stage 1 of the master pipeline.

