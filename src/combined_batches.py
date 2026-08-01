"""Combine completed weak-label CSV batches into one training file."""
import argparse
import csv
from pathlib import Path
from typing import Dict, List


INPUT_DIR = Path("data/labeling_batches")
OUTPUT_PATH = Path("data/weakly_labeled_reviews_full.csv")


def find_labeled_files(input_dir: Path) -> List[Path]:
    patterns = [
        "terpload_labeled_batch_*.csv",
        "weak_label_batch_*.csv",
        "weak_label_batch_*_labeled.csv",
        "labeled_batch_*.csv",
    ]

    files: List[Path] = []

    for pattern in patterns:
        files.extend(input_dir.glob(pattern))

    return sorted(set(files))


def load_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    files = find_labeled_files(args.input_dir)

    if not files:
        raise FileNotFoundError(
            f"No labeled batch files found in {args.input_dir}."
        )

    all_rows: List[Dict[str, str]] = []
    fieldnames: List[str] = []

    for path in files:
        rows = load_rows(path)
        print(f"Loaded {len(rows)} rows from {path}")

        if rows and not fieldnames:
            fieldnames = list(rows[0].keys())

        all_rows.extend(rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()