import json
import re
from pathlib import Path

from planetterp_client import fetch_course_reviews, normalize_course_code
from workload_labels import get_workload_labels


PROFILE_CACHE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "cache"
    / "course_profiles_distilbert.json"
)
POSITIVE_LABEL_THRESHOLD = 0.30
LOW_EVIDENCE_REVIEW_THRESHOLD = 10
EVIDENCE_VERSION = 25
EVIDENCE_EXCERPT_MAX_CHARS = 180
EVIDENCE_MIN_UNIT_WORDS = 4
EVIDENCE_MAX_UNIT_WORDS = 55
EVIDENCE_SHORT_UNIT_SCORE_TOLERANCE = 0.05

class CourseProfileService:
    """Coordinates live review retrieval with saved-model inference and caching."""

    def __init__(
        self,
        profile_cache_path=PROFILE_CACHE_PATH,
        model_factory=None,
        fetch_reviews=fetch_course_reviews,
    ):
        self.profile_cache_path = Path(profile_cache_path).resolve()
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
            # Import the heavy transformer stack only for a genuine cache miss.
            if self.model_factory is None:
                from distilbert_inference import DistilBertWorkloadModel
                self.model_factory = DistilBertWorkloadModel
            self._model = self.model_factory()
        return self._model

    def get_profile(self, course_code):
        """Return a cached profile, but re-check courses cached with zero reviews.

        Zero-review profiles are special because PlanetTerp may receive the first
        review later. The raw review client uses a short TTL for empty responses,
        so this check is cheap while still allowing a new first review to appear.
        """
        course_code = normalize_course_code(course_code)

        if course_code in self._profiles:
            profile = self._profiles[course_code]

            if int(profile.get("review_count", 0) or 0) == 0:
                try:
                    reviews = self.fetch_reviews(course_code)
                    review_texts = [review["review_text"] for review in reviews]
                except Exception:
                    # A temporary API problem should not erase a usable cached
                    # zero-review state. Return what we already know.
                    self._upgrade_cached_evidence(course_code, profile)
                    return profile

                if review_texts:
                    # PlanetTerp now has reviews where our old profile had none.
                    # Rebuild with the saved DistilBERT model and replace the stale
                    # zero-review profile. No retraining occurs.
                    profile = self._build_profile(course_code, review_texts)
                    self._profiles[course_code] = profile
                    self._save_profiles()
                    return profile

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
        """Return short evidence for each workload label without overstating it.

        Course-level workload predictions and schedule risk are unchanged.

        For every active course label, evidence is selected only from reviews that
        actually contributed positively to that label. Short candidate excerpts are
        scored with DistilBERT, and their full parent sentence is scored as context.

        This keeps selection generic across all courses and labels: a short fragment
        is pushed down when its surrounding sentence is primarily about a different
        workload category. No course names, review text, or workload keywords are
        hardcoded into the evidence-selection rules.
        """
        if not review_texts:
            return []

        model = self._get_model()
        labels = get_workload_labels()

        active_labels = [
            label
            for label in labels
            if profile.get(label)
        ]

        review_predictions = predictions
        if review_predictions is None:
            review_predictions = model.predict(review_texts)

        evidence_labels = active_labels if active_labels else labels

        review_rankings = []
        for index, row in enumerate(review_predictions):
            strongest_relevant = max(
                float(row[label])
                for label in evidence_labels
            )
            review_rankings.append((strongest_relevant, index))

        review_rankings.sort(reverse=True)

        candidate_records = []
        seen_units = set()

        for _, review_index in review_rankings[:4]:
            for unit in self._build_evidence_units(review_texts[review_index]):
                if unit in seen_units:
                    continue

                seen_units.add(unit)
                candidate_records.append((unit, review_index))

        if not candidate_records:
            return []

        candidate_units = [
            unit
            for unit, _ in candidate_records
        ]
        unit_predictions = model.predict(candidate_units)

        parent_sentences = [
            self._parent_sentence(
                review_texts[review_index],
                unit,
            )
            for unit, review_index in candidate_records
        ]
        parent_predictions = model.predict(parent_sentences)

        # ------------------------------------------------------------------
        # ACTIVE COURSE SIGNALS
        # ------------------------------------------------------------------
        if active_labels:
            evidence_items = []
            used_excerpts = set()

            for label in active_labels:
                threshold = float(model.thresholds[label])
                candidates = []

                for index, (
                    (unit, review_index),
                    unit_row,
                    parent_row,
                ) in enumerate(
                    zip(
                        candidate_records,
                        unit_predictions,
                        parent_predictions,
                    )
                ):
                    # Only use excerpts from a full review that actually counted
                    # positive toward this active course-level label.
                    if (
                        float(review_predictions[review_index][label])
                        < threshold
                    ):
                        continue

                    unit_scores = {
                        workload_label: float(unit_row[workload_label])
                        for workload_label in labels
                    }
                    parent_scores = {
                        workload_label: float(parent_row[workload_label])
                        for workload_label in labels
                    }

                    unit_score = unit_scores[label]
                    parent_score = parent_scores[label]

                    # Never display a clause pulled from the middle of a sentence
                    # as standalone evidence. It may lose the context that explains
                    # what the clause is actually referring to.
                    parent_sentence = parent_sentences[index]
                    if not self._is_standalone_evidence_unit(
                        parent_sentence,
                        unit,
                    ):
                        continue

                    strongest_unit_other = max(
                        score
                        for other_label, score in unit_scores.items()
                        if other_label != label
                    )
                    strongest_parent_other = max(
                        score
                        for other_label, score in parent_scores.items()
                        if other_label != label
                    )

                    strongest_parent_label = max(
                        labels,
                        key=lambda workload_label: parent_scores[workload_label],
                    )

                    # If the full sentence is clearly dominated by a workload type
                    # that is NOT active for the course, do not use its stripped
                    # fragment to explain this label.
                    if (
                        strongest_parent_label not in active_labels
                        and strongest_parent_other > parent_score + 0.05
                    ):
                        continue

                    context_margin = parent_score - strongest_parent_other
                    unit_margin = unit_score - strongest_unit_other

                    # Rank primarily by the target label, but reward agreement from
                    # the full sentence and penalize conflicting context.
                    representation_score = (
                        0.65 * unit_score
                        + 0.35 * parent_score
                        + 0.10 * min(unit_margin, 0.25)
                        + 0.15 * min(context_margin, 0.25)
                    )

                    candidates.append(
                        (
                            representation_score,
                            unit_score,
                            parent_score,
                            unit_margin,
                            context_margin,
                            unit,
                            index,
                        )
                    )

                # Recovery path: if the strict context guard removed every short
                # fragment, choose the candidate from a contributing review whose
                # full sentence best supports the target label relative to others.
                # This still uses model scores only; it does not inspect keywords.
                if not candidates:
                    for index, (
                        (unit, review_index),
                        unit_row,
                        parent_row,
                    ) in enumerate(
                        zip(
                            candidate_records,
                            unit_predictions,
                            parent_predictions,
                        )
                    ):
                        if (
                            float(review_predictions[review_index][label])
                            < threshold
                        ):
                            continue

                        unit_scores = {
                            workload_label: float(unit_row[workload_label])
                            for workload_label in labels
                        }
                        parent_scores = {
                            workload_label: float(parent_row[workload_label])
                            for workload_label in labels
                        }

                        unit_score = unit_scores[label]
                        parent_score = parent_scores[label]

                        parent_sentence = parent_sentences[index]
                        if not self._is_standalone_evidence_unit(
                            parent_sentence,
                            unit,
                        ):
                            continue

                        strongest_unit_other = max(
                            score
                            for other_label, score in unit_scores.items()
                            if other_label != label
                        )
                        strongest_parent_other = max(
                            score
                            for other_label, score in parent_scores.items()
                            if other_label != label
                        )

                        unit_margin = unit_score - strongest_unit_other
                        context_margin = parent_score - strongest_parent_other

                        representation_score = (
                            0.45 * unit_score
                            + 0.55 * parent_score
                            + 0.20 * context_margin
                        )

                        candidates.append(
                            (
                                representation_score,
                                unit_score,
                                parent_score,
                                unit_margin,
                                context_margin,
                                unit,
                                index,
                            )
                        )

                if not candidates:
                    continue

                candidates.sort(
                    key=lambda item: (
                        item[0],
                        item[1],
                        item[2],
                    ),
                    reverse=True,
                )

                strongest_representation = candidates[0][0]
                near_best = [
                    candidate
                    for candidate in candidates
                    if candidate[0]
                    >= strongest_representation
                    - EVIDENCE_SHORT_UNIT_SCORE_TOLERANCE
                ]

                unused_near_best = [
                    candidate
                    for candidate in near_best
                    if self._truncate_excerpt(
                        candidate[5],
                        max_chars=EVIDENCE_EXCERPT_MAX_CHARS,
                    )
                    not in used_excerpts
                ]

                pool = unused_near_best or near_best

                (
                    representation_score,
                    score,
                    parent_score,
                    specificity_margin,
                    parent_margin,
                    unit,
                    chosen_index,
                ) = min(
                    pool,
                    key=lambda item: (
                        len(item[5].split()),
                        -item[0],
                        -item[1],
                        -item[2],
                    ),
                )

                excerpt = self._truncate_excerpt(
                    unit,
                    max_chars=EVIDENCE_EXCERPT_MAX_CHARS,
                )
                used_excerpts.add(excerpt)

                chosen_scores = {
                    workload_label: float(
                        unit_predictions[chosen_index][workload_label]
                    )
                    for workload_label in labels
                }
                parent_chosen_scores = {
                    workload_label: float(
                        parent_predictions[chosen_index][workload_label]
                    )
                    for workload_label in labels
                }

                strongest_label = max(
                    labels,
                    key=lambda workload_label: chosen_scores[workload_label],
                )
                strongest_parent_label = max(
                    labels,
                    key=lambda workload_label: parent_chosen_scores[workload_label],
                )

                strong_minimum = max(threshold, 0.60)
                parent_minimum = max(0.50, threshold - 0.10)

                evidence_strength = (
                    "strong"
                    if (
                        strongest_label == label
                        and strongest_parent_label == label
                        and score >= strong_minimum
                        and parent_score >= parent_minimum
                        and specificity_margin >= 0.12
                        and parent_margin >= 0.05
                    )
                    else "related"
                )

                evidence_items.append(
                    {
                        "matched_labels": [label],
                        "excerpt": excerpt,
                        "source_url": (
                            f"https://planetterp.com/course/{course_code}/reviews"
                        ),
                        "model_scores": {
                            workload_label: round(value, 4)
                            for workload_label, value in chosen_scores.items()
                        },
                        "selection_method": "distilbert_context_ranked_per_label",
                        "evidence_scope": "active_signal",
                        "evidence_strength": evidence_strength,
                    }
                )

            return evidence_items

        # ------------------------------------------------------------------
        # NO DOMINANT COURSE SIGNAL
        # ------------------------------------------------------------------
        strict_candidates = []
        fallback_candidates = []

        for unit, row in zip(candidate_units, unit_predictions):
            scores = {
                label: float(row[label])
                for label in labels
            }

            ranked = sorted(
                scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            best_label, best_score = ranked[0]
            second_score = (
                ranked[1][1]
                if len(ranked) > 1
                else 0.0
            )
            margin = best_score - second_score

            fallback_candidates.append(
                (best_score, margin, best_label, unit)
            )

            minimum_score = max(
                float(model.thresholds[best_label]),
                0.60,
            )

            if best_score < minimum_score:
                continue
            if len(ranked) > 1 and margin < 0.12:
                continue

            strict_candidates.append(
                (best_score, margin, best_label, unit)
            )

        candidate_pool = strict_candidates or fallback_candidates

        if not candidate_pool:
            return []

        candidate_pool.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True,
        )

        strongest_score = candidate_pool[0][0]

        near_best = [
            candidate
            for candidate in candidate_pool
            if candidate[0]
            >= strongest_score
            - EVIDENCE_SHORT_UNIT_SCORE_TOLERANCE
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

        return [
            {
                "matched_labels": [label],
                "excerpt": excerpt,
                "source_url": (
                    f"https://planetterp.com/course/{course_code}/reviews"
                ),
                "model_scores": {
                    label: round(score, 4),
                },
                "selection_method": (
                    "distilbert_shortest_specific"
                    if strict_candidates
                    else "distilbert_representative_fallback"
                ),
                "evidence_scope": (
                    "representative"
                    if strict_candidates
                    else "representative_fallback"
                ),
            }
        ]

    @staticmethod
    def _is_standalone_evidence_unit(parent_sentence, unit):
        """Reject decontextualized mid-sentence fragments.

        Evidence can still be concise, but a fragment cut out of the middle of a
        longer sentence is not displayed by itself. This prevents dependent clauses
        from losing the context that changes their meaning.

        This rule is generic: it does not inspect course codes, workload keywords,
        or any specific review text.
        """
        parent = " ".join(str(parent_sentence or "").split())
        candidate = " ".join(str(unit or "").split())

        if not parent or not candidate:
            return False

        # A complete sentence is always eligible.
        if candidate == parent:
            return True

        # A shortened unit is eligible only when it begins the source sentence.
        # Mid-sentence pieces are too easy to misread without their context.
        return parent.startswith(candidate)

    @staticmethod
    def _parent_sentence(review_text, unit):
        """Return the full source sentence containing a candidate clause.

        Clause-level evidence can lose important context. For example, a fragment
        like "time limit (60 minutes...)" may come from a sentence explicitly
        describing a midterm. We therefore validate every active-signal clause
        against its full parent sentence before displaying it.
        """
        review = " ".join(str(review_text or "").split())
        unit_text = " ".join(str(unit or "").split())

        if not review or not unit_text:
            return unit_text

        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", review)
            if sentence.strip()
        ]

        def canonical(value):
            return " ".join(
                re.findall(r"[A-Za-z0-9]+", str(value).lower())
            )

        unit_key = canonical(unit_text)

        for sentence in sentences:
            if unit_key and unit_key in canonical(sentence):
                return sentence

        return unit_text

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
