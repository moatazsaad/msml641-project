"""
predict_course_signals.py

Loads saved TF-IDF models and thresholds to generate course workload signals.
"""

import json
from pathlib import Path

import joblib
import pandas as pd

from workload_labels import WORKLOAD_LABELS

TRAIN_PATH = Path("data/splits/train.csv")
VAL_PATH = Path("data/splits/val.csv")
REVIEWS_PATH = Path("data/cleaned_reviews.csv")
OUTPUT_PATH = Path("data/course_workload_signals.json")

MODEL_PATH = Path("results/tfidf_models.joblib")
THRESHOLD_PATH = Path("results/tfidf_thresholds.json")

POSITIVE_LABEL_THRESHOLD = 0.30
LOW_EVIDENCE_REVIEW_THRESHOLD = 10


def load_models():
    models = joblib.load(MODEL_PATH)
    with THRESHOLD_PATH.open("r", encoding="utf-8") as f:
        thresholds = json.load(f)
    return models, thresholds


def predict_review_labels(models, thresholds, review_texts):
    review_texts = review_texts.fillna("").astype(str)
    predictions = {}
    for label in WORKLOAD_LABELS:
        probs = models[label].predict_proba(review_texts)[:, 1]
        predictions[label] = (probs >= thresholds[label]).astype(int)
    return predictions


def aggregate_course_signals(reviews_df, predictions, labeled_df):
    reviews_df = reviews_df.copy()

    for label, preds in predictions.items():
        reviews_df[label] = preds

    known = labeled_df.set_index("review_id")[list(WORKLOAD_LABELS)].astype(int)

    reviews_df = reviews_df.set_index("review_id")
    reviews_df.update(known)
    reviews_df = reviews_df.reset_index()

    course_signals = {}

    for course_id, group in reviews_df.groupby("course_id"):
        review_count = len(group)

        entry = {
            "course_code": course_id,
            "review_count": int(review_count),
            "low_evidence": review_count < LOW_EVIDENCE_REVIEW_THRESHOLD,
        }

        for label in WORKLOAD_LABELS:
            rate = group[label].mean()
            entry[label] = bool(rate >= POSITIVE_LABEL_THRESHOLD)
            entry[f"{label}_positive_rate"] = round(float(rate), 3)

        course_signals[course_id] = entry

    return course_signals


def write_course_signals(course_signals):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(course_signals, f, indent=2)


def main():
    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    labeled_df = pd.concat([train_df, val_df], ignore_index=True)

    reviews_df = pd.read_csv(REVIEWS_PATH)

    models, thresholds = load_models()

    predictions = predict_review_labels(
        models,
        thresholds,
        reviews_df["review_text"],
    )

    course_signals = aggregate_course_signals(
        reviews_df,
        predictions,
        labeled_df,
    )

    write_course_signals(course_signals)

    print(f"[done] Wrote workload signals for {len(course_signals)} courses to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()