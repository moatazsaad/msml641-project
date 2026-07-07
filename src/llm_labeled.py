import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List

PILOT_BATCH_SIZE = 30
RANDOM_SEED = 42

def load_csv_rows(path: Path) -> List[Dict[str, Any]]:
  """Load rows from a CSV file."""

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
  if not rows:
        raise ValueError("No review excerpts were found.")

  random.seed(RANDOM_SEED)

  if batch_size >= len(rows):
      return rows.copy()

  return random.sample(rows, batch_size)

#need main