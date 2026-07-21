# Phase A Generated-Artifact Policy

## Kept In Git

- Strategy and research specifications.
- Source code and tests.
- Compact audit reports, conformance matrices, manifests, hashes, and summary metrics.
- Small fixtures required for deterministic regression tests.

## Excluded From Git

- `validation/cache/*.json`
- `validation/cache/baseline_*/`
- `validation/cache/phase_a_*/`
- `reports/refinement/baseline_2sym_*/`
- `reports/audit/phase_a_gate/`
- `reports/audit/phase_a_debug_*/`
- `reports/audit/phase_a_final_*/`
- `reports/audit/phase_a_manual_*/`

These are reproducible replay or cache outputs. They may be retained locally and should be uploaded as GitHub Actions artifacts when produced in CI.

## Regeneration

Run the canonical Phase A gate by module invocation:

```bash
python -m src.research.run_phase_a_gate --ci-status unknown
```

For development-only focused checks, keep the required full-suite command intact and pass a separate focused command:

```bash
python -m src.research.run_phase_a_gate --focused-test-command "python -m pytest tests/test_phase_a_stop_report.py -q"
```

Canonical evidence is valid only when the report records the current HEAD, complete three-symbol data coverage, clean A/B/resumed reproducibility, a passing full local suite, and exact-HEAD successful GitHub CI.
