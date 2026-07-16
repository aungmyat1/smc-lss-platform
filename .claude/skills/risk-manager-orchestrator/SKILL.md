---
name: risk-manager-orchestrator
description: >-
  Sizing+limits wrapper delegating math to the atomic risk-management skill.
  Trigger on 'size this trade', 'can I take this'.
---

# risk-manager-orchestrator

## Purpose
Thin orchestrator that calls risk-management for sizing and execution/mt5-trading for the two-step order flow.

## Inputs
- validated setup
- account + symbol specs

## Outputs
- APPROVED/REFUSED + order params

## Workflow
1. Call risk-management.
2. If APPROVED, call execution guardrails.
3. On confirm, mt5-trading places+modifies.

## Decision rules
- Delegates limits to risk-management; never overrides a REFUSE.

## Validation checklist
- [ ] no duplicate limit logic
- [ ] execution stays human-confirmed

## Failure handling
- Any REFUSE -> stop.

## Examples
Approved -> execution GO -> await confirm.

## Acceptance criteria
- [ ] Single source of truth for sizing (risk-management)
