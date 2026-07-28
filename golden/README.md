ST-C3 golden-case library scaffold.

Each category folder should eventually contain curated deterministic fixtures with:
- source evidence JSON
- expected state transitions
- expected trade-plan output
- notes about why the case is canonical

This scaffold is intentionally empty of fabricated market cases. It exists so the
daily workflow and test automation can point to stable artifact locations while
the real library is curated gate-by-gate.
