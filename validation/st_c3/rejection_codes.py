"""ST-C3 rejection (R-) and termination (ERR-) codes, loaded from the frozen
spec's `rejection_code_json_schema` (§4) rather than hardcoded here, so the
code set cannot drift from `specs/st-c3_v1.0.1.yaml`.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Mapping

from validation.st_c3.evidence import load_spec


@lru_cache(maxsize=1)
def r_codes() -> Mapping[str, str]:
    return dict(load_spec()["rejection_code_json_schema"]["R_CODES"])


@lru_cache(maxsize=1)
def err_codes() -> Mapping[str, str]:
    return dict(load_spec()["rejection_code_json_schema"]["ERR_CODES"])


def is_r_code(code: str) -> bool:
    return code in r_codes()


def is_err_code(code: str) -> bool:
    return code in err_codes()
