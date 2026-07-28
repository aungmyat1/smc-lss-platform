# S1-G7 Evidence-Gathering Plan - ST-C3

**Stage:** A  
**Gate:** S1-G7  
**Status:** Draft  
**Spec Basis:** v1.0.7 (authoritative), v1.0.8 (draft analytical extension)  
**Purpose:**  
Define the deterministic procedure for collecting evidence required to
evaluate S1-G7 (Signal-to-Execution Alignment), without modifying kernel,
evidence engine, or execution behavior.

---

## 1 - Inputs Required

### 1.1 Validated Signal Evidence

Collect the full evidence object produced by S1-G5/S1-G6:

- Sweep
- CHoCH
- MSS
- OB/FVG/Liquidity validation
- POI arrival
- Bias inference
- Trade-plan conformance
- Rejection codes
- Evidence bundle

### 1.2 SOP-A Analytical Context

Extract the analytical-only fields defined in the v1.0.8 draft:

- HTF bias
- HTF POI
- Draw-on-liquidity
- Qualification gates
- Setup validation extensions
- Confirmation filters
- Analytical OTE zone
- SOP-A summary block

### 1.3 Execution-Agent Requirements

The execution agent remains Stage-B and frozen, but its analytical
expectations are allowed for documentation:

- Required bias alignment
- Required POI type
- Required liquidity direction
- Required confirmation sequence
- Required environmental constraints

These expectations are documentation-only.

---

## 2 - Evidence-Gathering Workflow

### Step 1 - Collect Validated Signal Bundle

Gather the full evidence object produced by S1-G5/S1-G6:

- `signal_context`
- `trade_plan_context`
- `confirmation_structure`
- `environmental_context`
- `evidence_summary`

This is the baseline for alignment.

### Step 2 - Collect SOP-A Analytical Context

Extract the analytical-only fields defined in the v1.0.8 draft:

- HTF context
- Qualification gates
- Setup validation
- Confirmation filters
- Analytical OTE
- SOP-A summary

This forms the analytical extension layer.

### Step 3 - Collect Execution-Agent Analytical Requirements

Execution agent remains Stage-B and frozen, but its analytical
expectations are allowed:

- Required bias
- Required POI type
- Required liquidity direction
- Required confirmation sequence
- Required environmental constraints

These expectations are documentation-only.

### Step 4 - Build Alignment Matrix Inputs

Populate the alignment matrix with:

- Signal evidence
- SOP-A analytical evidence
- Execution-agent analytical requirements

No execution logic is invoked.

### Step 5 - Identify Alignment Points

For each component:

- Bias
- POI
- Liquidity
- OB/FVG
- Sweep/CHoCH/MSS
- OTE (analytical)
- Session/news/spread/daily-risk

Record:

- aligned
- partially aligned
- misaligned
- notes

### Step 6 - Produce Analytical Verdict

Generate:

```text
s1_g7_verdict:
  sop_a_alignment_pass: true | false
  reason: string
  confidence_score: float
  execution_binding: false
  lifecycle_binding: false
```

This verdict is non-binding and non-executable.

---

## 3 - Evidence Outputs

### 3.1 Alignment Matrix

A structured table comparing:

- Signal evidence
- SOP-A analytical evidence
- Execution-agent analytical requirements
- Alignment result
- Notes

### 3.2 Alignment Summary

```text
alignment_summary:
  aligned: true | false
  partial_alignment: true | false
  misalignment_points:
    - string
    - string
  notes: string
```

### 3.3 S1-G7 Analytical Verdict

Non-executable, non-lifecycle.

---

## 4 - Governance Constraints

- No kernel changes
- No evidence engine changes
- No execution logic
- No lifecycle logic
- No Stage-B activation
- S7/S8/S9 freeze upheld
- v1.0.8 treated as draft only
- SOP-A treated as analytical only
- Evidence-gathering is documentation-only

---

## 5 - Completion Criteria

S1-G7 evidence-gathering is complete when:

1. All validated signal evidence is collected
2. All SOP-A analytical evidence is collected
3. Execution-agent analytical expectations are documented
4. Alignment matrix is fully populated
5. Alignment summary is produced
6. Analytical verdict is produced
7. No execution or lifecycle logic was introduced

---

## Next Step Options

- Begin S1-G7 evidence gathering
- Ratify v1.0.8
- Draft S1-G7 audit template

