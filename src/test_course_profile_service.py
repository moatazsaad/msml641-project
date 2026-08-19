"""Executable backend checks for DistilBERT course-profile behavior."""

import json
import tempfile
from pathlib import Path

from course_profile_service import CourseProfileService
from distilbert_inference import DistilBertWorkloadModel, SavedModelUnavailableError
from planetterp_client import fetch_course_reviews


class FakeModel:
    thresholds = {
        "project_heavy": 0.9,
        "exam_heavy": 0.65,
        "homework_heavy": 0.55,
        "time_consuming": 0.75,
    }

    def predict(self, texts):
        return [
            {
                "project_heavy": 0.95,
                "exam_heavy": 0.70,
                "homework_heavy": 0.20,
                "time_consuming": 0.80,
            }
            for _ in texts
        ]


def make_service(cache_path, fetch_reviews, factory=lambda: FakeModel()):
    return CourseProfileService(
        profile_cache_path=cache_path,
        fetch_reviews=fetch_reviews,
        model_factory=factory,
    )


def test_known_course_uses_saved_profile_without_fetching_or_loading_model():
    with tempfile.TemporaryDirectory() as directory:
        cache_path = Path(directory) / "profiles.json"
        cache_path.write_text(json.dumps({"CMSC216": {"course_code": "CMSC216"}}))
        calls = {"fetch": 0, "model": 0}

        def fetch(_):
            calls["fetch"] += 1
            raise AssertionError("cached courses must not fetch")

        def factory():
            calls["model"] += 1
            raise AssertionError("cached courses must not load the model")

        profile = make_service(cache_path, fetch, factory).get_profile("cmsc 216")
        assert profile["course_code"] == "CMSC216"
        assert calls == {"fetch": 0, "model": 0}


def test_cached_raw_course_reviews_are_available_without_a_live_request():
    with tempfile.TemporaryDirectory() as directory:
        cache_path = Path(directory) / "CMSC216.json"
        cache_path.write_text(json.dumps({"reviews": [{"review": "Useful review"}]}))
        reviews = fetch_course_reviews("cmsc 216", cache_dir=directory)
        assert reviews == [{"review_text": "Useful review"}]


def test_unseen_course_fetches_infers_and_is_reused_from_cache():
    with tempfile.TemporaryDirectory() as directory:
        cache_path = Path(directory) / "profiles.json"
        calls = {"fetch": 0, "model": 0}

        def fetch(course):
            calls["fetch"] += 1
            assert course == "MATH999"
            return [{"review_text": "First review"}, {"review_text": "Second review"}]

        def factory():
            calls["model"] += 1
            return FakeModel()

        profile = make_service(cache_path, fetch, factory).get_profile("math 999")
        assert profile["model"] == "distilbert"
        assert profile["review_count"] == 2
        assert profile["project_heavy"] is True
        assert profile["homework_heavy"] is False
        assert calls == {"fetch": 1, "model": 1}

        cached = make_service(cache_path, lambda _: (_ for _ in ()).throw(AssertionError()), factory)
        assert cached.get_profile("MATH999") == profile
        assert calls == {"fetch": 1, "model": 1}


def test_api_failure_is_not_saved_as_a_profile():
    with tempfile.TemporaryDirectory() as directory:
        cache_path = Path(directory) / "profiles.json"

        def failing_fetch(_):
            raise ConnectionError("PlanetTerp unavailable")

        service = make_service(cache_path, failing_fetch)
        try:
            service.get_profile("CMSC999")
            raise AssertionError("expected API error")
        except ConnectionError:
            pass
        assert not cache_path.exists()


def test_missing_saved_model_reports_actionable_error():
    with tempfile.TemporaryDirectory() as directory:
        try:
            DistilBertWorkloadModel(Path(directory) / "missing")
            raise AssertionError("expected unavailable-model error")
        except SavedModelUnavailableError as error:
            assert "Saved DistilBERT model not found" in str(error)


def test_git_lfs_pointer_reports_actionable_error():
    with tempfile.TemporaryDirectory() as directory:
        model_dir = Path(directory)
        (model_dir / "config.json").write_text("{}")
        (model_dir / "model.safetensors").write_text(
            "version https://git-lfs.github.com/spec/v1\n"
        )
        try:
            DistilBertWorkloadModel(model_dir)
            raise AssertionError("expected unavailable-model error")
        except SavedModelUnavailableError as error:
            assert "Git LFS pointer" in str(error)


def test_full_schedule_analysis_uses_profiles_end_to_end():
    from risk_rules import estimate_schedule_risk
    from simple_report_cli import build_course_inputs

    with tempfile.TemporaryDirectory() as directory:
        cache_path = Path(directory) / "profiles.json"
        service = make_service(
            cache_path,
            lambda code: [{"review_text": f"Review for {code}"}],
        )
        codes = ["CMSC330", "CMSC351", "STAT400"]
        signals = {code: service.get_profile(code) for code in codes}
        courses, missing = build_course_inputs(codes, signals)
        result = estimate_schedule_risk(courses)

        assert missing == []
        assert len(courses) == 3
        assert result["risk_level"] in {"Low", "Medium", "High"}
        assert all(profile["model"] == "distilbert" for profile in signals.values())


TESTS = [
    test_known_course_uses_saved_profile_without_fetching_or_loading_model,
    test_cached_raw_course_reviews_are_available_without_a_live_request,
    test_unseen_course_fetches_infers_and_is_reused_from_cache,
    test_api_failure_is_not_saved_as_a_profile,
    test_missing_saved_model_reports_actionable_error,
    test_git_lfs_pointer_reports_actionable_error,
    test_full_schedule_analysis_uses_profiles_end_to_end,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
        print(f"[PASS] {test.__name__}")
    print(f"\n{len(TESTS)} passed, 0 failed")
