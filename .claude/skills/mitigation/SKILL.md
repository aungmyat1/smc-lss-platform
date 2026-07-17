---
name: mitigation
description: >-
  Track mitigation of POIs. Trigger on 'mitigation', 'mitigation block', 'retest
  origin'.
---

# mitigation

## Purpose
Detect when price returns to mitigate an OB/FVG origin, distinguishing fresh vs mitigated zones.

## Inputs
- POI zones (OB/FVG) with origin time
- subsequent candles

## Outputs
- per-POI mitigation status: FRESH | MITIGATED | INVALIDATED

## Workflow
1. For each POI, watch for price re-entering the zone.
2. First tap = mitigation event.
3. Body close through the zone = invalidation.

## Decision rules
- Trade fresh POIs preferentially.
- Invalidated zone must not be used.

## Validation checklist
- [ ] status transitions are close-based
- [ ] invalidation vs mitigation separated

## Failure handling
- Zone never revisited -> remains FRESH.
- Deep close-through -> INVALIDATED.

## Examples
Bullish OB 1.1420-1.1432 tapped to 1.1428 and rejected => MITIGATED, still valid.

## Acceptance criteria
- [ ] Each POI carries a current status
- [ ] invalidation removes it from candidates

## Coded detector (this platform)
`smc_engine.mitigation_status(candles, from_i, low, high, direction)` ->
FRESH / MITIGATED / INVALIDATED for a POI zone, close-based and deterministic.

