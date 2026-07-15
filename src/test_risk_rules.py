from risk_rules import estimate_schedule_risk


def test_empty_schedule_is_low_risk():
    # Call function with an empty list like a student who hasn't entered any courses yet
    result = estimate_schedule_risk([])

    # estimate_schedule_risk() returns a dict with 3 keys:
    # If the value doesn't match, Python raises an error and the test fails
    assert result["risk_level"] == "Low"      # no courses -> lowest label
    assert result["risk_score"] == 0          # no courses -> 0 points added
    assert result["reasons"] == []            # nothing to explain so empty list


def test_course_with_no_heavy_flags_is_low_risk():
    # This test checks a course with no workload labels.
    # Since there is no project_heavy, exam_heavy, homework_heavy, or time_consuming, the risk score should stay 0
    courses = [{"course_code": "EASY100"}]

    result = estimate_schedule_risk(courses)

    assert result["risk_level"] == "Low"      # nothing heavy -> Low
    assert result["risk_score"] == 0          # nothing heavy -> 0 points


def test_single_course_hits_medium_boundary_exactly():
    # This test checks the minimum score needed for Medium risk.
    # project_heavy adds 2 points.
    # exam_heavy adds 2 points.
    # Total score should be 4.
    courses = [
        {
            "course_code": "CMSC330",   
            "project_heavy": True,      # adds +2 
            "exam_heavy": True,         # adds +2 
        }
    ]

    result = estimate_schedule_risk(courses)

    assert result["risk_score"] == 4          
    assert result["risk_level"] == "Medium"   # 4 should map to Medium not Low


def test_three_exam_heavy_courses_hit_high_boundary_exactly():
    # This test checks the minimum score needed for High risk
    # Each exam-heavy course adds 2 points
    # Three exam-heavy courses = 6 points
    # Because there are 2 or more exam-heavy courses, the schedule gets a +2 bonus
    # Total score = 8
    # Since High starts at 8, the risk level should be High
    courses = [
        {"course_code": "A", "exam_heavy": True},
        {"course_code": "B", "exam_heavy": True},
        {"course_code": "C", "exam_heavy": True},
    ]

    result = estimate_schedule_risk(courses)

    assert result["risk_score"] == 8          
    assert result["risk_level"] == "High"     

    # The reasons should explain that multiple exam-heavy courses increase pressure
    assert any(
        "exam-heavy" in reason.lower() for reason in result["reasons"]
    )


def test_four_or_more_courses_alone_does_not_force_high_risk():
    # This test checks that 4 courses alone does not mean High risk
    # Since none of the courses has heavy workload labels, the only added point should be the small 4-course schedule point
    courses = [
        {"course_code": "A"},
        {"course_code": "B"},
        {"course_code": "C"},
        {"course_code": "D"},
    ]

    result = estimate_schedule_risk(courses)

    assert result["risk_score"] == 1          # only the "4+ courses" point
    assert result["risk_level"] == "Low"      # 1 point is still Low


# main() loops over this list
TESTS = [
    test_empty_schedule_is_low_risk,
    test_course_with_no_heavy_flags_is_low_risk,
    test_single_course_hits_medium_boundary_exactly,
    test_three_exam_heavy_courses_hit_high_boundary_exactly,
    test_four_or_more_courses_alone_does_not_force_high_risk,
]


def main():
    passed = 0   
    failed = 0   

    for test in TESTS:               
        try:
            # Run one test. If all assert checks pass, the test passed
            test()                   
            print(f"[PASS] {test.__name__}")   
            passed += 1
        except AssertionError as error:
            # If any assert fails, mark this test as failed but keep running the rest
            print(f"[FAIL] {test.__name__}: {error}")
            failed += 1
    # Print the final test summary
    print(f"\n{passed} passed, {failed} failed")

if __name__ == "__main__":
    main()
