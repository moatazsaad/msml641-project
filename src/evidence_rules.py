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
  
  