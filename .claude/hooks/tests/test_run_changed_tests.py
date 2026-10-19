from run_changed_tests import tests_for as select_tests


def test_maps_source_to_tests(tmp_path):
    (tmp_path / "api" / "tests").mkdir(parents=True)
    (tmp_path / "api" / "tests" / "test_fitment.py").write_text("")
    assert select_tests(tmp_path, ["api/src/fitment/repo/fitment.py"]) == [
        "api/tests/test_fitment.py"
    ]
    assert select_tests(tmp_path, ["api/src/fitment/config.py"]) == []
