#!/usr/bin/env python3
"""Gate: block A3 statistical-validation work until a candidate's A2 rule
coverage is closed (Lever F).

Reads an `A2_RULE_COVERAGE_MATRIX.json`-shaped file (schema:
`reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`) and refuses to
report closed while `summary.missing_rule_test_mappings > 0`. This
generalizes the ST-C2 completion-audit gate so any candidate's A3 runner can
call `a2_is_closed(matrix_path)` instead of re-deriving the same check.

This script only reports a boolean gate result — it does not itself open or
close any governance gate. Actual A2 closure requires the governance process
already used for ST-C2/ST-C3 (rule-to-test mapping, completion audit, owner
review), not just this script returning True.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def a2_is_closed(matrix_path: str | Path) -> bool:
    data = json.loads(Path(matrix_path).read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    missing = summary.get("missing_rule_test_mappings")
    if missing is None:
        raise KeyError(
            f"{matrix_path}: summary.missing_rule_test_mappings not present — "
            "cannot determine A2 closure from this file's schema"
        )
    return int(missing) == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix_path", help="Path to an A2_RULE_COVERAGE_MATRIX.json file")
    args = parser.parse_args(argv)
    closed = a2_is_closed(args.matrix_path)
    print("A2_CLOSED" if closed else "A2_OPEN")
    return 0 if closed else 1


if __name__ == "__main__":
    raise SystemExit(main())
