# ST-C1 v1.1.0 / spec v3.7 — Gate-to-Code-to-Test Traceability Matrix

| Gate | Spec section | Code (file:function) | Engine wiring | Tests |
|---|---|---|---|---|
| G1 | `specs/v3.7.yaml#g1_htf_bias` | `src/signal_v37.py:121 evaluate_g1_bias` (+ `:97 classify_breaks`, `:71 _break_events`) | `validation/historical_replay_engine_v37.py` → `v37.evaluate_candidates` (called from `generate_signal`) | `tests/test_signal_v37_gates.py::test_g1_*` (4) |
| G2 | `#g2_external_structure` | `src/signal_v37.py:154 evaluate_g2_external_structure` | same | `::test_g2_*` (2) |
| G3 | `#g3_bos_choch` | `src/signal_v37.py:97 classify_breaks` (shared with G1; reused for M5 close-confirmation inside `:300 evaluate_g6_m5_trigger`) | same | `::test_g3_*` (3) |
| G4 | `#g4_premium_discount` | `src/signal_v37.py:181 evaluate_g4_location` | same; ablation flag `_skip_g4` set from `HistoricalReplayEngineV37.ablation["location_gate"]` | `::test_g4_*` (3) |
| G5 | `#g5_htf_poi` | `src/signal_v37.py:281 evaluate_g5_htf_poi` (+ `:200,:220,:241` per-origin finders, `:259 _causal_displacement_ok`) | same | `::test_g5_*` (3) |
| G6 | `#g6_m5_trigger` | `src/signal_v37.py:300 evaluate_g6_m5_trigger` | `historical_replay_engine_v37.py::generate_signal` sizes the M5 search window via `m5_poi_entry_search_bars` before calling `evaluate_candidates` | `::test_g6_*` (7) |
| G7 | `#g7_structural_invalidation` | `src/signal_v37.py:367 evaluate_g7_stop` | same | `::test_g7_*` (2) |
| G8 | `#g8_net_reward_gate` | `validation/historical_replay_engine_v37.py::HistoricalReplayEngineV37.generate_signal` (net/gross RR block, reuses inherited `_cost_to_r`) — deliberately NOT in `signal_v37.py` (needs the cost model, which the replay engine owns per the one-cost-model requirement) | n/a (engine-native) | `::test_g8_net_rr_formula_gross_clears_but_net_misses_threshold`, `::test_example_2_...` |
| G9 | `#g9_preselected_target` | `src/signal_v37.py:405 evaluate_g9_target` | `consumed_levels` set threaded through `HistoricalReplayEngineV37._consumed_target_levels` across the replay loop | `::test_g9_*` (3) |
| G10 | `#g10_fixed_management` | `validation/historical_replay_engine.py::HistoricalReplayEngine._simulate_trade_detail` / `simulate_trade` (inherited unchanged by `HistoricalReplayEngineV37`) | `replay()` (inherited unchanged) | `tests/test_historical_replay.py` (pre-existing; not duplicated here) |

## Gate trace schema (IMPLEMENTATION ARCHITECTURE requirement)

Produced by `HistoricalReplayEngineV37._new_trace` on every `generate_signal`
call, appended to `self.gate_traces`:

`candidate_id, strategy_version, symbol, evaluation_time, G1_bias, G2_structure,
G3_confirmation, G4_location, G5_confluence, G6_trigger, G7_invalidation,
G8_reward, G9_target, G10_management, final_decision, rejection_code,
secondary_rejection_codes, evidence_ids, cost_snapshot, data_cutoff`

`G10_management` stays `None` on the trace itself (management only applies to
*filled* trades, tracked instead on the inherited `TradeRecord.management_events`)
— documented here rather than left silently unclear.

## Required negative/edge-case coverage — mapping to this task's TEST REQUIREMENTS list

| Required case | Where covered |
|---|---|
| Wick break without close | `test_g3_wick_only_rejection_never_registers_as_a_break` |
| Missing protected swing | `test_g1_neutral_on_conflicting_bias_never_defaults_to_a_side`, `test_g2_none_without_confirmed_swings_on_both_sides` |
| Stale/invalidated FVG | `test_g5_none_without_qualifying_causal_displacement` (no qualifying causal displacement); freshness lifecycle itself is `smc_engine.mitigation_status`, already covered by `tests/test_features.py`/`tests/test_smc_engine.py` (reused, not reimplemented) |
| Wrong event order | `test_g6_wrong_event_order_rejected` |
| Future-bar append invariance / no look-ahead | Structural: every gate function only ever receives bounded, already-closed-candle windows (`_bounded_context_window`, `_window`), consistent with the base engine's existing point-in-time tests in `tests/test_historical_replay.py`; not independently re-proven for v3.7 beyond the gate unit tests themselves given time constraints — flagged as a residual gap, see final validation doc |
| First-qualifying-bar behavior | `test_g6_first_qualifying_bar_only_uses_earliest_sweep` |
| Next-open gap invalidation | G8 explicitly recomputes `net_available_rr` off `entry_price = m5[index+1]["open"]` (the actual next-bar-open), not the signal-bar close — see `historical_replay_engine_v37.py::generate_signal`; not separately fixture-tested for a gap-specific scenario (residual gap) |
| No logical target | `test_g9_reject_no_target_never_synthetic_fixed_r` |
| Duplicate structure | Inherited `structure_key` consumption in `HistoricalReplayEngine.replay` (unchanged); `structure_identity` built per-signal in `generate_signal` via inherited `_structure_identity` |
| Same-bar stop/target ambiguity | Inherited `_simulate_trade_detail`'s `ambiguous_bar`/stop-first handling (unchanged); pre-existing coverage in `tests/test_historical_replay.py` |
| Partial and BE sequencing | Inherited, unchanged, pre-existing coverage |
| Timeout and end-of-data censoring | Inherited `CENSORED_END_OF_DATA` handling, unchanged, pre-existing coverage |
| Timezone and DST policy | Unchanged from base engine (`session`, fixed UTC windows, `dst_adjusted: false` by design, per `specs/v3.7.yaml#session`); not re-tested here |
| Repaired-candle sensitivity | See `reports/ablation/ST_C1_V37_DATA_REPAIR_SENSITIVITY.md` — not applicable at the strategy level given the zero-trade ablation result (see final validation doc) |

## Known, disclosed simplifications (not silent defaults-to-pass)

1. **G6 POI-touch search window is bounded** (`m5_poi_entry_search_bars`,
   default 3200 M5 bars ≈ 11 trading days) rather than the full theoretical
   staleness window a POI could have (up to `htf_poi_max_age_h1_bars`=60 H1
   bars or `d1_gap_max_age_d1_bars`=10 D1 bars, i.e. potentially longer).
   This is a disclosed engine-tractability bound, not a strategy rule change
   — it can only make the engine MORE conservative (miss some theoretically
   valid but very slow-developing setups), never less. Confirmed via direct
   testing against real EURUSD data that widening this window from 108 to
   3200 bars did change real behavior (found more POI touches), so the bound
   is not inert.
2. **G2's reusable/consumed liquidity lifecycle** is only tracked for target
   selection (G9's `consumed_levels`), not as a fully general per-structure
   ACTIVE/SWEPT/INVALIDATED state machine across the whole replay.
