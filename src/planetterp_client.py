import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests
from grade_context import aggregate_grade_rows

BASE_URL = "https://planetterp.com/api/v1"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "cache" / "planetterp"

# PlanetTerp can receive new reviews after a course was first cached.
# Empty caches are refreshed much sooner so a newly posted first review
# does not stay invisible in TerpLoad.
REVIEW_CACHE_TTL_SECONDS = 24 * 60 * 60
EMPTY_REVIEW_CACHE_TTL_SECONDS = 15 * 60

def normalize_course_code(course_code):
    return (
        course_code
        .replace(" ", "")
        .replace("-", "")
        .strip()
        .upper()
    )


def _fetch_course_payload_from_planetterp(course_code):
    """Fetch one fresh course payload from PlanetTerp."""
    response = requests.get(
        f"{BASE_URL}/course",
        params={"name": course_code, "reviews": "true"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, dict) or not isinstance(payload.get("reviews"), list):
        raise ValueError(
            f"PlanetTerp did not return a valid course response for {course_code}."
        )

    return payload


def fetch_course_reviews(course_code, cache_dir=CACHE_DIR):
    """Return current course reviews while avoiding stale zero-review caches.

    A previously cached empty response is only trusted briefly. This matters for
    courses such as MSML606: if the course had zero reviews when TerpLoad first
    cached it and a review is later added to PlanetTerp, the app will re-check
    PlanetTerp instead of permanently returning the old empty list.
    """
    course_code = normalize_course_code(course_code)
    cache_path = Path(cache_dir) / f"{course_code}.json"
    payload = None
    should_refresh = True

    if cache_path.exists():
        try:
            with cache_path.open("r", encoding="utf-8") as file:
                cached_payload = json.load(file)

            cached_reviews = cached_payload.get("reviews", [])
            if not isinstance(cached_reviews, list):
                cached_reviews = []

            cache_age_seconds = max(0.0, time.time() - cache_path.stat().st_mtime)
            ttl = (
                EMPTY_REVIEW_CACHE_TTL_SECONDS
                if len(cached_reviews) == 0
                else REVIEW_CACHE_TTL_SECONDS
            )

            if cache_age_seconds < ttl:
                payload = cached_payload
                should_refresh = False
        except (OSError, json.JSONDecodeError):
            # Corrupt/unreadable cache: fetch a clean copy instead.
            should_refresh = True

    if should_refresh:
        payload = _fetch_course_payload_from_planetterp(course_code)
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

def _review_year(review):
    """Return the year from PlanetTerp's review `created` timestamp."""
    created = str(review.get("created", "")).strip()
    if len(created) < 4:
        return None

    try:
        return int(created[:4])
    except ValueError:
        return None


def get_recent_professor_context(course_code, start_year=2024, end_year=2026):
    """Return up to 3 recent actual PROFESSORS for this exact course.

    Inclusion rules:
    - the course's own PlanetTerp review payload must contain a non-empty,
      numeric-rated review for this exact professor/course combination
    - at least one such rating must fall in 2024-2026
    - at least one such rating must fall in 2025-2026
    - PlanetTerp's professor record must have type == "professor" (exclude TAs)

    Ranking:
    - most recent qualifying course rating first
    - ties break by PlanetTerp's current overall average rating
    - return only the top 3

    Displayed rating:
    - PlanetTerp's current overall professor average_rating
    - not a date-window average

    This is context only. It never affects NLP predictions, course labels,
    confidence, or schedule risk.
    """
    course_code = normalize_course_code(course_code)

    course_payload = _fetch_course_payload_from_planetterp(course_code)
    course_reviews = course_payload.get("reviews", [])

    if not isinstance(course_reviews, list):
        return []

    def created_sort_key(review):
        created = str(review.get("created", "")).strip()
        if not created:
            return datetime.min

        normalized = created.replace("Z", "+00:00")

        try:
            parsed = datetime.fromisoformat(normalized)
            # Make comparisons timezone-naive but preserve chronological order.
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone().replace(tzinfo=None)
            return parsed
        except ValueError:
            # PlanetTerp normally exposes a date-like timestamp. If parsing ever
            # fails, still preserve year-level ordering instead of breaking UI.
            year = _review_year(review)
            return datetime(year, 1, 1) if year else datetime.min

    reviews_by_professor = {}

    for review in course_reviews:
        if not isinstance(review, dict):
            continue

        review_text = str(review.get("review", "")).strip()
        if not review_text:
            continue

        try:
            float(review.get("rating"))
        except (TypeError, ValueError):
            continue

        year = _review_year(review)
        if year is None:
            continue

        professor_name = str(
            review.get("professor")
            or review.get("professor_name")
            or ""
        ).strip()

        if not professor_name:
            continue

        reviews_by_professor.setdefault(professor_name, []).append(
            {
                "year": year,
                "created_key": created_sort_key(review),
            }
        )

    candidate_professors = []

    for professor_name, rated_reviews in reviews_by_professor.items():
        has_2024_2026 = any(
            start_year <= item["year"] <= end_year
            for item in rated_reviews
        )
        has_2025_2026 = any(
            max(2025, start_year) <= item["year"] <= end_year
            for item in rated_reviews
        )

        if not (has_2024_2026 and has_2025_2026):
            continue

        recent_window_reviews = [
            item
            for item in rated_reviews
            if start_year <= item["year"] <= end_year
        ]

        latest_rating_date = max(
            item["created_key"]
            for item in recent_window_reviews
        )

        candidate_professors.append(
            (professor_name, latest_rating_date)
        )

    professor_context = []

    for professor_name, latest_rating_date in candidate_professors:
        try:
            professor_response = requests.get(
                f"{BASE_URL}/professor",
                params={"name": professor_name},
                timeout=15,
            )
            professor_response.raise_for_status()
            professor = professor_response.json()
        except requests.RequestException:
            continue

        if not isinstance(professor, dict):
            continue

        # PlanetTerp explicitly distinguishes professor vs TA.
        if str(professor.get("type", "")).strip().lower() != "professor":
            continue

        try:
            average_rating = float(professor.get("average_rating"))
        except (TypeError, ValueError):
            continue

        slug = str(professor.get("slug", "")).strip()
        if not slug:
            continue

        professor_context.append(
            {
                "name": str(
                    professor.get("name", professor_name)
                ).strip(),
                "average_rating": average_rating,
                "latest_rating_date": latest_rating_date.isoformat(),
                "planetterp_url": (
                    "https://planetterp.com/professor/"
                    + quote(slug, safe="_-")
                ),
            }
        )

    # Most recent rated review for THIS COURSE first; rating is only a tie-breaker.
    professor_context.sort(
        key=lambda item: (
            item["latest_rating_date"],
            item["average_rating"],
        ),
        reverse=True,
    )

    return professor_context[:3]