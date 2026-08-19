"""Precompute TerpLoad demo caches once, then commit the generated JSON files.

Run from the repository root:
    python scripts/precompute_demo_cache.py

It uses the saved DistilBERT model and the existing
PlanetTerp review cache to upgrade evidence using CourseProfileService's exact
_select_evidence implementation. It also snapshots professor and grade context so
those secondary lookups do not block the deployed demo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from course_profile_service import CourseProfileService, EVIDENCE_VERSION
from planetterp_client import get_grade_context, get_recent_professor_context

PROFILE_CACHE = ROOT / "data" / "cache" / "course_profiles_distilbert.json"
PLANETTERP_CACHE = ROOT / "data" / "cache" / "planetterp"
GRADE_CACHE = ROOT / "data" / "cache" / "grade_context.json"
PROF_CACHE = ROOT / "data" / "cache" / "professor_context.json"


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def cached_review_texts(course_code: str):
    path = PLANETTERP_CACHE / f"{course_code}.json"
    payload = read_json(path, {})
    reviews = payload.get("reviews", []) if isinstance(payload, dict) else []
    return [
        str(item.get("review", "")).strip()
        for item in reviews
        if isinstance(item, dict) and str(item.get("review", "")).strip()
    ]


def main():
    service = CourseProfileService(profile_cache_path=PROFILE_CACHE)
    course_codes = sorted(service._profiles)
    if not course_codes:
        raise SystemExit(f"No profiles found in {PROFILE_CACHE}")

    print(f"Found {len(course_codes)} cached course profiles")
    changed = False
    for index, code in enumerate(course_codes, 1):
        profile = service._profiles[code]
        if profile.get("evidence_version") == EVIDENCE_VERSION:
            print(f"[{index}/{len(course_codes)}] {code}: evidence already current")
            continue
        texts = cached_review_texts(code)
        if not texts:
            print(f"[{index}/{len(course_codes)}] {code}: no cached review text; skipped")
            continue
        print(f"[{index}/{len(course_codes)}] {code}: upgrading evidence from {len(texts)} cached reviews...")
        profile["evidence_snippets"] = service._select_evidence(
            course_code=code,
            review_texts=texts,
            predictions=None,
            profile=profile,
        )
        profile["evidence_version"] = EVIDENCE_VERSION
        changed = True

    if changed:
        service._save_profiles()
        print(f"Saved upgraded evidence to {PROFILE_CACHE}")

    grade_cache = read_json(GRADE_CACHE, {})
    prof_cache = read_json(PROF_CACHE, {})

    for index, code in enumerate(course_codes, 1):
        if code not in grade_cache:
            print(f"[{index}/{len(course_codes)}] {code}: caching grade context...")
            try:
                grade_cache[code] = get_grade_context(code)
            except Exception as exc:
                print(f"  grade lookup failed: {exc}")
        if code not in prof_cache:
            print(f"[{index}/{len(course_codes)}] {code}: caching professor context...")
            try:
                prof_cache[code] = get_recent_professor_context(code, start_year=2024, end_year=2026)
            except Exception as exc:
                print(f"  professor lookup failed: {exc}")

    write_json(GRADE_CACHE, grade_cache)
    write_json(PROF_CACHE, prof_cache)
    print(f"Saved {GRADE_CACHE}")
    print(f"Saved {PROF_CACHE}")
    print("Done. Commit the three JSON cache files plus the optimized app/service files.")


if __name__ == "__main__":
    main()
