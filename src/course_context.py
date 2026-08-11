from evidence_rules import build_evidence_status
from planetterp_client import get_grade_context


def build_course_context(course_code, review_count):
    grade_context = get_grade_context(course_code)

    evidence_status = build_evidence_status(
        review_count=review_count,
        grade_data_available=grade_context is not None,
    )

    return {
        "course_code": course_code,
        "review_count": review_count,
        "evidence_status": evidence_status,
        "grade_context": grade_context,
    }