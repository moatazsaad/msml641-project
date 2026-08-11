import pandas as pd

from predict_course_signals import aggregate_course_signals


def test_below_threshold_is_false():
    reviews_df = pd.DataFrame([
        {"review_id": "r1", "course_id": "CMSC216"},
        {"review_id": "r2", "course_id": "CMSC216"},
        {"review_id": "r3", "course_id": "CMSC216"},
        {"review_id": "r4", "course_id": "CMSC216"},
        {"review_id": "r5", "course_id": "CMSC216"},
        {"review_id": "r6", "course_id": "CMSC216"},
        {"review_id": "r7", "course_id": "CMSC216"},
        {"review_id": "r8", "course_id": "CMSC216"},
        {"review_id": "r9", "course_id": "CMSC216"},
        {"review_id": "r10", "course_id": "CMSC216"},
    ])

    predictions = {
        "project_heavy": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "exam_heavy": [0] * 10,
        "homework_heavy": [0] * 10,
        "time_consuming": [0] * 10,
    }

    labeled_df = pd.DataFrame(
        columns=[
            "review_id",
            "project_heavy",
            "exam_heavy",
            "homework_heavy",
            "time_consuming",
        ]
    )

    result = aggregate_course_signals(
        reviews_df,
        predictions,
        labeled_df,
    )

    course = result["CMSC216"]

    assert course["project_heavy_positive_rate"] == 0.20
    assert course["project_heavy"] is False
def test_exact_threshold_is_true():
    reviews_df = pd.DataFrame([
        {"review_id": f"r{i}", "course_id": "CMSC216"}
        for i in range(1, 11)
    ])

    predictions = {
        "project_heavy": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        "exam_heavy": [0] * 10,
        "homework_heavy": [0] * 10,
        "time_consuming": [0] * 10,
    }

    labeled_df = pd.DataFrame(
        columns=[
            "review_id",
            "project_heavy",
            "exam_heavy",
            "homework_heavy",
            "time_consuming",
        ]
    )

    result = aggregate_course_signals(
        reviews_df,
        predictions,
        labeled_df,
    )

    course = result["CMSC216"]

    assert course["project_heavy_positive_rate"] == 0.30
    assert course["project_heavy"] is True
def test_above_threshold_is_true():
    reviews_df = pd.DataFrame([
        {"review_id": f"r{i}", "course_id": "CMSC216"}
        for i in range(1, 11)
    ])

    predictions = {
        "project_heavy": [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        "exam_heavy": [0] * 10,
        "homework_heavy": [0] * 10,
        "time_consuming": [0] * 10,
    }

    labeled_df = pd.DataFrame(
        columns=[
            "review_id",
            "project_heavy",
            "exam_heavy",
            "homework_heavy",
            "time_consuming",
        ]
    )

    result = aggregate_course_signals(
        reviews_df,
        predictions,
        labeled_df,
    )

    course = result["CMSC216"]

    assert course["project_heavy_positive_rate"] == 0.40
    assert course["project_heavy"] is True