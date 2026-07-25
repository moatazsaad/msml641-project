from pathlib import Path

from simple_report_cli import (
    build_course_inputs,
    load_course_signals,
    parse_courses,
)

# Small fake signals dict so these tests don't depend on the real,
# model-generated data/course_workload_signals.json file.
FAKE_COURSE_SIGNALS = {
    "CMSC330": {
        "course_code": "CMSC330",
        "project_heavy": True,
        "exam_heavy": False,
        "homework_heavy": False,
        "time_consuming": True,
    },
}


def test_parse_courses_splits_trims_and_upper_cases():
    result = parse_courses(" cmsc330,  cmsc351 ,stat400")

    assert result == ["CMSC330", "CMSC351", "STAT400"]


def test_parse_courses_ignores_empty_entries():
    result = parse_courses("CMSC330,, ,STAT400")

    assert result == ["CMSC330", "STAT400"]


def test_build_course_inputs_uses_known_signals():
    courses, courses_without_data = build_course_inputs(
        ["CMSC330"], FAKE_COURSE_SIGNALS
    )

    assert courses == [FAKE_COURSE_SIGNALS["CMSC330"]]
    assert courses_without_data == []


def test_build_course_inputs_flags_unknown_courses():
    courses, courses_without_data = build_course_inputs(
        ["MATH410"], FAKE_COURSE_SIGNALS
    )

    assert courses == [{"course_code": "MATH410"}]
    assert courses_without_data == ["MATH410"]


def test_load_course_signals_returns_empty_dict_when_file_missing():
    # A path that should never exist, so this doesn't depend on
    # data/course_workload_signals.json being present or up to date.
    missing_path = Path("data/does_not_exist_course_signals.json")

    result = load_course_signals(missing_path)

    assert result == {}


TESTS = [
    test_parse_courses_splits_trims_and_upper_cases,
    test_parse_courses_ignores_empty_entries,
    test_build_course_inputs_uses_known_signals,
    test_build_course_inputs_flags_unknown_courses,
    test_load_course_signals_returns_empty_dict_when_file_missing,
]


def main():
    passed = 0
    failed = 0

    for test in TESTS:
        try:
            test()
            print(f"[PASS] {test.__name__}")
            passed += 1
        except AssertionError as error:
            print(f"[FAIL] {test.__name__}: {error}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
