from validation.st_c2.golden_cases import case_ids, load_cases, validate_manifest


def test_golden_case_manifest_validates():
    assert validate_manifest() == []


def test_required_initial_golden_cases_exist():
    expected = {
        "GC-STC2-GBPUSD-CONFIG-001",
        "GC-STC2-GBPUSD-BULL-POS-001",
        "GC-STC2-GBPUSD-BEAR-POS-001",
        "GC-STC2-GBPUSD-LIQ-NEG-001",
        "GC-STC2-GBPUSD-CUTOFF-001",
        "GC-STC2-GBPUSD-DETERMINISM-001",
        "GC-STC2-GBPUSD-POINTS-BOUNDARY-001",
        "GC-STC2-GBPUSD-ID-STABILITY-001",
    }
    assert expected <= case_ids()


def test_golden_fixture_loading():
    cases = {case.case_id: case for case in load_cases()}
    bull = cases["GC-STC2-GBPUSD-BULL-POS-001"]
    assert bull.expected_signal == {"decision": "SIGNAL", "direction": "long"}
    assert bull.fixture_paths == ("positive/bull_positive.json",)
