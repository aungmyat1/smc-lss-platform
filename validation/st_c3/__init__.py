"""ST-C3 reference funnel package (A2/S1-G2 scoped research/validation only).

Research-only Stage A code. Implements the deterministic evidence-driven
validator kernel described in `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md`
and `docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md` against
`specs/st-c3_v1.0.1.yaml`. Must not import broker/MT5 paths and does not
authorize execution, demo, live, or production trading.

Scope note: several ST-C3 numeric detection thresholds (sweep wick ratio,
displacement body-ratio, freshness definition, entry-window bar count, etc.)
are still `UNRESOLVED`/`PROVISIONAL` in the frozen spec. Building real
price-bar SMC detection modules for those stages would require inventing
numbers the spec does not provide, which the A2/S1-G2 authorization forbids
("No Strategy Innovation"). This package therefore implements the layer the
state-machine document itself describes as `validator_rules`:
`validator_never_computes_structure` / `detection_modules_produce_evidence` —
a pure guard/transition engine over pre-built Evidence objects, not a
price-level detector. Golden/negative-case tests construct Evidence objects
directly rather than deriving them from raw candles under thresholds that do
not exist yet.
"""
