import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any

INPUT_PATH = Path("data/raw_planetterp.csv")
OUTPUT_PATH = Path("data/cleaned_reviews.csv")

def normalize_whitespace(text: str) -> str:
  """Normalize repeated whitespace"""
  return re.sub(r"\s+", " ", text).strip()


def parse_year(date_text: str) -> int | None:
  if not date_text:
      return None

  date_text = date_text.strip()

  # handling full date formats
  for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
      try:
          return datetime.strptime(date_text, fmt).year
      except ValueError:
          pass

  #get any year only
  match = re.search(r"(20\d{2}|19\d{2})", date_text)
  if match:
      return int(match.group(1))

  return None

def is_recent_review(date_text: str) -> int:
    """Return 1 if review is from 2022 or later, otherwise 0."""
    year = parse_year(date_text)
    if year is not None and year >= 2022:
        return 1
    return 0
