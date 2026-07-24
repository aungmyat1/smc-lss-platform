# ST-C2 HTF Structure and Bias Report

**Date:** 2026-07-24  
**Gate Slice:** S1-G2-GC2  
**Authority:** `specs/st-c2_v1.2.0.yaml`

## Verdict

HTF STRUCTURE AND BIAS: PASS

## Evidence

- HTF swings are detected through the frozen H4 fractal setting.
- BOS/CHoCH events require closed-candle breaks beyond confirmed structure.
- Active bias is classified only from HTF BOS/CHoCH events.
- Liquidity sweeps, FVGs, OTE, displacement outside CHoCH qualification, and LTF confirmation cannot create or flip HTF bias.
- CHoCH flip attempts require the frozen body-ratio threshold and emit rejection evidence when below threshold.
- Bias evidence records event ID, timestamp, evidence type, protected-level ID, causal cutoff, and reason.

## Tests

- `tests/st_c2/test_structural_conformance.py::test_htf_bias_uses_closed_candle_bos_choch_not_wick_only`
- `tests/st_c2/test_structural_conformance.py::test_choch_flip_requires_displacement_threshold`
- `tests/st_c2/test_structural_conformance.py::test_structural_context_is_causal_and_deterministic`

## Remaining Limits

Multi-CHoCH advanced sequencing remains partial and is not sufficient to close full S1-G2.
