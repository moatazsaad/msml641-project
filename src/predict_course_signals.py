"""
Predict per-course workload signals using the trained TF-IDF classifier.

Trains one TF-IDF + LogisticRegression classifier per workload label on all
labeled reviews (data/weakly-labeled-week08.csv), then applies it to the
real reviews TerpLoad has collected (data/cleaned_reviews.csv). Predictions
are averaged per course so the CLI report can use real data instead of the
hardcoded sample signals.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from workload_labels import WORKLOAD_LABELS

LABELED_DATA_PATH = Path("data/weakly-labeled-week08.csv")
REVIEWS_PATH = Path("data/cleaned_reviews.csv")
OUTPUT_PATH = Path("data/course_workload_signals.json")

# A course is marked True for a label once at least this share of its
# reviews are predicted positive for that label.
POSITIVE_LABEL_THRESHOLD = 0.3


def train_label_classifiers(labeled_df):
    """Fit one TF-IDF + LogisticRegression pipeline per workload label."""

    classifiers = {}

    for label in WORKLOAD_LABELS:
        # class_weight="balanced" matters here: project_heavy and
        # homework_heavy only have ~15% positive examples in the labeled
        # set, so an unweighted model just predicts "no" for every course.
        pipe = Pipeline(
            [
                ("tfidf", TfidfVectorizer(stop_words="english")),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                    ),
                ),
            ]
        )
        pipe.fit(
            labeled_df["review_text"].fillna(""),
            labeled_df[label].astype(int),
        )
        classifiers[label] = pipe

    return classifiers


def predict_review_labels(classifiers, review_texts):
    """Return {label: [0/1, ...]} predictions for a list of review texts."""

    return {
        label: pipe.predict(review_texts)
        for label, pipe in classifiers.items()
    }


def aggregate_course_signals(reviews_df, predictions):
    """Turn per-review predictions into per-course workload signals."""

    reviews_df = reviews_df.copy()

    for label, preds in predictions.items():
        reviews_df[label] = preds

    course_signals = {}

    for course_id, group in reviews_df.groupby("course_id"):
        signals = {
            "course_code": course_id,
            "review_count": int(len(group)),
        }

        for label in WORKLOAD_LABELS:
            positive_rate = group[label].mean()
            signals[label] = bool(positive_rate >= POSITIVE_LABEL_THRESHOLD)
            signals[f"{label}_positive_rate"] = round(float(positive_rate), 3)

        course_signals[course_id] = signals

    return course_signals


def write_course_signals(course_signals, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(course_signals, file, indent=2)


def main():
    labeled_df = pd.read_csv(LABELED_DATA_PATH)
    reviews_df = pd.read_csv(REVIEWS_PATH)

    classifiers = train_label_classifiers(labeled_df)
    predictions = predict_review_labels(
        classifiers,
        reviews_df["review_text"].fillna(""),
    )
    course_signals = aggregate_course_signals(reviews_df, predictions)

    write_course_signals(course_signals, OUTPUT_PATH)

    print(
        f"[done] Wrote workload signals for {len(course_signals)} courses "
        f"to {OUTPUT_PATH}"
    )

    for course_id, signals in sorted(course_signals.items()):
        label_summary = ", ".join(
            f"{label}={signals[label]}" for label in WORKLOAD_LABELS
        )
        print(f"{course_id} ({signals['review_count']} reviews): {label_summary}")


if __name__ == "__main__":
    main()
