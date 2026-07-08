import csv
import random
from pathlib import Path
from typing import Any, Dict, List


INPUT_PATH = Path("data/cleaned_reviews.csv")
PILOT_OUTPUT_PATH = Path("data/labeling_pilot_reviews_week06.csv")

PILOT_BATCH_SIZE = 30
RANDOM_SEED = 42

LABEL_FIELDS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
    "self_learning_required",
    "harsh_grading",
    "disorganized_course",
    "evidence_excerpt",
    "confidence",
    "notes",
]

def load_csv_rows(path: Path) -> List[Dict[str, Any]]:
    """Load cleaned review rows from CSV."""

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def select_pilot_batch(
    rows: List[Dict[str, Any]],
    batch_size: int,
) -> List[Dict[str, Any]]:
    """Select a reproducible random pilot batch."""

    if not rows:
        raise ValueError("No cleaned reviews were found.")

    random.seed(RANDOM_SEED)

    if batch_size >= len(rows):
        return rows.copy()

    return random.sample(rows, batch_size)


def write_pilot_csv(
    rows: List[Dict[str, Any]],
    path: Path,
) -> None:
    """Write selected full reviews to a pilot-labeling CSV."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
      "review_id",
      "course_id",
      "professor",
      "review_text",
      "rating",
      "date",
      "review_year",
      "is_recent",
      "evidence_weight",
      "source",
    ]+ LABEL_FIELDS

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    field: row.get(field, "")
                    for field in fieldnames
                }
            )


def main() -> None:
    rows = load_csv_rows(INPUT_PATH)

    pilot_batch = select_pilot_batch(
        rows,
        PILOT_BATCH_SIZE,
    )

    write_pilot_csv(
        pilot_batch,
        PILOT_OUTPUT_PATH,
    )

    print(f"Loaded {len(rows)} cleaned reviews")
    print(
        f"Wrote {len(pilot_batch)} pilot reviews "
        f"to {PILOT_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()