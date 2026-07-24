from validation.run_st_c2_gbp_existence import build_report


def test_existence_signal_reproduction():
    build_report()
    text = open("reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md", encoding="utf-8").read()
    assert "**SIGNAL_FOUND**" in text
    assert "First signal time: `2026-06-10 17:15`" in text
    assert "Direction: `short`" in text
