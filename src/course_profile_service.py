"""Fetch, infer, and persist course workload profiles for the application."""

import json
from pathlib import Path

from distilbert_inference import DistilBertWorkloadModel
from planetterp_client import fetch_course_reviews, normalize_course_code
from workload_labels import get_workload_labels


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_CACHE_PATH = PROJECT_ROOT / "data" / "cache" / "course_profiles_distilbert.json"
POSITIVE_LABEL_THRESHOLD = 0.30
LOW_EVIDENCE_REVIEW_THRESHOLD = 10


class CourseProfileService:
    """Coordinates live review retrieval with saved-model inference and caching."""

    def __init__(
        self,
        profile_cache_path=PROFILE_CACHE_PATH,
        model_factory=DistilBertWorkloadModel,
        fetch_reviews=fetch_course_reviews,
    ):
        self.profile_cache_path = Path(profile_cache_path)
        self.model_factory = model_factory
        self.fetch_reviews = fetch_reviews
        self._model = None
        self._profiles = self._load_profiles()

    def _load_profiles(self):
        if not self.profile_cache_path.exists():
            return {}
        with self.profile_cache_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save_profiles(self):
        self.profile_cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.profile_cache_path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(self._profiles, file, indent=2)
        temporary.replace(self.profile_cache_path)

    def _get_model(self):
        if self._model is None:
            self._model = self.model_factory()
        return self._model

    def get_profile(self, course_code):
        """Return a cached profile or fetch and infer one exactly once."""
        course_code = normalize_course_code(course_code)
        if course_code in self._profiles:
            return self._profiles[course_code]

        reviews = self.fetch_reviews(course_code)
        texts = [review["review_text"] for review in reviews]
        profile = self._build_profile(course_code, texts)
        self._profiles[course_code] = profile
        self._save_profiles()
        return profile

    def _build_profile(self, course_code, review_texts):
        profile = {
            "course_code": course_code,
            "review_count": len(review_texts),
            "low_evidence": len(review_texts) < LOW_EVIDENCE_REVIEW_THRESHOLD,
            "model": "distilbert",
            "evidence_snippets": review_texts[:2],
        }
        labels = get_workload_labels()
        if not review_texts:
            for label in labels:
                profile[label] = False
                profile[f"{label}_positive_rate"] = 0.0
            return profile

        predictions = self._get_model().predict(review_texts)
        thresholds = self._get_model().thresholds
        for label in labels:
            rate = sum(row[label] >= thresholds[label] for row in predictions) / len(predictions)
            profile[label] = rate >= POSITIVE_LABEL_THRESHOLD
            profile[f"{label}_positive_rate"] = round(rate, 3)
        return profile
