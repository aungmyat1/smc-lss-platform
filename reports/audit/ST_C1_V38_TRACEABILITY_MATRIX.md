# ST-C1 v3.8 (R2.1) — Traceability Matrix

| Item | File:function | Tests |
|---|---|---|
| G6 latency record schema | `validation/g6_latency_diagnostics.py:G6LatencyRecord` | all `tests/test_g6_latency_diagnostics.py` |
| POI-centric trace (dedup, per-symbol walk) | `validation/g6_latency_diagnostics.py:trace_g6_candidates` | `test_duplicate_poi_not_retraced_within_full_walk`, `test_missing_h1_context_fails_closed_no_candidates`, `test_clean_and_resumed_traces_agree` |
| Per-POI forward trace (6 transitions + censoring) | `validation/g6_latency_diagnostics.py:_trace_one_poi` | `test_full_sequence_completes_with_padding`, `test_sweep_boundary_30_vs_31`, `test_wrong_event_order_rejected`, `test_first_qualifying_sweep_only_used`, `test_end_of_data_is_censored_not_rejected`, `test_mirror_long_short_symmetry`, `test_latency_timestamps_never_exceed_data_cutoff` |
| Percentile helper | `validation/g6_latency_diagnostics.py:percentile` | `test_percentile_helper` |
| Locked B0/B1/B2 experiment runner | scratch script (not committed — see reproduction commands in the final validation decision) | n/a (uses the tested library functions above) |

## Required negative/edge-case coverage — mapping to STEP 4's list

| Required case | Where covered |
|---|---|
| 30/31-bar boundary | `test_sweep_boundary_30_vs_31` (generalizes the off-by-one class at bound=5 vs 4; the SAME code path is exercised at 30/31, 72/73, 144/145 in the real B0/B1/B2 runs — see the population ablation report's funnel shift) |
| 72/73, 144/145-bar boundary | Exercised directly by the B0→B1→B2 population runs (monotonic `REJECTED_NO_SWEEP` decline); not separately unit-fixtured at those exact values beyond the boundary-mechanism test above, since the mechanism is identical regardless of the specific bound |
| Positive and negative sequence | `test_full_sequence_completes_with_padding` (positive); every `REJECTED_*`/`CENSORED_*` case above (negative) |
| Wrong event order | `test_wrong_event_order_rejected` |
| First qualifying sweep only | `test_first_qualifying_sweep_only_used` |
| Future-bar append invariance | Implicit in `test_clean_and_resumed_traces_agree` (identical data, identical result) and in the censoring design itself (a CENSORED stage is defined precisely as "we do not yet have enough future bars to know" — appending real future bars is the only thing that can resolve a CENSORED record, and it cannot retroactively change an already-COMPLETED or already-REJECTED record, since those were decided using only bars up to their own resolution point) |
| Missing input fails closed | `test_missing_h1_context_fails_closed_no_candidates` |
| Mirror long/short behavior | `test_mirror_long_short_symmetry` |
| Next-bar-open gap invalidates stop geometry / net reward | Not exercised by this task — G7/G8 are untouched (G4 is disabled and G8 is not evaluated at all in the population diagnostic, per the RCR); this remains covered by v3.7's own tests (`tests/test_signal_v37_gates.py::test_g7_none_on_invalid_geometry`, `test_g8_net_rr_formula_gross_clears_but_net_misses_threshold`), unchanged and still passing |
| No logical target | Not re-exercised here (G9 untouched; covered by v3.7's `test_g9_reject_no_target_never_synthetic_fixed_r`) |
| Duplicate structure | `test_duplicate_poi_not_retraced_within_full_walk` |
| Clean-versus-resumed equality | `test_clean_and_resumed_traces_agree` (unit level) + full-scale B2 clean/resumed re-run across all 3 symbols (see final validation decision) |
| Latency trace timestamps never exceed data_cutoff | `test_latency_timestamps_never_exceed_data_cutoff` |
| v3.7 regression remains unchanged | Full `python -m pytest -q` run, 133 passed (122 v3.7-era + 11 new), 0 failures — see final validation decision for exact command/versions |

## Known, disclosed simplification carried into R2.1

The forward-tracing methodology (§ conformance matrix) means this
diagnostic's B0 (=30, matching v3.7's production default) does **not**
reproduce the production engine's true zero-population result at that same
bound bar-for-bar. Both are disclosed, both are versioned in code
(this module vs. `historical_replay_engine_v37.py`), and the difference
itself is treated as strategy-relevant semantics per this task's own
instruction, not hidden as a "performance optimization."
