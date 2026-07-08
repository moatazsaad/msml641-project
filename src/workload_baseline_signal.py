"""
Baseline workload signal extraction.

This module uses simple keyword matching to identify workload-related
signals from course review text. It serves as a baseline before replacing
the rules with a trained NLP classifier.
"""

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

    Parameters
    ----------
    text : str

    Returns
    -------
    dict
        Mapping from workload label to bool.
    """
    text = text.lower()

    predictions = {}

    for label, keywords in KEYWORDS.items():
        predictions[label] = any(keyword in text for keyword in keywords)

    return predictions


if __name__ == "__main__":
    review = """
    Weekly homework takes several hours.
    The semester project is difficult.
    Midterms are challenging.
    """

    print(predict_workload_signals(review))
