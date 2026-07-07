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
MAX_REVIEWS_PER_COURSE = 50

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
        date = review.get("created", "")
        

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


def fetch_course_data(course_id: str) -> dict[str, Any]:
  """Fetch one course from PlanetTerp, using cache when possible."""
  CACHE_DIR.mkdir(parents=True, exist_ok=True)
  cache_path = cache_path_for_course(course_id)

  if cache_path.exists():
      print(f"[cache] Using cached data for {course_id}")
      with cache_path.open("r", encoding="utf-8") as file:
          return json.load(file)

  print(f"[fetch] Requesting {course_id} from PlanetTerp")

  response = requests.get(
      BASE_URL,
      params={
          "name": course_id,
          "reviews": "true",
      },
      timeout=20,
  )

  response.raise_for_status()
  course_data = response.json()

  with cache_path.open("w", encoding="utf-8") as file:
      json.dump(course_data, file, indent=2)

  time.sleep(REQUESTS_DELAY)

  return course_data



#main method to get all courses and  handle any errors
def main() -> None:
  """Collect PlanetTerp reviews for the initial course list."""
  course_ids = load_course_ids(COURSE_LIST_PATH)
  print(f"[start] Loaded {len(course_ids)} courses")

  all_reviews: list[dict[str, Any]] = []

  for course_id in course_ids:
      course_id = course_id.strip().upper()

      try:
          course_data = fetch_course_data(course_id)
          reviews = extract_reviews(course_id, course_data)

          if MAX_REVIEWS_PER_COURSE is not None:
              reviews = reviews[:MAX_REVIEWS_PER_COURSE]

          print(f"[course] {course_id}: {len(reviews)} reviews")
          all_reviews.extend(reviews)

      except requests.HTTPError as error:
          print(f"[error] HTTP error for {course_id}: {error}")

      except requests.RequestException as error:
          print(f"[error] Request failed for {course_id}: {error}")

      except Exception as error:
          print(f"[error] Unexpected error for {course_id}: {error}")

  write_reviews_csv(all_reviews, OUTPUT_PATH)


if __name__ == "__main__":
    main()