import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any

INPUT_PATH = Path("data/raw_planetterp.csv")
OUTPUT_PATH = Path("data/cleaned_reviews.csv")

def normalize_whitespace(text: str) -> str:
  """Normalize repeated whitespace without changing capitalization."""
  return re.sub(r"\s+", " ", text).strip()


def parse_year(date_text: str) -> int | None:
  """Try to extract a year from a date string."""
  if not date_text:
      return None

  date_text = date_text.strip()

  # Try common full date formats first.
  for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
      try:
          return datetime.strptime(date_text, fmt).year
      except ValueError:
          pass

  # Fallback: find any 4-digit year.
  match = re.search(r"(20\d{2}|19\d{2})", date_text)
  if match:
      return int(match.group(1))

  return None

