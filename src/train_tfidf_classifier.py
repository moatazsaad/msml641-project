"""
TF-IDF workload classifier.

Skeleton training script for predicting workload labels from
course review text.

Future work:
- Load labeled review dataset
- Train one classifier per workload label
- Save trained models


These are the exact input columns needed for training:
review_text          (string)
project_heavy        (0/1)
exam_heavy           (0/1)
homework_heavy       (0/1)
time_consuming       (0/1)
"""

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def load_dataset(csv_path):
    return pd.read_csv(csv_path)


def train_single_label(df, label):
    X_train, X_test, y_train, y_test = train_test_split(
        df["review_text"],
        df[label],
        test_size=0.2,
        random_state=42,
    )

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(stop_words="english")),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print(f"\n===== {label} =====")
    print(classification_report(y_test, predictions))

    return model


def main():
    csv_path = "data/labeled_reviews.csv"

    df = load_dataset(csv_path)

    labels = [
        "project_heavy",
        "exam_heavy",
        "homework_heavy",
        "time_consuming",
    ]

    trained_models = {}

    for label in labels:
        trained_models[label] = train_single_label(df, label)

    print("\nTraining complete.")


if __name__ == "__main__":
    main()
