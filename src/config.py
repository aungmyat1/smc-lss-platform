#!/usr/bin/env python3
"""Configuration loader for the SMC-LSS live execution path (Phase 3 M1).

Loads and validates config/watchlist.yaml (risk, symbols, execution knobs) and
specs/v1.yaml (execution-track strategy shape). Fails closed: a missing or
invalid value raises ConfigError rather than being silently defaulted, so a
broken config blocks the live path instead of running on a guessed value.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from types import MappingProxyType
from typing import Any, NoReturn

import yaml

logger = logging.getLogger(__name__)

SUPPORTED_SCHEMA_VERSIONS = {1}
ALLOWED_WATCHLIST_KEYS = {
    "strategy_spec",
    "research_spec",
    "governance",
    "autonomy",
    "risk",
    "execution",
    "reporting",
    "cadence",
    "symbols",
}
ALLOWED_GOVERNANCE_KEYS = {
    "schema_version",
    "config_version",
    "registry_version",
    "approval_package_required",
    "fail_closed",
}
ALLOWED_AUTONOMY_KEYS = {
    "demo",
    "live",
    "engine_implements_spec",
    "promote_to_live",
}
ALLOWED_RISK_KEYS = {
    "risk_pct_demo",
    "risk_pct_live",
    "min_rr",
    "daily_loss_pct",
    "max_positions",
    "portfolio_heat_pct",
    "position_amount_mode",
    "fixed_lot_demo",
    "fixed_lot_live",
    "fixed_notional_demo",
    "fixed_notional_live",
}
ALLOWED_EXECUTION_KEYS = {
    "equilibrium_window",
    "liquidity_sweep_lookback_bars",
    "breakeven_at_r",
    "lot_step",
    "killzones",
}
ALLOWED_REPORTING_KEYS = {"telegram"}
ALLOWED_TELEGRAM_KEYS = {"enabled", "bot_token_env", "chat_id_env", "events"}
ALLOWED_CADENCE_KEYS = {"runs_utc", "weekdays_only", "timeframes"}
ALLOWED_TIMEFRAME_KEYS = {"etrigger", "context", "confirm"}
ALLOWED_SYMBOL_KEYS = {"name", "mt5", "pip", "pip_value_per_lot", "variants"}
ALLOWED_SPEC_KEYS = {
    "version",
    "track",
    "status",
    "promotion_stage",
    "symbol",
    "htf",
    "entry_tf",
    "ltf_confirm",
    "swing_lookback",
    "equal_level_tol_pips",
    "min_fvg_pips",
    "risk_pct",
    "min_rr",
    "sessions",
}


class ConfigError(Exception):
    """Raised when configuration is missing or fails schema validation."""


def _reject(message: str) -> NoReturn:
    logger.error(message)
    raise ConfigError(message)


def _load_yaml(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        _reject(f"config file not found: {path}")
    except yaml.YAMLError as ex:
        _reject(f"{path}: invalid YAML ({ex})")
    if not isinstance(data, dict):
        _reject(f"{path}: expected a YAML mapping at top level")
    return data


def _reject_unknown_keys(d: dict, allowed: set[str], path: str) -> None:
    unknown = sorted(set(d) - allowed)
    if unknown:
        _reject(f"{path}: unknown keys: {', '.join(unknown)}")


def _type_name(typ: type | tuple[type, ...]) -> str:
    if isinstance(typ, tuple):
        return " or ".join(t.__name__ for t in typ)
    return typ.__name__


def _require(d: dict, key: str, path: str, typ: type | tuple[type, ...] | None = None) -> Any:
    if key not in d or d[key] is None:
        _reject(f"{path}: missing required key '{key}'")
    v = d[key]
    numeric = typ is int or typ == (int, float)
    if typ is not None and (not isinstance(v, typ) or (numeric and isinstance(v, bool))):
        _reject(f"{path}: '{key}' must be {_type_name(typ)}, got {type(v).__name__}")
    return v


def _positive(v: float, path: str, key: str) -> float:
    if not (isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0):
        _reject(f"{path}: '{key}' must be a positive number, got {v!r}")
    return v


def _hour(v: int, path: str, key: str) -> int:
    if not (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 24):
        _reject(f"{path}: '{key}' must be an hour in [0, 24], got {v!r}")
    return v


def _resolve_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def _ensure_file_exists(path: str, label: str) -> None:
    if not os.path.isfile(path):
        _reject(f"{label}: file not found: {path}")


def _version_tuple(version: str, path: str, key: str) -> tuple[int, int, int]:
    if not isinstance(version, str):
        _reject(f"{path}: '{key}' must be a string, got {type(version).__name__}")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        _reject(f"{path}: '{key}' must use MAJOR.MINOR.PATCH, got {version!r}")
    return tuple(int(part) for part in match.groups())


def _version_prefix(version: str, path: str, key: str) -> tuple[int, int]:
    major, minor, _patch = _version_tuple(version, path, key)
    return major, minor


def _freeze_tuple(items: list[Any]) -> tuple[Any, ...]:
    return tuple(items)


class FrozenConfig:
    __slots__ = ("_frozen",)

    def _freeze(self) -> None:
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError(f"{self.__class__.__name__} is immutable")
        object.__setattr__(self, name, value)


class RiskConfig(FrozenConfig):
    __slots__ = (
        "risk_pct_demo",
        "risk_pct_live",
        "min_rr",
        "daily_loss_pct",
        "max_positions",
        "portfolio_heat_pct",
        "position_amount_mode",
        "fixed_lot_demo",
        "fixed_lot_live",
        "fixed_notional_demo",
        "fixed_notional_live",
    )

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_RISK_KEYS, path)
        object.__setattr__(self, "risk_pct_demo", _positive(_require(d, "risk_pct_demo", path, (int, float)), path, "risk_pct_demo"))
        object.__setattr__(self, "risk_pct_live", _positive(_require(d, "risk_pct_live", path, (int, float)), path, "risk_pct_live"))
        object.__setattr__(self, "min_rr", _positive(_require(d, "min_rr", path, (int, float)), path, "min_rr"))
        object.__setattr__(self, "daily_loss_pct", _positive(_require(d, "daily_loss_pct", path, (int, float)), path, "daily_loss_pct"))
        max_positions = _require(d, "max_positions", path, int)
        if max_positions < 1:
            _reject(f"{path}: 'max_positions' must be >= 1")
        object.__setattr__(self, "max_positions", max_positions)
        object.__setattr__(self, "portfolio_heat_pct", _positive(_require(d, "portfolio_heat_pct", path, (int, float)), path, "portfolio_heat_pct"))
        position_amount_mode = _require(d, "position_amount_mode", path, str)
        if position_amount_mode not in ("risk_pct", "fixed_lot", "fixed_notional"):
            _reject(f"{path}: 'position_amount_mode' must be one of risk_pct|fixed_lot|fixed_notional")
        object.__setattr__(self, "position_amount_mode", position_amount_mode)
        object.__setattr__(self, "fixed_lot_demo", _require(d, "fixed_lot_demo", path, (int, float)))
        object.__setattr__(self, "fixed_lot_live", _require(d, "fixed_lot_live", path, (int, float)))
        object.__setattr__(self, "fixed_notional_demo", _require(d, "fixed_notional_demo", path, (int, float)))
        object.__setattr__(self, "fixed_notional_live", _require(d, "fixed_notional_live", path, (int, float)))
        self._freeze()

    def risk_pct_for(self, env: str) -> float:
        if env not in ("demo", "live"):
            _reject(f"unknown env '{env}' (expected 'demo' or 'live')")
        return self.risk_pct_live if env == "live" else self.risk_pct_demo


class KillzoneConfig(FrozenConfig):
    __slots__ = ("name", "start_hour", "end_hour")

    def __init__(self, name: str, d: dict, path: str) -> None:
        _reject_unknown_keys(d, {"start_hour", "end_hour"}, path)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "start_hour", _hour(_require(d, "start_hour", path, int), path, "start_hour"))
        object.__setattr__(self, "end_hour", _hour(_require(d, "end_hour", path, int), path, "end_hour"))
        if self.end_hour <= self.start_hour:
            _reject(f"{path}: 'end_hour' must be greater than 'start_hour'")
        self._freeze()

    def contains(self, hour: int) -> bool:
        return self.start_hour <= hour < self.end_hour


class ExecutionConfig(FrozenConfig):
    __slots__ = ("equilibrium_window", "liquidity_sweep_lookback_bars", "breakeven_at_r", "lot_step", "killzones")

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_EXECUTION_KEYS, path)
        equilibrium_window = _require(d, "equilibrium_window", path, int)
        if equilibrium_window < 1:
            _reject(f"{path}: 'equilibrium_window' must be >= 1")
        object.__setattr__(self, "equilibrium_window", equilibrium_window)
        liquidity_sweep_lookback_bars = _require(d, "liquidity_sweep_lookback_bars", path, int)
        if liquidity_sweep_lookback_bars < 1:
            _reject(f"{path}: 'liquidity_sweep_lookback_bars' must be >= 1")
        object.__setattr__(self, "liquidity_sweep_lookback_bars", liquidity_sweep_lookback_bars)
        object.__setattr__(self, "breakeven_at_r", _positive(_require(d, "breakeven_at_r", path, (int, float)), path, "breakeven_at_r"))
        object.__setattr__(self, "lot_step", _positive(_require(d, "lot_step", path, (int, float)), path, "lot_step"))
        kz = _require(d, "killzones", path, dict)
        if not kz:
            _reject(f"{path}: 'killzones' must define at least one session")
        killzones = {name: KillzoneConfig(name, v, f"{path}.killzones.{name}") for name, v in kz.items()}
        object.__setattr__(self, "killzones", MappingProxyType(killzones))
        self._freeze()

    def session_of(self, hour: int) -> tuple[str, bool]:
        for kz in self.killzones.values():
            if kz.contains(hour):
                return kz.name.upper() + "-KZ", True
        return "OFF-KZ", False


class SymbolConfig(FrozenConfig):
    __slots__ = ("name", "mt5", "pip", "pip_value_per_lot", "variants")

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_SYMBOL_KEYS, path)
        object.__setattr__(self, "name", _require(d, "name", path, str))
        object.__setattr__(self, "mt5", _require(d, "mt5", path, str))
        object.__setattr__(self, "pip", _positive(_require(d, "pip", path, (int, float)), path, "pip"))
        object.__setattr__(self, "pip_value_per_lot", _positive(_require(d, "pip_value_per_lot", path, (int, float)), path, "pip_value_per_lot"))
        variants = d.get("variants", [])
        if not isinstance(variants, list):
            _reject(f"{path}: 'variants' must be a list")
        object.__setattr__(self, "variants", _freeze_tuple(variants))
        self._freeze()


class AutonomyConfig(FrozenConfig):
    __slots__ = ("demo", "live", "engine_implements_spec", "promote_to_live")

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_AUTONOMY_KEYS, path)
        object.__setattr__(self, "demo", _require(d, "demo", path, str))
        object.__setattr__(self, "live", _require(d, "live", path, str))
        object.__setattr__(self, "engine_implements_spec", _require(d, "engine_implements_spec", path, bool))
        object.__setattr__(self, "promote_to_live", _require(d, "promote_to_live", path, bool))
        self._freeze()


class ReportingConfig(FrozenConfig):
    __slots__ = ("telegram",)

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_REPORTING_KEYS, path)
        telegram_raw = _require(d, "telegram", path, dict)
        telegram_path = f"{path}.telegram"
        _reject_unknown_keys(telegram_raw, ALLOWED_TELEGRAM_KEYS, telegram_path)
        enabled = _require(telegram_raw, "enabled", telegram_path, bool)
        bot_token_env = _require(telegram_raw, "bot_token_env", telegram_path, str)
        chat_id_env = _require(telegram_raw, "chat_id_env", telegram_path, str)
        events = _require(telegram_raw, "events", telegram_path, list)
        if not events:
            _reject(f"{telegram_path}: 'events' must be non-empty")
        if not all(isinstance(event, str) and event for event in events):
            _reject(f"{telegram_path}: 'events' must contain non-empty strings")
        object.__setattr__(
            self,
            "telegram",
            MappingProxyType(
                {
                    "enabled": enabled,
                    "bot_token_env": bot_token_env,
                    "chat_id_env": chat_id_env,
                    "events": _freeze_tuple(events),
                }
            ),
        )
        self._freeze()


class CadenceConfig(FrozenConfig):
    __slots__ = ("runs_utc", "weekdays_only", "timeframes")

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_CADENCE_KEYS, path)
        runs_utc = _require(d, "runs_utc", path, list)
        if not runs_utc:
            _reject(f"{path}: 'runs_utc' must be non-empty")
        if not all(isinstance(run, str) and run for run in runs_utc):
            _reject(f"{path}: 'runs_utc' must contain non-empty strings")
        object.__setattr__(self, "runs_utc", _freeze_tuple(runs_utc))
        object.__setattr__(self, "weekdays_only", _require(d, "weekdays_only", path, bool))
        timeframes = _require(d, "timeframes", path, dict)
        _reject_unknown_keys(timeframes, ALLOWED_TIMEFRAME_KEYS, f"{path}.timeframes")
        etrigger = _require(timeframes, "etrigger", f"{path}.timeframes", str)
        context = _require(timeframes, "context", f"{path}.timeframes", str)
        confirm = _require(timeframes, "confirm", f"{path}.timeframes", str)
        object.__setattr__(self, "timeframes", MappingProxyType({"etrigger": etrigger, "context": context, "confirm": confirm}))
        self._freeze()


class StrategyConfig(FrozenConfig):
    """Strategy-shape parameters for the execution-track spec (specs/v1.yaml)."""

    __slots__ = (
        "version",
        "track",
        "status",
        "promotion_stage",
        "symbol",
        "htf",
        "entry_tf",
        "ltf_confirm",
        "swing_lookback",
        "equal_level_tol_pips",
        "min_fvg_pips",
        "risk_pct",
        "min_rr",
        "sessions",
    )

    def __init__(self, d: dict, path: str) -> None:
        _reject_unknown_keys(d, ALLOWED_SPEC_KEYS, path)
        version = _require(d, "version", path, int)
        if version != 1:
            _reject(f"{path}: 'version' must be 1, got {version!r}")
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "track", d.get("track"))
        object.__setattr__(self, "status", d.get("status"))
        object.__setattr__(self, "promotion_stage", d.get("promotion_stage"))
        object.__setattr__(self, "symbol", _require(d, "symbol", path, str))
        object.__setattr__(self, "htf", _require(d, "htf", path, str))
        object.__setattr__(self, "entry_tf", _require(d, "entry_tf", path, str))
        object.__setattr__(self, "ltf_confirm", _require(d, "ltf_confirm", path, str))
        swing_lookback = _require(d, "swing_lookback", path, int)
        if swing_lookback < 1:
            _reject(f"{path}: 'swing_lookback' must be >= 1")
        object.__setattr__(self, "swing_lookback", swing_lookback)
        object.__setattr__(self, "equal_level_tol_pips", _positive(_require(d, "equal_level_tol_pips", path, (int, float)), path, "equal_level_tol_pips"))
        object.__setattr__(self, "min_fvg_pips", _positive(_require(d, "min_fvg_pips", path, (int, float)), path, "min_fvg_pips"))
        object.__setattr__(self, "risk_pct", _positive(_require(d, "risk_pct", path, (int, float)), path, "risk_pct"))
        object.__setattr__(self, "min_rr", _positive(_require(d, "min_rr", path, (int, float)), path, "min_rr"))
        sessions = _require(d, "sessions", path, list)
        if not sessions:
            _reject(f"{path}: 'sessions' must be non-empty")
        if not all(isinstance(session, str) and session for session in sessions):
            _reject(f"{path}: 'sessions' must contain non-empty strings")
        object.__setattr__(self, "sessions", _freeze_tuple(sessions))
        self._freeze()


class Config(FrozenConfig):
    __slots__ = (
        "watchlist_path",
        "spec_path",
        "strategy_spec",
        "strategy_spec_path",
        "research_spec",
        "research_spec_path",
        "schema_version",
        "config_version",
        "registry_version",
        "config_hash",
        "governance",
        "autonomy",
        "reporting",
        "cadence",
        "risk",
        "execution",
        "symbols_active",
        "symbols_pending",
        "strategy",
    )

    def __init__(self, watchlist_path: str, spec_path: str, raw_watchlist: dict, raw_spec: dict) -> None:
        _reject_unknown_keys(raw_watchlist, ALLOWED_WATCHLIST_KEYS, watchlist_path)

        watchlist_abs = _resolve_path(watchlist_path)
        spec_abs = _resolve_path(spec_path)
        strategy_spec_raw = _require(raw_watchlist, "strategy_spec", watchlist_path, str)
        strategy_spec_abs = _resolve_path(strategy_spec_raw)
        if strategy_spec_abs != spec_abs:
            _reject(
                f"{watchlist_path}: 'strategy_spec' must match the loaded spec path "
                f"({strategy_spec_raw!r} != {spec_path!r})"
            )
        _ensure_file_exists(watchlist_abs, "watchlist")
        _ensure_file_exists(strategy_spec_abs, "strategy_spec")
        _ensure_file_exists(spec_abs, "spec")

        research_spec_raw = _require(raw_watchlist, "research_spec", watchlist_path, str)
        research_spec_abs = _resolve_path(research_spec_raw)
        _ensure_file_exists(research_spec_abs, "research_spec")

        governance_raw = _require(raw_watchlist, "governance", watchlist_path, dict)
        _reject_unknown_keys(governance_raw, ALLOWED_GOVERNANCE_KEYS, f"{watchlist_path}:governance")
        schema_version = _require(governance_raw, "schema_version", f"{watchlist_path}:governance", int)
        if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            _reject(
                f"{watchlist_path}:governance: unsupported schema_version {schema_version!r}; "
                f"supported={sorted(SUPPORTED_SCHEMA_VERSIONS)}"
            )
        config_version = _require(governance_raw, "config_version", f"{watchlist_path}:governance", str)
        registry_version = _require(governance_raw, "registry_version", f"{watchlist_path}:governance", str)
        config_prefix = _version_prefix(config_version, f"{watchlist_path}:governance", "config_version")
        registry_prefix = _version_prefix(registry_version, f"{watchlist_path}:governance", "registry_version")
        if config_prefix != registry_prefix:
            _reject(
                f"{watchlist_path}:governance: config_version {config_version!r} is incompatible "
                f"with registry_version {registry_version!r}"
            )
        approval_package_required = _require(governance_raw, "approval_package_required", f"{watchlist_path}:governance", bool)
        fail_closed = _require(governance_raw, "fail_closed", f"{watchlist_path}:governance", bool)
        governance = MappingProxyType(
            {
                "schema_version": schema_version,
                "config_version": config_version,
                "registry_version": registry_version,
                "approval_package_required": approval_package_required,
                "fail_closed": fail_closed,
            }
        )

        autonomy_raw = _require(raw_watchlist, "autonomy", watchlist_path, dict)
        autonomy = AutonomyConfig(autonomy_raw, f"{watchlist_path}:autonomy")
        reporting_raw = _require(raw_watchlist, "reporting", watchlist_path, dict)
        reporting = ReportingConfig(reporting_raw, f"{watchlist_path}:reporting")
        cadence_raw = _require(raw_watchlist, "cadence", watchlist_path, dict)
        cadence = CadenceConfig(cadence_raw, f"{watchlist_path}:cadence")

        risk = RiskConfig(_require(raw_watchlist, "risk", watchlist_path, dict), f"{watchlist_path}:risk")
        execution = ExecutionConfig(_require(raw_watchlist, "execution", watchlist_path, dict), f"{watchlist_path}:execution")

        symbols = _require(raw_watchlist, "symbols", watchlist_path, dict)
        _reject_unknown_keys(symbols, {"active", "pending"}, f"{watchlist_path}:symbols")
        active = _require(symbols, "active", f"{watchlist_path}:symbols", list)
        if not active:
            _reject(f"{watchlist_path}:symbols.active must list at least one symbol")
        pending = symbols.get("pending", [])
        if not isinstance(pending, list):
            _reject(f"{watchlist_path}:symbols.pending must be a list")

        symbols_active = [SymbolConfig(s, f"{watchlist_path}:symbols.active[{i}]") for i, s in enumerate(active)]
        symbols_pending = [SymbolConfig(s, f"{watchlist_path}:symbols.pending[{i}]") for i, s in enumerate(pending)]
        names = [s.name for s in symbols_active + symbols_pending]
        if len(set(names)) != len(names):
            _reject(f"{watchlist_path}:symbols contains duplicate symbol names")

        strategy = StrategyConfig(raw_spec, spec_path)
        if abs(strategy.min_rr - risk.min_rr) > 1e-12:
            _reject(
                f"{spec_path} and {watchlist_path}:risk disagree on min_rr "
                f"({strategy.min_rr!r} != {risk.min_rr!r})"
            )

        raw_blob = yaml.safe_dump({"watchlist": raw_watchlist, "spec": raw_spec}, sort_keys=True)
        config_hash = hashlib.sha256(raw_blob.encode("utf-8")).hexdigest()

        object.__setattr__(self, "watchlist_path", watchlist_abs)
        object.__setattr__(self, "spec_path", spec_abs)
        object.__setattr__(self, "strategy_spec", strategy_spec_raw)
        object.__setattr__(self, "strategy_spec_path", strategy_spec_abs)
        object.__setattr__(self, "research_spec", research_spec_raw)
        object.__setattr__(self, "research_spec_path", research_spec_abs)
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "config_version", config_version)
        object.__setattr__(self, "registry_version", registry_version)
        object.__setattr__(self, "config_hash", config_hash)
        object.__setattr__(self, "governance", governance)
        object.__setattr__(self, "autonomy", autonomy)
        object.__setattr__(self, "reporting", reporting)
        object.__setattr__(self, "cadence", cadence)
        object.__setattr__(self, "risk", risk)
        object.__setattr__(self, "execution", execution)
        object.__setattr__(self, "symbols_active", _freeze_tuple(symbols_active))
        object.__setattr__(self, "symbols_pending", _freeze_tuple(symbols_pending))
        object.__setattr__(self, "strategy", strategy)
        self._freeze()

    def symbol(self, name: str) -> SymbolConfig:
        for s in self.symbols_active + self.symbols_pending:
            if s.name == name:
                return s
        _reject(f"unknown symbol '{name}' (not in {self.watchlist_path} symbols.active/pending)")


def load(watchlist_path: str = "config/watchlist.yaml", spec_path: str = "specs/v1.yaml") -> Config:
    raw_watchlist = _load_yaml(watchlist_path)
    raw_spec = _load_yaml(spec_path)
    return Config(watchlist_path, spec_path, raw_watchlist, raw_spec)
