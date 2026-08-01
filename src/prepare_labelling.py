"""
making a balanced review set for weak labeling and getting all the
PlanetTerp reviews and writes rows with empty label
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

def load_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def load_existing_review_ids() -> Set[str]:
    review_ids: Set[str] = set()

    for path in EXISTING_LABEL_PATHS:
        if not path.exists():
            continue

        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                review_id = row.get("review_id", "").strip()
                if review_id:
                    review_ids.add(review_id)

    return review_ids


def normalize_row(row: Dict[str, str]) -> Dict[str, str]:
    course = row.get("course", row.get("course_id", "")).strip().upper()
    year = row.get("year", row.get("review_year", "")).strip()

    return {
        "review_id": row.get("review_id", "").strip(),
        "course": course,
        "professor": row.get("professor", "").strip(),
        "year": year,
        "rating": row.get("rating", "").strip(),
        "review_text": row.get("review_text", "").strip(),
    }


def choose_balanced_rows(
    rows: List[Dict[str, str]],
    target_count: int,
    min_review_chars: int,
) -> List[Dict[str, str]]:
    existing_ids = load_existing_review_ids()
    normalized = [
        normalize_row(row)
        for row in rows
        if row.get("review_text", "").strip()
    ]

    candidates = [
        row
        for row in normalized
        if row["review_id"] not in existing_ids
        and len(row["review_text"]) >= min_review_chars
    ]

    by_course: Dict[str, List[Dict[str, str]]] = {}

    for row in candidates:
        by_course.setdefault(row["course"], []).append(row)

    for course_rows in by_course.values():
        course_rows.sort(
            key=lambda item: (
                item.get("year", ""),
                item.get("review_id", ""),
            ),
            reverse=True,
        )

    selected: List[Dict[str, str]] = []

    while len(selected) < target_count:
        added_in_round = False

        for course in sorted(by_course):
            if len(selected) >= target_count:
                break

            course_rows = by_course[course]
            if course_rows:
                selected.append(course_rows.pop(0))
                added_in_round = True

        if not added_in_round:
            break

    return selected


def write_rows(rows: List[Dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ORIGINAL_COLUMNS + LABEL_COLUMNS

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            output_row = {column: row.get(column, "") for column in ORIGINAL_COLUMNS}
            for column in LABEL_COLUMNS:
                output_row[column] = ""
            writer.writerow(output_row)

    print(f"Wrote {len(rows)} rows to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=500)
    parser.add_argument("--min-review-chars", type=int, default=80)
    args = parser.parse_args()

    rows = load_rows(INPUT_PATH)
    selected = choose_balanced_rows(
        rows,
        target_count=args.target,
        min_review_chars=args.min_review_chars,
    )
    write_rows(selected, OUTPUT_PATH)


if __name__ == "__main__":
    main()