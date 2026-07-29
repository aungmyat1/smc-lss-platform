"""Governance-safe ST-C3 replay ledger and hashing primitives.

This module implements the deterministic ledger contract needed by the
ultra-fast validation funnel. It does not open A3, place orders, connect to a
broker, optimize rules, or rely on the quarantined A3 replay path.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

LEDGER_HASH_PREFIX = "st_c3_ledger_sha256="
REPLAY_ENGINE_VERSION = "st_c3_replay_engine.v1"


@dataclass(frozen=True)
class TradeRecord:
    id: str
    symbol: str
    timestamp_entry: str
    timestamp_exit: str
    direction: str
    entry_price: float
    exit_price: float
    size: float
    r: float
    mae_r: float
    mfe_r: float
    session: str
    news_flag: bool
    rationale: str
    win_loss: str
    chain_id: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tags"] = list(self.tags)
        return data


@dataclass(frozen=True)
class ReplayLedger:
    meta: Mapping[str, Any]
    trades: tuple[TradeRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        trades = sorted(
            (trade.to_dict() for trade in self.trades),
            key=lambda item: (
                str(item["timestamp_entry"]),
                str(item["symbol"]),
                str(item["id"]),
            ),
        )
        meta = dict(self.meta)
        meta.setdefault("replay_engine_version", REPLAY_ENGINE_VERSION)
        return {"meta": meta, "trades": trades}


def build_ledger(trade_records: Iterable[TradeRecord], meta: Mapping[str, Any] | None = None) -> ReplayLedger:
    """Build a normalized ST-C3 replay ledger from already-authorized records."""
    ledger = ReplayLedger(meta=dict(meta or {}), trades=tuple(trade_records))
    _validate_ledger_dict(ledger.to_dict())
    return ledger


def run_replay(
    *,
    spec_version: str,
    symbols: Iterable[str],
    date_from: str,
    date_to: str,
    tf_set: Iterable[str],
    source_ledger: str | Path | None = None,
    sample: bool = False,
) -> ReplayLedger:
    """Create a deterministic replay ledger without opening A3.

    `source_ledger` is for owner-approved normalized replay input. `sample`
    produces a tiny deterministic fixture for CI and dry-run plumbing only.
    """
    if spec_version != "1.0.7":
        raise ValueError("ST-C3 replay runner is locked to frozen spec version 1.0.7")
    if source_ledger and sample:
        raise ValueError("choose either source_ledger or sample, not both")
    meta = {
        "strategy_id": "ST-C3",
        "version": spec_version,
        "data_range": {"from": date_from, "to": date_to},
        "symbols": sorted(symbols),
        "tf_set": list(tf_set),
        "governance_status": "does_not_open_A3_or_imply_acceptance",
    }
    if source_ledger:
        data = load_ledger(source_ledger)
        source_meta = dict(data["meta"])
        source_meta.update(meta)
        return ReplayLedger(
            meta=source_meta,
            trades=tuple(_trade_record_from_dict(trade) for trade in data["trades"]),
        )
    if sample:
        meta["sample_mode"] = True
        meta["sample_note"] = "Synthetic dry-run fixture; not A3 evidence."
        return build_ledger(_sample_trades(), meta)
    raise ValueError("no approved replay source supplied; use --source-ledger or --sample for dry-run")


def canonical_ledger_bytes(ledger: ReplayLedger | Mapping[str, Any]) -> bytes:
    """Return byte-stable JSON bytes for hashing and writing."""
    data = ledger.to_dict() if isinstance(ledger, ReplayLedger) else dict(ledger)
    _validate_ledger_dict(data)
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def write_ledger(ledger: ReplayLedger | Mapping[str, Any], path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(canonical_ledger_bytes(ledger))
    return out_path


def load_ledger(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    _validate_ledger_dict(data)
    return data


def compute_ledger_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_ledger_hash(ledger_path: str | Path, hash_path: str | Path) -> str:
    digest = compute_ledger_sha256(ledger_path)
    out_path = Path(hash_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"{LEDGER_HASH_PREFIX}{digest}\n", encoding="utf-8")
    return digest


def read_ledger_hash(hash_path: str | Path) -> str:
    text = Path(hash_path).read_text(encoding="utf-8").strip()
    if not text.startswith(LEDGER_HASH_PREFIX):
        raise ValueError(f"ledger hash must start with {LEDGER_HASH_PREFIX!r}")
    digest = text[len(LEDGER_HASH_PREFIX):]
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("ledger hash must be a lowercase SHA-256 hex digest")
    return digest


def verify_ledger_hash(ledger_path: str | Path, hash_path: str | Path) -> str:
    expected = read_ledger_hash(hash_path)
    actual = compute_ledger_sha256(ledger_path)
    if actual != expected:
        raise ValueError(f"ledger hash mismatch: expected {expected}, got {actual}")
    return actual


def _validate_ledger_dict(data: Mapping[str, Any]) -> None:
    if not isinstance(data.get("meta"), Mapping):
        raise ValueError("ledger requires a meta object")
    trades = data.get("trades")
    if not isinstance(trades, list):
        raise ValueError("ledger requires a trades array")
    required = {
        "id",
        "symbol",
        "timestamp_entry",
        "timestamp_exit",
        "direction",
        "entry_price",
        "exit_price",
        "size",
        "r",
        "mae_r",
        "mfe_r",
        "session",
        "news_flag",
        "rationale",
        "win_loss",
    }
    for index, trade in enumerate(trades):
        if not isinstance(trade, Mapping):
            raise ValueError(f"trade {index} must be an object")
        missing = required - set(trade)
        if missing:
            raise ValueError(f"trade {index} missing required fields: {sorted(missing)}")


def _trade_record_from_dict(data: Mapping[str, Any]) -> TradeRecord:
    return TradeRecord(
        id=str(data["id"]),
        symbol=str(data["symbol"]),
        timestamp_entry=str(data["timestamp_entry"]),
        timestamp_exit=str(data["timestamp_exit"]),
        direction=str(data["direction"]),
        entry_price=float(data["entry_price"]),
        exit_price=float(data["exit_price"]),
        size=float(data["size"]),
        r=float(data["r"]),
        mae_r=float(data["mae_r"]),
        mfe_r=float(data["mfe_r"]),
        session=str(data["session"]),
        news_flag=bool(data["news_flag"]),
        rationale=str(data["rationale"]),
        win_loss=str(data["win_loss"]),
        chain_id=str(data["chain_id"]) if data.get("chain_id") is not None else None,
        tags=tuple(str(tag) for tag in data.get("tags", ())),
    )


def _sample_trades() -> tuple[TradeRecord, ...]:
    return (
        TradeRecord(
            id="sample-2024-gbpusd-001",
            symbol="GBPUSD",
            timestamp_entry="2024-01-02T08:00:00Z",
            timestamp_exit="2024-01-02T09:00:00Z",
            direction="LONG",
            entry_price=1.1000,
            exit_price=1.1010,
            size=1.0,
            r=2.0,
            mae_r=-0.2,
            mfe_r=2.2,
            session="LONDON",
            news_flag=False,
            rationale="synthetic dry-run sample",
            win_loss="win",
            chain_id="sample-chain-001",
            tags=("sample",),
        ),
        TradeRecord(
            id="sample-2024-gbpusd-002",
            symbol="GBPUSD",
            timestamp_entry="2024-02-02T08:00:00Z",
            timestamp_exit="2024-02-02T09:00:00Z",
            direction="SHORT",
            entry_price=1.1000,
            exit_price=1.1005,
            size=1.0,
            r=-0.5,
            mae_r=-0.6,
            mfe_r=0.4,
            session="NY",
            news_flag=False,
            rationale="synthetic dry-run sample",
            win_loss="loss",
            chain_id="sample-chain-002",
            tags=("sample",),
        ),
        TradeRecord(
            id="sample-2025-gbpusd-001",
            symbol="GBPUSD",
            timestamp_entry="2025-01-02T08:00:00Z",
            timestamp_exit="2025-01-02T09:00:00Z",
            direction="LONG",
            entry_price=1.1000,
            exit_price=1.1012,
            size=1.0,
            r=2.4,
            mae_r=-0.1,
            mfe_r=2.6,
            session="LONDON",
            news_flag=False,
            rationale="synthetic dry-run sample",
            win_loss="win",
            chain_id="sample-chain-003",
            tags=("sample",),
        ),
        TradeRecord(
            id="sample-2025-gbpusd-002",
            symbol="GBPUSD",
            timestamp_entry="2025-02-02T08:00:00Z",
            timestamp_exit="2025-02-02T09:00:00Z",
            direction="SHORT",
            entry_price=1.1000,
            exit_price=1.1004,
            size=1.0,
            r=-0.4,
            mae_r=-0.5,
            mfe_r=0.5,
            session="NY",
            news_flag=False,
            rationale="synthetic dry-run sample",
            win_loss="loss",
            chain_id="sample-chain-004",
            tags=("sample",),
        ),
    )
