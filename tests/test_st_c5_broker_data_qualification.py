from __future__ import annotations

import yaml

from tools.st_c5_broker_data_qualification import run_broker_data_qualification


def test_broker_qualification_prepares_unapproved_candidate_without_acquire(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_broker_data_qualification(candidate_dir=tmp_path / "candidate", write_reports=True)

    assert result["decision"]["recommendation"] == "BROKER_DATA_PENDING"
    assert result["decision"]["dataset_status"] == "NOT_APPROVED"
    assert result["decision"]["replay_status"] == "BLOCKED"
    assert (tmp_path / "candidate/DATASET_MANIFEST_ST_C3.yaml").exists()
    manifest = yaml.safe_load((tmp_path / "candidate/DATASET_MANIFEST_ST_C3.yaml").read_text(encoding="utf-8"))
    assert manifest["approved"] is False
    assert manifest["approval_status"] == "NOT_APPROVED"
    assert manifest["provider"] == "Vantage MT5"
    assert (tmp_path / "reports/st_c5/BROKER_DATA_QUALIFICATION_STATUS.json").exists()
    assert (tmp_path / "research_data/metadata/ST_C5_BROKER_CANDIDATE.json").exists()


def test_broker_qualification_acquire_blocks_when_metatrader_package_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "MetaTrader5":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = run_broker_data_qualification(candidate_dir=tmp_path / "candidate", acquire=True, write_reports=False)

    assert result["acquisition"]["status"] == "BLOCKED"
    assert result["decision"]["recommendation"] == "BROKER_DATA_PENDING"
    assert result["decision"]["strategy_validation_status"] == "BLOCKED"


def test_broker_qualification_custom_broker_name_is_recorded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_broker_data_qualification(candidate_dir=tmp_path / "candidate", broker="Example Broker MT5", write_reports=False)

    manifest = yaml.safe_load((tmp_path / "candidate/DATASET_MANIFEST_ST_C3.yaml").read_text(encoding="utf-8"))
    assert result["broker"] == "Example Broker MT5"
    assert manifest["provider"] == "Example Broker MT5"
