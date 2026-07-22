"""
Baseline workload signal extraction.

This module uses simple keyword matching to identify workload-related
signals from course review text. It serves as a baseline before replacing
the rules with a trained NLP classifier.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from workload_labels import WORKLOAD_LABELS

KEYWORDS = {
    "project_heavy": [
        "project",
        "projects",
        "final project",
        "group project",
        "semester project",
    ],
    "exam_heavy": [
        "exam",
        "midterm",
        "final",
        "quiz",
        "tests",
    ],
    "homework_heavy": [
        "homework",
        "assignment",
        "assignments",
        "problem set",
        "weekly homework",
    ],
    "time_consuming": [
        "time consuming",
        "hours",
        "10 hours",
        "every week",
        "workload",
        "busy",
    ],
}


def predict_workload_signals(text):
    """
    Predict workload labels using simple keyword matching.
    """
    text = str(text).lower()

    predictions = {}

    for label, keywords in KEYWORDS.items():
        predictions[label] = any(keyword in text for keyword in keywords)

    return predictions


def evaluate_baseline(
    dataset_path="data\weakly-labeled-week08.csv",
):
    """
    Evaluate keyword baseline on the labeled dataset.
    """

    df = pd.read_csv(dataset_path)

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    metrics = {}

    prediction_df = df[["review_text"]].copy()

    for label in WORKLOAD_LABELS:

        y_true = df[label].astype(int)

        y_pred = (
            df["review_text"]
            .fillna("")
            .apply(lambda x: int(predict_workload_signals(x)[label]))
        )

        prediction_df[f"{label}_true"] = y_true
        prediction_df[f"{label}_pred"] = y_pred

        metrics[label] = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(
                precision_score(y_true, y_pred, zero_division=0)
            ),
            "recall": float(
                recall_score(y_true, y_pred, zero_division=0)
            ),
            "f1": float(
                f1_score(y_true, y_pred, zero_division=0)
            ),
        }

    prediction_df.to_csv(
        results_dir / "keyword_predictions.csv",
        index=False,
    )

    with open(
        results_dir / "keyword_baseline_metrics.json",
        "w",
    ) as f:
        json.dump(metrics, f, indent=4)

    print("\nKeyword Baseline Metrics\n")
    print(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    evaluate_baseline()
