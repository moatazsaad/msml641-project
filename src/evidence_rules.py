"""
If there is low evidence, need to fallback and create logic for that.
"""
LOW_EVIDENCE_THRESHOLD = 10

def get_evidence_level(review_count: int) -> str:
    if review_count <= 0:
        return "none"

    if review_count < LOW_EVIDENCE_THRESHOLD:
        return "low"

    return "enough"

def should_show_grade_context(grade_data_available: bool) -> bool:
    return grade_data_available
  
def build_evidence_status(
    review_count: int,
    grade_data_available: bool,
) -> dict:
    evidence_level = get_evidence_level(review_count)

    if evidence_level == "none":
        return {
            "evidence_level": "none",
            "can_show_workload_signals": False,
            "show_low_evidence_warning": True,
            "show_grade_context": grade_data_available,
            "message": (
                "TerpLoad does not have enough review evidence "
                "to estimate workload for this course."
            ),
        }