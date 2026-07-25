"""Tests for the generic A2-closure gate (scripts/check_a2_closure.py)."""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from check_a2_closure import a2_is_closed, main  # noqa: E402


def _write_matrix(tmp_path, missing: int):
    path = tmp_path / "matrix.json"
    path.write_text(json.dumps({"summary": {"missing_rule_test_mappings": missing}}), encoding="utf-8")
    return path


def test_a2_is_closed_true_when_zero_missing(tmp_path):
    path = _write_matrix(tmp_path, 0)
    assert a2_is_closed(path) is True


def test_a2_is_closed_false_when_missing_present(tmp_path):
    path = _write_matrix(tmp_path, 10)
    assert a2_is_closed(path) is False


def test_a2_is_closed_raises_on_missing_key(tmp_path):
    path = tmp_path / "matrix.json"
    path.write_text(json.dumps({"summary": {}}), encoding="utf-8")
    with pytest.raises(KeyError):
        a2_is_closed(path)


def test_main_returns_nonzero_exit_when_open(tmp_path):
    path = _write_matrix(tmp_path, 3)
    assert main([str(path)]) == 1


def test_main_returns_zero_exit_when_closed(tmp_path):
    path = _write_matrix(tmp_path, 0)
    assert main([str(path)]) == 0


def test_against_real_st_c2_matrix_reports_open():
    real_path = os.path.join(ROOT, "reports", "validation", "st_c2", "A2_RULE_COVERAGE_MATRIX.json")
    assert a2_is_closed(real_path) is False
