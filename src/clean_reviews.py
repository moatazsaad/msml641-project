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


def clean_reviews(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Clean, deduplicate, and enrich raw review rows."""

    cleaned_rows: list[dict[str, Any]] = []
    seen_reviews: set[tuple[str, str]] = set()

    missing_review_text_count = 0
    duplicate_review_count = 0
    missing_date_count = 0

    for row in rows:
        review_text = normalize_whitespace(
            row.get("review_text", "")
        )

        if not review_text:
            missing_review_text_count += 1
            continue

        course_id = normalize_whitespace(
            row.get("course_id", "")
        ).upper()

        # Include course ID so the same text in different courses
        # is not automatically treated as a duplicate.
        duplicate_key = (
            course_id,
            review_text.casefold(),
        )

        if duplicate_key in seen_reviews:
            duplicate_review_count += 1
            continue

        seen_reviews.add(duplicate_key)

        professor = normalize_whitespace(
            row.get("professor", "")
        )

        review_date = normalize_whitespace(
            row.get("date", "")
        )

        if not review_date:
            missing_date_count += 1

        is_recent, review_year, evidence_weight = (
            review_recency_features(review_date)
        )

        cleaned_rows.append(
            {
                "review_id": normalize_whitespace(
                    row.get("review_id", "")
                ),
                "course_id": course_id,
                "review_text": review_text,
                "rating": normalize_whitespace(
                    row.get("rating", "")
                ),
                "professor": professor,
                "date": review_date,
                "review_year": (
                    review_year
                    if review_year is not None
                    else ""
                ),
                "source": normalize_whitespace(
                    row.get("source", "")
                ),
                "is_recent": is_recent,
                "evidence_weight": evidence_weight,
            }
        )

    recent_review_count = sum(
        1 for row in cleaned_rows if row["is_recent"] == 1
    )

    professor_review_count = sum(
        1 for row in cleaned_rows if row["professor"]
    )

    dated_review_count = sum(
        1 for row in cleaned_rows if row["review_year"] != ""
    )

    course_ids = {
        row["course_id"]
        for row in cleaned_rows
        if row["course_id"]
    }

    cleaned_count = len(cleaned_rows)

    stats = {
        "total_raw_rows": len(rows),
        "total_cleaned_rows": cleaned_count,
        "missing_review_text_count": missing_review_text_count,
        "duplicate_review_count": duplicate_review_count,
        "missing_date_count": missing_date_count,
        "dated_review_count": dated_review_count,
        "dated_review_rate": (
            round(dated_review_count / cleaned_count, 3)
            if cleaned_count
            else 0
        ),
        "recent_review_count": recent_review_count,
        "recent_review_rate": (
            round(recent_review_count / cleaned_count, 3)
            if cleaned_count
            else 0
        ),
        "reviews_with_professor_count": professor_review_count,
        "reviews_with_professor_rate": (
            round(professor_review_count / cleaned_count, 3)
            if cleaned_count
            else 0
        ),
        "courses_collected": len(course_ids),
    }

    return cleaned_rows, stats    