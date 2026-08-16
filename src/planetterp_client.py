"""
fetches data from planetterp

"""
import json
from pathlib import Path

import requests
from grade_context import aggregate_grade_rows

BASE_URL = "https://planetterp.com/api/v1"
CACHE_DIR = Path("data/cache/planetterp")

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
    """Return grade context, trying the matching DATA code for MSML courses."""
    requested_course = normalize_course_code(course_code)

    candidate_codes = [requested_course]

    # The important relationship is the MSML/DATA prefix.
    # Example: if MSML601 has no direct grade rows, try DATA601.
    if requested_course.startswith("MSML"):
        course_number = requested_course[4:]

        if course_number.isdigit():
            candidate_codes.append(f"DATA{course_number}")

    for source_course in candidate_codes:
        try:
            grade_rows = fetch_grades(source_course)
        except requests.RequestException:
            # A missing fallback course should not break the app.
            continue

        context = aggregate_grade_rows(grade_rows)

        if context:
            context["requested_course_code"] = requested_course
            context["grade_source_course_code"] = source_course
            context["used_crosslist_fallback"] = (
                source_course != requested_course
            )
            return context

    return None
