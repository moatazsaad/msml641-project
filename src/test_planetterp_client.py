from planetterp_client import fetch_grades
from planetterp_client import fetch_grades, get_grade_context


def test_fetch_grades_real_course():
    rows = fetch_grades("CMSC216")

    assert isinstance(rows, list)


def test_get_grade_context_real_course():
    context = get_grade_context("CMSC216")
    print("\nGRADE CONTEXT:")
    print(context)
    assert context is not None
    assert context["total_grade_records"] > 0
    assert "a_range_rate" in context
    assert "f_rate" in context
    assert "withdrawal_rate" in context

