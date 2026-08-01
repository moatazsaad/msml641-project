"""
Prepare a balanced review set for weak labeling.

This samples from cleaned PlanetTerp reviews and writes rows with empty label
columns that can be completed by an LLM labeling prompt.
"""
import argparse
import csv
from pathlib import Path
from typing import Dict, List, Set


INPUT_PATH = Path("data/cleaned_reviews.csv")
OUTPUT_PATH = Path("data/reviews_to_weak_label.csv")
EXISTING_LABEL_PATHS = [
    Path("data/weakly-labeled-week08.csv"),
    Path("data/weakly_labeled_reviews_full.csv"),
]

ORIGINAL_COLUMNS = [
    "review_id",
    "course",
    "professor",
    "year",
    "rating",
    "review_text",
]

LABEL_COLUMNS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
    "self_learning_required",
    "harsh_grading",
    "disorganized_course",
    "fair_but_strict",
    "evidence_snippet",
    "label_rationale",
]