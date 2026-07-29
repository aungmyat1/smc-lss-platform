#!/usr/bin/env python3
"""Verify an ST-C3 replay ledger against its SHA-256 hash file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validation.st_c3.replay_engine import verify_ledger_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path, help="Path to ledger.json")
    parser.add_argument("--hash", required=True, type=Path, help="Path to ledger.hash")
    args = parser.parse_args()
    digest = verify_ledger_hash(args.ledger, args.hash)
    print(json.dumps({"status": "PASS", "ledger_sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
