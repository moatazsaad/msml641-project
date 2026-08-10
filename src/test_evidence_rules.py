"""
need to test the evidence rules
"""

from evidence_rules import build_evidence_status

def test_zero_reviews():
    result = build_evidence_status(
        review_count=0,
        grade_data_available=True,
    )

    assert result["evidence_level"] == "none"
    assert result["can_show_workload_signals"] is False
    assert result["show_low_evidence_warning"] is True
    assert result["show_grade_context"] is True

def test_one_review():
    result = build_evidence_status(
        review_count=1,
        grade_data_available=True,
    )

    assert result["evidence_level"] == "low"
    assert result["can_show_workload_signals"] is True
    assert result["message"] == (
        "Limited evidence: this estimate is based on only 1 review."
    )
    
def test_multiple_low_reviews():
    result = build_evidence_status(
        review_count=4,
        grade_data_available=True,
    )

    assert result["evidence_level"] == "low"
    assert result["message"] == (
        "Limited evidence: this estimate is based on only 4 reviews."
    )
