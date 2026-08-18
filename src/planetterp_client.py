"""
fetches data from planetterp

"""
import json
from pathlib import Path

import requests
from grade_context import aggregate_grade_rows

BASE_URL = "https://planetterp.com/api/v1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "cache" / "planetterp"

def normalize_course_code(course_code):
    return (
        course_code
        .replace(" ", "")
        .replace("-", "")
        .strip()
        .upper()
    )


def fetch_course_reviews(course_code, cache_dir=CACHE_DIR):
    """Return review records for a valid course, using the raw-response cache."""
    course_code = normalize_course_code(course_code)
    cache_path = Path(cache_dir) / f"{course_code}.json"
    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    else:
        response = requests.get(
            f"{BASE_URL}/course",
            params={"name": course_code, "reviews": "true"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("reviews"), list):
            raise ValueError(f"PlanetTerp did not return a valid course response for {course_code}.")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    reviews = payload.get("reviews", [])
    if not isinstance(reviews, list):
        raise ValueError(f"Cached course response for {course_code} has no review list.")
    return [
        {"review_text": str(item.get("review", "")).strip()}
        for item in reviews
        if str(item.get("review", "")).strip()
    ]
def fetch_grades(course_code):
    course_code = normalize_course_code(course_code)

    response = requests.get(
        f"{BASE_URL}/grades",
        params={"course": course_code},
        timeout=15,
    )

    response.raise_for_status()

    return response.json()
  
def get_grade_context(course_code):
    grade_rows = fetch_grades(course_code)
    return aggregate_grade_rows(grade_rows)
