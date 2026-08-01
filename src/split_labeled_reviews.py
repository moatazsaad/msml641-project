"""Create train/validation/test splits from weakly labeled reviews."""
import csv
import random
from pathlib import Path
from typing import Dict, List


INPUT_PATH = Path("data/weakly_labeled_reviews_full.csv")
OUTPUT_DIR = Path("data/splits")
RANDOM_SEED = 641

CORE_LABELS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
]


def load_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def normalize_label(value: str) -> str:
    value = str(value).strip()

    if value in {"0", "0.0"}:
        return "0"

    if value in {"1", "1.0"}:
        return "1"

    raise ValueError(f"Expected binary label, got {value!r}")


def validate_and_normalize(rows: List[Dict[str, str]]) -> None:
    for row in rows:
        for label in CORE_LABELS:
            row[label] = normalize_label(row.get(label, ""))


def write_rows(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def positive_counts(rows: List[Dict[str, str]]) -> Dict[str, int]:
    return {
        label: sum(1 for row in rows if row.get(label) == "1")
        for label in CORE_LABELS
    }


def main() -> None:
    rows = load_rows(INPUT_PATH)

    if not rows:
        raise ValueError(f"No rows found in {INPUT_PATH}")

    validate_and_normalize(rows)

    rng = random.Random(RANDOM_SEED)
    rows = list(rows)
    rng.shuffle(rows)

    total = len(rows)
    train_end = int(total * 0.70)
    val_end = train_end + int(total * 0.15)

    train_rows = rows[:train_end]
    val_rows = rows[train_end:val_end]
    test_rows = rows[val_end:]

    fieldnames = list(rows[0].keys())

    write_rows(OUTPUT_DIR / "train.csv", train_rows, fieldnames)
    write_rows(OUTPUT_DIR / "val.csv", val_rows, fieldnames)
    write_rows(OUTPUT_DIR / "test.csv", test_rows, fieldnames)

    print(f"Input rows: {total}")
    print(f"Train rows: {len(train_rows)}")
    print(f"Validation rows: {len(val_rows)}")
    print(f"Test rows: {len(test_rows)}")
    print("Positive label counts:")
    print(f"- train: {positive_counts(train_rows)}")
    print(f"- val: {positive_counts(val_rows)}")
    print(f"- test: {positive_counts(test_rows)}")


if __name__ == "__main__":
    main()