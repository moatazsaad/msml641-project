"""Split reviews_to_weak_label.csv into smaller LLM labeling batches."""
import argparse
import csv
from pathlib import Path
from typing import Dict, List


INPUT_PATH = Path("data/reviews_to_weak_label.csv")
OUTPUT_DIR = Path("data/labeling_batches")


def load_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_batch(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    output_path: Path,
) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    rows = load_rows(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not rows:
        print("No rows to split.")
        return

    fieldnames = list(rows[0].keys())

    for index in range(0, len(rows), args.batch_size):
        batch_number = index // args.batch_size + 1
        batch_rows = rows[index : index + args.batch_size]
        output_path = args.output_dir / f"weak_label_batch_{batch_number:02d}.csv"
        write_batch(batch_rows, fieldnames, output_path)


if __name__ == "__main__":
    main()