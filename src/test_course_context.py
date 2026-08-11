from course_context import build_course_context


def test_course_context_zero_reviews():
    result = build_course_context("CMSC216", 0)

    assert result["course_code"] == "CMSC216"
    assert result["review_count"] == 0
    assert result["evidence_status"]["evidence_level"] == "none"
    assert result["evidence_status"]["can_show_workload_signals"] is False
    assert result["grade_context"] is not None


def test_course_context_low_reviews():
    result = build_course_context("CMSC216", 5)

    assert result["evidence_status"]["evidence_level"] == "low"
    assert result["evidence_status"]["can_show_workload_signals"] is True
    assert result["evidence_status"]["show_low_evidence_warning"] is True
    assert result["grade_context"] is not None


def test_course_context_enough_reviews():
    result = build_course_context("CMSC216", 20)

    assert result["evidence_status"]["evidence_level"] == "enough"
    assert result["evidence_status"]["can_show_workload_signals"] is True
    assert result["evidence_status"]["show_low_evidence_warning"] is False
    assert result["grade_context"] is not None