import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any

INPUT_PATH = Path("data/raw_planetterp.csv")
OUTPUT_PATH = Path("data/cleaned_reviews.csv")


def normalize_whitespace(text: Any) -> str:
  """Collapse repeated spaces and newlines into one space."""
  if text is None:
      return ""

  return re.sub(r"\s+", " ", str(text)).strip()


def parse_year(date_text: str) -> int | None:
  """Extract a four-digit year from common date formats."""

  if not date_text:
      return None

  date_text = date_text.strip()

  common_formats = [
      "%Y-%m-%d",
      "%Y-%m-%dT%H:%M:%S",
      "%Y-%m-%dT%H:%M:%S.%f",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%B %d, %Y",
      "%b %d, %Y",
      "%Y",
  ]

  normalized_date = date_text.replace("Z", "")

  for date_format in common_formats:
      try:
          return datetime.strptime(
              normalized_date,
              date_format,
          ).year
      except ValueError:
          continue

  year_match = re.search(r"\b(19|20)\d{2}\b", date_text)

  if year_match:
      return int(year_match.group())

  return None

def review_recency_features(date_text: str) -> tuple[int, float, str]:
  year = parse_year(date_text)

  if year is None:
      return 0, None, 0.25

  if year >= 2022:
      return 1, year, 1.00

  if year == 2021:
      return 1, year, 0.75

  return 0, year, 0.50

def load_rows(path: Path) -> list[dict[str, Any]]:
  """Load raw CSV rows."""

  if not path.exists():
      raise FileNotFoundError(f"Missing input file: {path}")

  with path.open(
      "r",
      encoding="utf-8",
      newline="",
  ) as file:
      return list(csv.DictReader(file))