"""
Predict per-course workload signals using the trained TF-IDF classifier.

Trains one TF-IDF classifier per workload label using the latest
training and validation splits, then applies the classifiers to the
current cleaned PlanetTerp review corpus.

For the reviews that already have a real (weak) label, that known label is
used instead of the model's own prediction when building course signals.
Without this, the model would be "predicting" on reviews it was directly
trained on, which would make the course signals look more confident than
the model actually is.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from workload_labels import WORKLOAD_LABELS


TRAIN_PATH = Path("data/splits/train.csv")
VAL_PATH = Path("data/splits/val.csv")
TEST_PATH = Path("data/splits/test.csv")

REVIEWS_PATH = Path("data/cleaned_reviews.csv")
OUTPUT_PATH = Path("data/course_workload_signals.json")
# A course is marked True for a label once at least this share of its
# reviews are predicted positive for that label.
POSITIVE_LABEL_THRESHOLD = 0.3

# Courses with fewer reviews than this are flagged as low evidence so the
# CLI report can warn students instead of presenting thin data as fact.
LOW_EVIDENCE_REVIEW_THRESHOLD = 10


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


def aggregate_course_signals(reviews_df, predictions, labeled_df):
    """Turn per-review predictions into per-course workload signals.

    Reviews that already have a real (weak) label use that label instead
    of the model's prediction - the model was trained on those exact
    reviews, so predicting on them again would just reproduce the
    training data instead of measuring anything new.
    """

    reviews_df = reviews_df.copy()

    for label, preds in predictions.items():
        reviews_df[label] = preds

    label_columns = list(WORKLOAD_LABELS)
    known_labels = labeled_df.set_index("review_id")[label_columns].astype(int)

    reviews_df = reviews_df.set_index("review_id")
    reviews_df.update(known_labels)
    reviews_df = reviews_df.reset_index()

    course_signals = {}

    for course_id, group in reviews_df.groupby("course_id"):
        review_count = len(group)
        signals = {
            "course_code": course_id,
            "review_count": int(review_count),
            "low_evidence": review_count < LOW_EVIDENCE_REVIEW_THRESHOLD,
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
    # Same columns, no overlapping review_id values, so a plain concat is safe.
    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    labeled_df = pd.concat(
    [train_df, val_df],
    ignore_index=True,
)
    reviews_df = pd.read_csv(REVIEWS_PATH)

    classifiers = train_label_classifiers(labeled_df)
    predictions = predict_review_labels(
        classifiers,
        reviews_df["review_text"].fillna(""),
    )
    course_signals = aggregate_course_signals(reviews_df, predictions, labeled_df)

    write_course_signals(course_signals, OUTPUT_PATH)

    print(
        f"[done] Wrote workload signals for {len(course_signals)} courses "
        f"to {OUTPUT_PATH}"
    )

    for course_id, signals in sorted(course_signals.items()):
        label_summary = ", ".join(
            f"{label}={signals[label]}" for label in WORKLOAD_LABELS
        )
        evidence_note = " [low evidence]" if signals["low_evidence"] else ""
        print(
            f"{course_id} ({signals['review_count']} reviews){evidence_note}: "
            f"{label_summary}"
        )


if __name__ == "__main__":
    main()
