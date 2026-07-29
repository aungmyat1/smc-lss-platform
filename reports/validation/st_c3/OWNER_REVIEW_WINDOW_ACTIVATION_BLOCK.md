# ST-C3 Owner Review Window Activation Block

**Status:** TEMPLATE ONLY - not active
**Purpose:** Activate the consolidated 48-hour owner review window after the
approved dataset replay and evidence packet are complete.

## Preconditions

- `DATA_APPROVAL_ST_C3.md` records owner dataset approval.
- `governance/st_c3_stage_status.yaml` has `data.approved = true`.
- `reports/validation/st_c3/replay/ledger.json` exists.
- `reports/validation/st_c3/replay/ledger.hash` verifies.
- Stats, robustness, and walk-forward outputs reference the same ledger hash.
- `OWNER_DECISION_PACKET_ST_C3_A2.md` and `.json` exist.
- S1-G5 and S1-G6 evidence files are linked in the packet.

## NEXT_ACTION.md Block

```markdown
NEXT: Owner review of consolidated S1-G5 + S1-G6 packet (48-hour window).

Review packet:
`reports/validation/st_c3/replay/OWNER_DECISION_PACKET_ST_C3_A2.md`

This review does not open A3, authorize execution, or imply acceptance.
Owner must return separate outcomes for S1-G5 and S1-G6: accept, reject,
or defer.
```

## YAML Status Block

```yaml
s1_g5:
  status: pending_review
s1_g6:
  status: pending_review
review_window:
  status: active
  duration_hours: 48
  packet: reports/validation/st_c3/replay/OWNER_DECISION_PACKET_ST_C3_A2.md
  guardrail: >
    Pending review only. Does not accept S1-G5 or S1-G6, pass A2, open A3,
    or authorize execution.
```

