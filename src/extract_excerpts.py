import csv
import re
from pathlib import Path
from typing import Any, Dict, List


INPUT_PATH = Path("data/cleaned_reviews.csv")
OUTPUT_PATH = Path("data/review_excerpts.csv")

MIN_EXCERPT_LENGTH = 25
MAX_EXCERPT_LENGTH = 500


WORKLOAD_KEYWORDS = [
    "project",
    "projects",
    "exam",
    "exams",
    "midterm",
    "midterms",
    "final",
    "finals",
    "quiz",
    "quizzes",
    "homework",
    "assignment",
    "assignments",
    "worksheet",
    "worksheets",
    "lab",
    "labs",
    "workload",
    "time",
    "hours",
    "study",
    "studying",
    "hard",
    "difficult",
    "challenging",
    "stress",
    "stressful",
    "start early",
    "self study",
    "self-studying",
    "teach yourself",
    "grading",
    "graded",
    "curve",
    "curved",
    "unfair",
    "disorganized",
    "unclear",
    "confusing",
    "fast paced",
    "fast-paced",
    "lecture",
    "lectures",
]
