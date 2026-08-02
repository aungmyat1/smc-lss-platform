from __future__ import annotations

import builtins

from tools import st_c5_3_connection_check as check


class _Info:
    def __init__(self, **values):
        self.values = values

    def _asdict(self):
        return self.values


class _FakeMT5:
    def __init__(self, server: str, company: str = "MetaQuotes Ltd."):
        self.server = server
        self.company = company

    def initialize(self):
        return True

    def terminal_info(self):
        return _Info(connected=True, build=6063)

    def account_info(self):
        return _Info(server=self.server, company=self.company)

    def symbol_select(self, symbol, selected):
        return True

    def symbol_info(self, symbol):
        return _Info(description=f"{symbol} test", path=f"Forex\\{symbol}")

    def shutdown(self):
        return None


def _patch_mt5(monkeypatch, fake):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "MetaTrader5":
            return fake
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)


def test_connection_check_rejects_wrong_server(tmp_path, monkeypatch):
    _patch_mt5(monkeypatch, _FakeMT5("VTMarkets-Demo", "VT Markets (Pty) Ltd"))

    result = check.run_connection_check(report_dir=tmp_path, filename_stem="check")

    assert result["status"] == "PENDING_METAQUOTES_CONNECTION"
    assert result["server"] == "VTMarkets-Demo"
    assert (tmp_path / "check.json").exists()
    assert (tmp_path / "check.md").exists()


def test_connection_check_allows_metaquotes_server(tmp_path, monkeypatch):
    _patch_mt5(monkeypatch, _FakeMT5("MetaQuotes-Demo"))

    result = check.run_connection_check(report_dir=tmp_path, filename_stem="check")

    assert result["status"] == "READY_FOR_HISTORY_GATE"
    assert result["next_action"] == "Run python -m tools.st_c5_3_history_sync_gate"
