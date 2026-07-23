# Agent Alignment Contract

Both agents (Governance and Engineering) must read this file.

## Project Goal

Create a professional MT5 Demo Auto Trading Platform.

Priority: **Reliability > Complexity**

---

## Current State

- Execution: **v1 strategy** (`specs/v1.yaml`, sole execution authority per ADR-0001)
- Research: **v3.6 → ST-C1 (v3.7–v3.10, parked) → ST-C2 (active candidate)**

Promotion requires validation. See
`docs/adr/ADR-0001-two-track-strategy-lifecycle.md` for the two-track
execution/research lifecycle.

---

## Non-Negotiable Rules

1. No silent architecture changes
2. No fabricated decisions
3. No undocumented authority changes
4. No live trading
5. Tests required before completion
6. Git history defines official changes

---

## Communication Model

- **Governance Agent:** decides WHAT and WHY.
- **Engineering Agent:** implements HOW.

Neither agent overrides the other.
