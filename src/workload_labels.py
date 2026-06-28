"""
Workload label schema for TerpLoad.

This file defines the first set of workload labels that the NLP model
should try to predict from course-related text.
"""

WORKLOAD_LABELS = {
    "project_heavy": "Large, frequent, or time-consuming projects.",
    "exam_heavy": "Difficult exams, many exams, or high exam pressure.",
    "homework_heavy": "Heavy homework or frequent assignments.",
    "time_consuming": "High weekly time commitment.",
}


def get_workload_labels():
    """Return all supported workload labels."""
    return list(WORKLOAD_LABELS.keys())


def describe_label(label):
    """Return the description for one workload label."""
    return WORKLOAD_LABELS.get(label, "Unknown label")


if __name__ == "__main__":
    print("TerpLoad workload labels:")
    for label, description in WORKLOAD_LABELS.items():
        print(f"- {label}: {description}")