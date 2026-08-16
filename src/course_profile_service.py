import json
import re
from pathlib import Path

from distilbert_inference import DistilBertWorkloadModel
from planetterp_client import fetch_course_reviews, normalize_course_code
from workload_labels import get_workload_labels


PROFILE_CACHE_PATH = Path("data/cache/course_profiles_distilbert.json")
POSITIVE_LABEL_THRESHOLD = 0.30
LOW_EVIDENCE_REVIEW_THRESHOLD = 10
EVIDENCE_VERSION = 13
EVIDENCE_EXCERPT_MAX_CHARS = 180
EVIDENCE_MIN_UNIT_WORDS = 4
EVIDENCE_MAX_UNIT_WORDS = 55
EVIDENCE_SHORT_UNIT_SCORE_TOLERANCE = 0.05

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
            profile = self._profiles[course_code]
            self._upgrade_cached_evidence(course_code, profile)
            return profile

        reviews = self.fetch_reviews(course_code)
        texts = [review["review_text"] for review in reviews]
        profile = self._build_profile(course_code, texts)
        self._profiles[course_code] = profile
        self._save_profiles()
        return profile

    def _upgrade_cached_evidence(self, course_code, profile):
        """Refresh old cached evidence using the saved DistilBERT model.

        This may run inference once when an old cached profile is first opened,
        but it never changes the cached course workload labels or schedule-risk
        inputs. The refreshed evidence is then persisted with the profile.
        """
        if profile.get("evidence_version") == EVIDENCE_VERSION:
            return
        if profile.get("model") != "distilbert" or "review_count" not in profile:
            return

        try:
            reviews = self.fetch_reviews(course_code)
            review_texts = [review["review_text"] for review in reviews]
        except Exception:
            # Evidence should never make a cached workload profile unavailable.
            return

        profile["evidence_snippets"] = self._select_evidence(
            course_code=course_code,
            review_texts=review_texts,
            predictions=None,
            profile=profile,
        )
        profile["evidence_version"] = EVIDENCE_VERSION
        self._save_profiles()

    def _build_profile(self, course_code, review_texts):
        profile = {
            "course_code": course_code,
            "review_count": len(review_texts),
            "low_evidence": len(review_texts) < LOW_EVIDENCE_REVIEW_THRESHOLD,
            "model": "distilbert",
            "evidence_snippets": [],
            "evidence_version": EVIDENCE_VERSION,
        }
        labels = get_workload_labels()
        if not review_texts:
            for label in labels:
                profile[label] = False
                profile[f"{label}_positive_rate"] = 0.0
            return profile

        model = self._get_model()
        predictions = model.predict(review_texts)
        thresholds = model.thresholds

        for label in labels:
            rate = sum(row[label] >= thresholds[label] for row in predictions) / len(predictions)
            profile[label] = rate >= POSITIVE_LABEL_THRESHOLD
            profile[f"{label}_positive_rate"] = round(rate, 3)

        profile["evidence_snippets"] = self._select_evidence(
            course_code=course_code,
            review_texts=review_texts,
            predictions=predictions,
            profile=profile,
        )
        return profile

    def _select_evidence(self, course_code, review_texts, predictions, profile):
        """Pick conservative, label-specific evidence with DistilBERT."""
        if not review_texts:
            return []

        model = self._get_model()
        labels = get_workload_labels()
        active_labels = [
            label for label in labels
            if profile.get(label)
        ]

        # When no workload category crosses the 30% course-level threshold,
        # we can still surface ONE representative review-level excerpt.
        # This does not change the course labels or schedule risk.
        representative_only = not active_labels
        evidence_labels = active_labels if active_labels else labels

        review_predictions = predictions
        if review_predictions is None:
            review_predictions = model.predict(review_texts)

        review_rankings = []

        for index, row in enumerate(review_predictions):
            score = max(float(row[label]) for label in evidence_labels)
            review_rankings.append((score, index))

        review_rankings.sort(reverse=True)

        candidate_units = []

        for _, review_index in review_rankings[:4]:
            candidate_units.extend(
                self._build_evidence_units(review_texts[review_index])
            )

        # Preserve order while removing duplicate sentence/clause candidates.
        candidate_units = list(dict.fromkeys(candidate_units))

        if not candidate_units:
            return []

        unit_predictions = model.predict(candidate_units)

        candidates_by_label = {
            label: []
            for label in evidence_labels
        }

        # Used only as a final fallback for courses with no dominant workload
        # signal. These candidates do NOT create a course label or affect risk.
        representative_fallback_candidates = []

        for unit, row in zip(candidate_units, unit_predictions):
            active_scores = {
                label: float(row[label])
                for label in evidence_labels
            }

            ranked = sorted(
                active_scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            best_label, best_score = ranked[0]
            second_score = ranked[1][1] if len(ranked) > 1 else 0.0
            specificity_margin = best_score - second_score

            if representative_only:
                representative_fallback_candidates.append(
                    (
                        best_score,
                        specificity_margin,
                        best_label,
                        unit,
                    )
                )

            threshold = float(model.thresholds[best_label])
            minimum_score = max(threshold, 0.60)

            if best_score < minimum_score:
                continue

            if len(ranked) > 1 and specificity_margin < 0.12:
                continue

            candidates_by_label[best_label].append(
                (
                    best_score,
                    specificity_margin,
                    unit,
                )
            )

        label_candidates = []

        for label in evidence_labels:
            candidates = candidates_by_label[label]

            if not candidates:
                continue

            candidates.sort(
                key=lambda item: (item[0], item[1]),
                reverse=True,
            )

            # First find the strongest valid model-supported unit.
            strongest_score = candidates[0][0]

            # Then, among units whose score is essentially as strong, prefer
            # the shortest one. This removes surrounding filler without using
            # workload keywords or rewriting the review text.
            near_best = [
                candidate
                for candidate in candidates
                if candidate[0]
                >= strongest_score - EVIDENCE_SHORT_UNIT_SCORE_TOLERANCE
            ]

            score, margin, unit = min(
                near_best,
                key=lambda item: (
                    len(item[2].split()),
                    -item[0],
                    -item[1],
                ),
            )

            label_candidates.append(
                (
                    score,
                    margin,
                    label,
                    unit,
                )
            )

        label_candidates.sort(reverse=True)

        evidence_items = []
        used_excerpts = set()

        for score, margin, label, unit in label_candidates:
            excerpt = self._truncate_excerpt(
                unit,
                max_chars=EVIDENCE_EXCERPT_MAX_CHARS,
            )

            if excerpt in used_excerpts:
                continue

            used_excerpts.add(excerpt)

            evidence_items.append(
                {
                    "matched_labels": [label],
                    "excerpt": excerpt,
                    "source_url": (
                        f"https://planetterp.com/course/{course_code}/reviews"
                    ),
                    "model_scores": {
                        label: round(score, 4),
                    },
                    "selection_method": "distilbert_shortest_specific",
                    "evidence_scope": (
                        "representative"
                        if representative_only
                        else "active_signal"
                    ),
                }
            )

            # For a no-dominant-signal course, show only the single strongest
            # representative workload excerpt so we do not overstate isolated reviews.
            if representative_only:
                break

            if len(evidence_items) >= 2:
                break

        if representative_only and not evidence_items and representative_fallback_candidates:
            representative_fallback_candidates.sort(
                key=lambda item: (item[0], item[1]),
                reverse=True,
            )

            strongest_score = representative_fallback_candidates[0][0]
            near_best = [
                candidate
                for candidate in representative_fallback_candidates
                if candidate[0]
                >= strongest_score - EVIDENCE_SHORT_UNIT_SCORE_TOLERANCE
            ]

            score, margin, label, unit = min(
                near_best,
                key=lambda item: (
                    len(item[3].split()),
                    -item[0],
                    -item[1],
                ),
            )

            excerpt = self._truncate_excerpt(
                unit,
                max_chars=EVIDENCE_EXCERPT_MAX_CHARS,
            )

            evidence_items.append(
                {
                    "matched_labels": [label],
                    "excerpt": excerpt,
                    "source_url": (
                        f"https://planetterp.com/course/{course_code}/reviews"
                    ),
                    "model_scores": {
                        label: round(score, 4),
                    },
                    "selection_method": "distilbert_representative_fallback",
                    "evidence_scope": "representative_fallback",
                }
            )

        return evidence_items

    @classmethod
    def _build_evidence_units(cls, review_text):
        """Create exact-text sentence and clause candidates for DistilBERT.

        The segmentation is generic: punctuation/conjunction boundaries only.
        No workload keywords are used to decide what text is important.
        DistilBERT still decides which candidate best supports each active label.
        """
        text = " ".join(str(review_text or "").split())
        if not text:
            return []

        sentences = [
            unit.strip()
            for unit in re.split(r"(?<=[.!?])\s+", text)
            if unit.strip()
        ]

        units = []

        for sentence in sentences:
            word_count = len(sentence.split())

            if EVIDENCE_MIN_UNIT_WORDS <= word_count <= EVIDENCE_MAX_UNIT_WORDS:
                units.append(sentence)

            # Generate shorter exact-text clauses from longer sentences.
            # These are only candidates; the model still has to score them
            # above threshold and with enough specificity.
            clauses = cls._split_sentence_clauses(sentence)

            for clause in clauses:
                clause_words = len(clause.split())

                if (
                    EVIDENCE_MIN_UNIT_WORDS
                    <= clause_words
                    <= EVIDENCE_MAX_UNIT_WORDS
                ):
                    units.append(clause)

        return list(dict.fromkeys(units))

    @staticmethod
    def _split_sentence_clauses(sentence):
        """Split a sentence at generic clause boundaries, preserving source text."""
        sentence = " ".join(str(sentence or "").split()).strip()
        if not sentence:
            return []

        # First split at strong punctuation boundaries.
        punctuation_parts = [
            part.strip()
            for part in re.split(r"\s*(?:;|:|—|–)\s*", sentence)
            if part.strip()
        ]

        clauses = []

        for part in punctuation_parts:
            # Commas and common conjunctions often separate the useful clause
            # from surrounding context. We keep the original words; nothing is
            # paraphrased or keyword-selected.
            pieces = [
                piece.strip()
                for piece in re.split(
                    r"\s*,\s+|\s+(?=(?:but|although|though|while|whereas|because|except)\b)",
                    part,
                    flags=re.IGNORECASE,
                )
                if piece.strip()
            ]

            if len(pieces) <= 1:
                continue

            clauses.extend(pieces)

            # Also include adjacent clause pairs so we do not over-trim context.
            for index in range(len(pieces) - 1):
                combined = f"{pieces[index]} {pieces[index + 1]}".strip()
                clauses.append(combined)

        return list(dict.fromkeys(clauses))


    @staticmethod
    def _truncate_excerpt(text, max_chars=EVIDENCE_EXCERPT_MAX_CHARS):
        """Trim a quote at a word boundary so evidence stays scannable."""
        text = " ".join(str(text).split())
        if len(text) <= max_chars:
            return text

        shortened = text[: max_chars - 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
        return shortened + "…"
