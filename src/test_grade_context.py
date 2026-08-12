from grade_context import aggregate_grade_rows


def test_no_grade_rows():
    assert aggregate_grade_rows([]) is None


def test_grade_aggregation():
    rows = [
        {
            "A+": 2,
            "A": 8,
            "A-": 0,
            "B+": 0,
            "B": 5,
            "B-": 0,
            "C+": 0,
            "C": 3,
            "C-": 0,
            "D+": 0,
            "D": 1,
            "D-": 0,
            "F": 1,
            "W": 0,
        }
    ]

    result = aggregate_grade_rows(rows)

    assert result["total_grade_records"] == 20
    assert result["a_range_rate"] == 0.50
    assert result["b_range_rate"] == 0.25
    assert result["c_range_rate"] == 0.15
    assert result["d_range_rate"] == 0.05
    assert result["f_rate"] == 0.05
    assert result["withdrawal_rate"] == 0.0


def test_multiple_grade_rows_are_combined():
    rows = [
        {
            "A": 10,
            "B": 5,
            "C": 0,
            "D": 0,
            "F": 0,
            "W": 0,
        },
        {
            "A": 10,
            "B": 5,
            "C": 0,
            "D": 0,
            "F": 0,
            "W": 0,
        },
    ]

    result = aggregate_grade_rows(rows)

    assert result["total_grade_records"] == 30
    assert result["distribution"]["A"] == 20
    assert result["distribution"]["B"] == 10