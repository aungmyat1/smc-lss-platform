from __future__ import annotations

import lzma
import struct
from datetime import UTC, datetime

from tools.st_c3_verify_dukascopy_provider import _minute_bid_bars, _minute_gap_count, _parse_bi5_ticks


def _record(ms: int, ask: int, bid: int) -> bytes:
    return struct.pack(">IIIff", ms, ask, bid, 1.0, 2.0)


def test_dukascopy_bi5_parser_decodes_ticks_to_utc_prices():
    payload = lzma.compress(_record(1_000, 110001, 109999) + _record(61_000, 110011, 110009))

    ticks = _parse_bi5_ticks(payload, datetime(2024, 1, 2, 0, tzinfo=UTC), "EURUSD")

    assert ticks[0].timestamp == datetime(2024, 1, 2, 0, 0, 1, tzinfo=UTC)
    assert ticks[0].ask == 1.10001
    assert ticks[0].bid == 1.09999
    assert ticks[1].timestamp == datetime(2024, 1, 2, 0, 1, 1, tzinfo=UTC)


def test_dukascopy_minute_bars_and_gap_count_are_deterministic():
    payload = lzma.compress(
        _record(1_000, 110001, 110000)
        + _record(2_000, 110011, 110010)
        + _record(61_000, 110021, 110020)
    )
    hour = datetime(2024, 1, 2, 0, tzinfo=UTC)
    ticks = _parse_bi5_ticks(payload, hour, "EURUSD")

    bars = _minute_bid_bars(ticks)

    assert list(bars) == [datetime(2024, 1, 2, 0, 0, tzinfo=UTC), datetime(2024, 1, 2, 0, 1, tzinfo=UTC)]
    assert bars[datetime(2024, 1, 2, 0, 0, tzinfo=UTC)]["open"] == 1.1
    assert bars[datetime(2024, 1, 2, 0, 0, tzinfo=UTC)]["high"] == 1.1001
    assert _minute_gap_count(bars, hour) == 58
