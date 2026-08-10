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
