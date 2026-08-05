import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    hamming_loss,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline


LABELS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
]

TRAIN_PATH = Path("data/splits/train.csv")
VAL_PATH = Path("data/splits/val.csv")
TEST_PATH = Path("data/splits/test.csv")

RESULTS_DIR = Path("results")


N_FOLDS = 5
RANDOM_STATE = 42

# Validation thresholds tested for each label.
THRESHOLD_CANDIDATES = np.arange(0.10, 0.91, 0.05)


def validate_split(df: pd.DataFrame, split_name: str) -> None:
    """Validate required text and label columns for one dataset split."""
    required_columns = {"review_text", *LABELS}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{split_name} is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError(f"{split_name} is empty.")

    for label in LABELS:
        values = set(df[label].dropna().unique())

        if not values.issubset({0, 1}):
            raise ValueError(
                f"{split_name}.{label} contains nonbinary values: "
                f"{sorted(values)}"
            )


def build_pipeline() -> Pipeline:
    """Create a fresh TF-IDF and logistic-regression pipeline."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def binary_metrics(
    truths: np.ndarray,
    predictions: np.ndarray,
) -> dict:
    """Calculate binary classification metrics for one label."""
    return {
        "accuracy": float(accuracy_score(truths, predictions)),
        "precision": float(
            precision_score(
                truths,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                truths,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                truths,
                predictions,
                zero_division=0,
            )
        ),
        "support": int(np.sum(truths)),
        "total": int(len(truths)),
    }


def select_threshold(
    truths: np.ndarray,
    probabilities: np.ndarray,
) -> tuple[float, dict]:
    """
    Select the validation threshold with the highest F1.

    Ties are broken by:
    1. Higher recall
    2. Threshold closer to 0.5
    """
    best_threshold = 0.5
    best_metrics = None
    best_rank = None

    for candidate in THRESHOLD_CANDIDATES:
        predictions = (probabilities >= candidate).astype(int)
        candidate_metrics = binary_metrics(truths, predictions)

        rank = (
            candidate_metrics["f1"],
            candidate_metrics["recall"],
            -abs(float(candidate) - 0.5),
        )

        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_threshold = float(round(candidate, 2))
            best_metrics = candidate_metrics

    if best_metrics is None:
        raise RuntimeError("Threshold selection did not produce a result.")

    return best_threshold, best_metrics


def metadata_frame(test_df: pd.DataFrame) -> pd.DataFrame:
    """Preserve useful metadata in the test prediction output."""
    preferred_columns = [
        "review_id",
        "course",
        "professor",
        "year",
        "rating",
        "review_text",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in test_df.columns
    ]

    return test_df[available_columns].reset_index(drop=True).copy()


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    validate_split(train_df, "train")
    validate_split(val_df, "validation")
    validate_split(test_df, "test")

    train_texts = train_df["review_text"].fillna("").astype(str)
    val_texts = val_df["review_text"].fillna("").astype(str)
    test_texts = test_df["review_text"].fillna("").astype(str)

    predictions_df = metadata_frame(test_df)

    metrics: dict = {}
    thresholds: dict = {}

    models = {}

    all_test_truths = []
    all_test_predictions = []

    for label in LABELS:
        print(f"\nProcessing {label}...")

        train_y = train_df[label].astype(int).to_numpy()
        val_y = val_df[label].astype(int).to_numpy()
        test_y = test_df[label].astype(int).to_numpy()

        positive_count = int(train_y.sum())
        negative_count = int(len(train_y) - positive_count)

        if positive_count < N_FOLDS or negative_count < N_FOLDS:
            raise ValueError(
                f"{label} does not have enough examples in both classes "
                f"for {N_FOLDS}-fold stratified CV. "
                f"Positive={positive_count}, negative={negative_count}."
            )

        pipeline = build_pipeline()

        # Cross-validation is performed only on the training split.
        # Every training review receives one out-of-fold prediction from a
        # model that did not train on that review.
        cv = StratifiedKFold(
            n_splits=N_FOLDS,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        cv_probabilities = cross_val_predict(
            pipeline,
            train_texts,
            train_y,
            cv=cv,
            method="predict_proba",
            n_jobs=-1,
        )[:, 1]

        # CV uses 0.5 because threshold selection belongs to validation.
        cv_predictions = (cv_probabilities >= 0.5).astype(int)
        train_cv_metrics = binary_metrics(train_y, cv_predictions)

        # Train one final candidate model on the full training split.
        pipeline.fit(train_texts, train_y)

        models[label] = pipeline

        # Use validation only to select the label-specific threshold.
        val_probabilities = pipeline.predict_proba(val_texts)[:, 1]

        selected_threshold, validation_metrics = select_threshold(
            val_y,
            val_probabilities,
        )

        # Evaluate once on the untouched test split.
        test_probabilities = pipeline.predict_proba(test_texts)[:, 1]
        test_predictions = (
            test_probabilities >= selected_threshold
        ).astype(int)

        test_metrics = binary_metrics(test_y, test_predictions)

        thresholds[label] = selected_threshold

        metrics[label] = {
            "train_cv": {
                "folds": N_FOLDS,
                "threshold": 0.5,
                **train_cv_metrics,
            },
            "selected_threshold": selected_threshold,
            "validation": validation_metrics,
            "test": test_metrics,
        }

        predictions_df[f"{label}_true"] = test_y
        predictions_df[f"{label}_probability"] = test_probabilities
        predictions_df[f"{label}_pred"] = test_predictions

        all_test_truths.append(test_y)
        all_test_predictions.append(test_predictions)



        print(
            f"  CV F1: {train_cv_metrics['f1']:.4f}\n"
            f"  Threshold: {selected_threshold:.2f}\n"
            f"  Validation F1: {validation_metrics['f1']:.4f}\n"
            f"  Test F1: {test_metrics['f1']:.4f}"
        )

    # Convert from four lists of length N to an N x 4 matrix.
    test_truth_matrix = np.column_stack(all_test_truths)
    test_prediction_matrix = np.column_stack(all_test_predictions)

    metrics["overall_test"] = {
        "macro_f1": float(
            f1_score(
                test_truth_matrix,
                test_prediction_matrix,
                average="macro",
                zero_division=0,
            )
        ),
        "micro_f1": float(
            f1_score(
                test_truth_matrix,
                test_prediction_matrix,
                average="micro",
                zero_division=0,
            )
        ),
        "subset_accuracy": float(
            accuracy_score(
                test_truth_matrix,
                test_prediction_matrix,
            )
        ),
        "hamming_loss": float(
            hamming_loss(
                test_truth_matrix,
                test_prediction_matrix,
            )
        ),
        "test_rows": int(len(test_df)),
    }

    joblib.dump(
        models,
        RESULTS_DIR / "tfidf_models.joblib",
    )

    predictions_df.to_csv(
        RESULTS_DIR / "tfidf_predictions.csv",
        index=False,
    )

    with open(
        RESULTS_DIR / "tfidf_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metrics, file, indent=4)

    with open(
        RESULTS_DIR / "tfidf_thresholds.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(thresholds, file, indent=4)

    print("\nOverall held-out test metrics:")
    print(json.dumps(metrics["overall_test"], indent=2))
    print("\nFinished.")


if __name__ == "__main__":
    main()