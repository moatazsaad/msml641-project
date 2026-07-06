"""
need small set of planetterp reviews for TERPLOAD

- need course ids from initial course list csv file
- calls planetterp course API with reviews=True
- waits between calls(api rules say dont hammer w requests)
- Saves raw API responses to data/cache/planetterp/
- Writes a review text CSV to data/raw_planetterp.csv
"""
import csv 
import json
import time
from pathlib import Path
from typing import Any 

import requests

BASE_URL = "https://planetterp.com/api/v1/course"
#need cahche so we dont hammer api
COURSE_LIST_PATH = Path("data/initial_course_list.csv")
CACHE_DIR = Path("data/cache/planetterp")
OUTPUT_PATH = Path("data/raw_planetterp.csv")

REQUESTS_DELAY = 2
MAX_REVIEWS_PER_COURSE = 2

def load_course_ids(path:Path) -> list[str]:
  """Load course IDs """
  if not path.exists():
    raise FileNotFoundError(f"Missing course list file: {path}")
  
  course_ids: list[str] = []
  with path.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    
    for row in reader:
      course_id = row.get("course_id", "").strip()
      
      if course_id:
        course_ids.append(course_id)
  
  return course_ids

def cache_path_for_course(course_id: str) -> Path:
    """Return the cache file path for one course."""
    return CACHE_DIR / f"{course_id}.json"

def extract_reviews(course_id: str, course_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract review text from one PlanetTerp course response."""
    reviews = course_data.get("reviews", [])
    extracted_reviews: list[dict[str, Any]] = []

    for index, review in enumerate(reviews):
        text = review.get("review", "").strip()
        rating = review.get("rating", "")
        professor = review.get("professor", "")
        date = review.get("date", "")

        if not text:
            continue

        extracted_reviews.append(
            {
                "review_id": f"{course_id}_{index + 1:03d}",
                "course_id": course_id,
                "review_text": text,
                "rating": rating,
                "professor": professor,
                "date": date,
                "source": "PlanetTerp",
            }
        )

    return extracted_reviews
  
def write_reviews_csv(reviews: list[dict[str, Any]], output_path: Path )-> None:
  output_path.parent.mkdir(parents=True, exist_ok=True)
  fieldnames = [
    "review_id",
    "course_id",
    "review_text",
    "rating",
    "professor",
    "date",
    "source",
  ]
  with output_path.open("w", encoding="utf-8", newline="") as file:
      writer = csv.DictWriter(file, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(reviews)

  print(f"[done] Wrote {len(reviews)} reviews to {output_path}")


