"""End-to-end config governance audit for the daily runner."""
from __future__ import annotations

import csv
import json
import os
import sys
import textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import daily_runner


ROOT = os.path.dirname(os.path.dirname(__file__))


def _write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(textwrap.dedent(text))


def _write_csv(path: str) -> None:
    rows = [
        ("2026-07-19T00:00:00Z", 1.1000, 1.1010, 1.0990, 1.1005),
        ("2026-07-19T00:05:00Z", 1.1005, 1.1020, 1.1000, 1.1015),
        ("2026-07-19T00:10:00Z", 1.1015, 1.1030, 1.1010, 1.1025),
        ("2026-07-19T00:15:00Z", 1.1025, 1.1040, 1.1020, 1.1035),
        ("2026-07-19T00:20:00Z", 1.1035, 1.1050, 1.1030, 1.1045),
        ("2026-07-19T00:25:00Z", 1.1045, 1.1060, 1.1040, 1.1055),
        ("2026-07-19T00:30:00Z", 1.1055, 1.1070, 1.1050, 1.1065),
        ("2026-07-19T00:35:00Z", 1.1065, 1.1080, 1.1060, 1.1075),
        ("2026-07-19T00:40:00Z", 1.1075, 1.1090, 1.1070, 1.1085),
        ("2026-07-19T00:45:00Z", 1.1085, 1.1100, 1.1080, 1.1095),
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close"])
        writer.writerows(rows)


def test_daily_runner_uses_config_loader_and_emits_audit_metadata(tmp_path, monkeypatch):
    watchlist_path = tmp_path / "watchlist.yaml"
    specs_dir = tmp_path / "specs"
    spec_path = specs_dir / "v1.yaml"
    research_path = specs_dir / "v3.6.yaml"
    specs_dir.mkdir()
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    data_dir.mkdir()

    _write_text(
        spec_path,
        """\
        version: 1
        track: execution
        status: active
        promotion_stage: deployed
        symbol: EURUSD
        htf: H4
        entry_tf: M15
        ltf_confirm: M1
        swing_lookback: 2
        equal_level_tol_pips: 2
        min_fvg_pips: 3
        risk_pct: 1.0
        min_rr: 2.0
        sessions: [london, ny]
        """,
    )
    _write_text(
        research_path,
        """\
        version: 3.6
        track: research
        status: draft
        promotion_stage: research
        symbol: EURUSD
        htf: H4
        entry_tf: M15
        ltf_confirm: M1
        swing_lookback: 2
        equal_level_tol_pips: 2
        min_fvg_pips: 3
        risk_pct: 1.0
        min_rr: 2.0
        sessions: [london, ny]
        """,
    )
    _write_text(
        watchlist_path,
        f"""\
        strategy_spec: specs/v1.yaml
        research_spec: specs/v3.6.yaml
        governance:
          schema_version: 1
          config_version: 3.6.0
          registry_version: 3.6.0
          approval_package_required: true
          fail_closed: true
        autonomy:
          demo: proposal_only
          live: disabled
          engine_implements_spec: false
          promote_to_live: false
        reporting:
          telegram:
            enabled: false
            bot_token_env: TELEGRAM_BOT_TOKEN
            chat_id_env: TELEGRAM_CHAT_ID
            events: [scan_summary, decision]
        cadence:
          runs_utc: ["07:00", "12:00"]
          weekdays_only: true
          timeframes: {{etrigger: H1, context: D1, confirm: M5}}
        risk:
          risk_pct_demo: 0.5
          risk_pct_live: 1.0
          position_amount_mode: risk_pct
          fixed_lot_demo: 0.01
          fixed_lot_live: 0.01
          fixed_notional_demo: 0.0
          fixed_notional_live: 0.0
          daily_loss_pct: 3.0
          max_positions: 3
          portfolio_heat_pct: 4.0
          min_rr: 2.0
        execution:
          equilibrium_window: 40
          liquidity_sweep_lookback_bars: 10
          breakeven_at_r: 1.0
          lot_step: 0.01
          killzones:
            london: {{start_hour: 7, end_hour: 10}}
            ny: {{start_hour: 12, end_hour: 15}}
        symbols:
          active:
            - {{name: EURUSD, mt5: EURUSD, pip: 0.0001, pip_value_per_lot: 10.0, variants: [E1M3]}}
          pending: []
        """,
    )
    _write_csv(str(data_dir / "EURUSD_M5.csv"))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "daily_runner.py",
            "--config",
            str(watchlist_path),
            "--data",
            str(data_dir),
            "--equity",
            "1000",
            "--env",
            "demo",
        ],
    )

    daily_runner.main()

    report_path = reports_dir / "daily_signals.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["strategy_spec"].endswith("v1.yaml")
    assert report["research_spec"].endswith("v3.6.yaml")
    assert report["schema_version"] == 1
    assert report["config_version"] == "3.6.0"
    assert report["registry_version"] == "3.6.0"
    assert report["config_hash"]
    assert report["results"]
    assert report["results"][0]["symbol"] == "EURUSD"
