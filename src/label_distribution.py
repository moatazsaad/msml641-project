"""getting label distribution counts for the whole weakly labeled dataset"""
import csv
from pathlib import Path


INPUT_PATH = Path("data/weakly_labeled_reviews_full.csv")
OUTPUT_PATH = Path("results/label_distribution.csv")

LABELS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
    "self_learning_required",
    "harsh_grading",
    "disorganized_course",
    "fair_but_strict",
]


def normalize_binary(value: str) -> int:
    value = str(value).strip()

    if value in {"1", "1.0"}:
        return 1

    return 0


def main() -> None:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["label", "positive_count", "total_count", "positive_rate"],
        )
        writer.writeheader()

        for label in LABELS:
            positives = sum(normalize_binary(row.get(label, "0")) for row in rows)
            total = len(rows)
            writer.writerow(
                {
                    "label": label,
                    "positive_count": positives,
                    "total_count": total,
                    "positive_rate": round(positives / total, 4) if total else 0,
                }
            )

    print(f"Wrote label distribution to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()