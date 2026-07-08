import csv
import json
from pathlib import Path
from typing import Any, Dict, List


PILOT_CSV_PATH = Path("data/labeling_pilot_reviews_week06.csv")
LABELS_JSON_PATH = Path("data/llm_labels_pilot.json")
OUTPUT_CSV_PATH = Path("data/llm_labeled_week06.csv")


LABEL_FIELDS = [
    "relevant_to_workload_or_risk",
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
    "self_learning_required",
    "harsh_grading",
    "disorganized_course",
    "confidence",
    "notes",
]


def load_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV file: {path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def load_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSON file: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("The JSON file must contain a list of label objects.")

    return data


def merge_rows(
    review_rows: List[Dict[str, Any]],
    label_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    labels_by_review_id = {
        row["review_id"]: row
        for row in label_rows
        if row.get("review_id")
    }

    merged_rows = []
    missing_ids = []

    for review in review_rows:
        review_id = review.get("review_id", "")
        label_data = labels_by_review_id.get(review_id)

        if label_data is None:
            missing_ids.append(review_id)
            continue

        merged_row = review.copy()

        for field in LABEL_FIELDS:
            merged_row[field] = label_data.get(field, "")

        merged_row["audit_status"] = ""
        merged_row["audited_by"] = ""
        merged_row["audit_notes"] = ""

        merged_rows.append(merged_row)

    if missing_ids:
        print("Warning: no labels found for:")
        for review_id in missing_ids:
            print(f"  - {review_id}")

    return merged_rows


def write_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    if not rows:
        raise ValueError("No merged rows were created.")

    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys())

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    review_rows = load_csv(PILOT_CSV_PATH)
    label_rows = load_json(LABELS_JSON_PATH)

    merged_rows = merge_rows(review_rows, label_rows)
    write_csv(merged_rows, OUTPUT_CSV_PATH)

    print(f"Pilot reviews loaded: {len(review_rows)}")
    print(f"LLM label rows loaded: {len(label_rows)}")
    print(f"Merged rows written: {len(merged_rows)}")
    print(f"Output: {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()