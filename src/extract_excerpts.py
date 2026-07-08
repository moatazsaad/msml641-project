import csv
import re
from pathlib import Path
from typing import Any, Dict, List


INPUT_PATH = Path("data/cleaned_reviews.csv")
OUTPUT_PATH = Path("data/review_excerpts.csv")

MIN_EXCERPT_LENGTH = 25
MAX_EXCERPT_LENGTH = 500


WORKLOAD_KEYWORDS = [
    "project",
    "projects",
    "exam",
    "exams",
    "midterm",
    "midterms",
    "final",
    "finals",
    "quiz",
    "quizzes",
    "homework",
    "assignment",
    "assignments",
    "worksheet",
    "worksheets",
    "lab",
    "labs",
    "workload",
    "time",
    "hours",
    "study",
    "studying",
    "hard",
    "difficult",
    "challenging",
    "stress",
    "stressful",
    "start early",
    "self study",
    "self-studying",
    "teach yourself",
    "grading",
    "graded",
    "curve",
    "curved",
    "unfair",
    "disorganized",
    "unclear",
    "confusing",
    "fast paced",
    "fast-paced",
    "lecture",
    "lectures",
]
def load_rows(path: Path) -> List[Dict[str, Any]]:
    """Load cleaned review rows."""

    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def normalize_whitespace(text: Any) -> str:
    """Collapse repeated whitespace into one space."""

    if text is None:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def split_into_sentences(text: str) -> List[str]:
    """Split review text into rough sentence-level excerpts."""

    text = normalize_whitespace(text)

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def contains_workload_signal(text: str) -> bool:
    """Return True when an excerpt contains workload/risk language."""

    lowered = text.casefold()

    return any(
        keyword in lowered
        for keyword in WORKLOAD_KEYWORDS
    )


def is_valid_excerpt(text: str) -> bool:
    """Check basic excerpt quality."""

    length = len(text)

    if length < MIN_EXCERPT_LENGTH:
        return False

    if length > MAX_EXCERPT_LENGTH:
        return False

    return contains_workload_signal(text)


def extract_excerpts(
    rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Extract workload-related excerpts from cleaned reviews."""

    excerpts: List[Dict[str, Any]] = []
    seen_excerpts = set()

    for row in rows:
        review_id = normalize_whitespace(
            row.get("review_id", "")
        )

        course_id = normalize_whitespace(
            row.get("course_id", "")
        )

        professor = normalize_whitespace(
            row.get("professor", "")
        )

        review_text = normalize_whitespace(
            row.get("review_text", "")
        )

        sentences = split_into_sentences(
            review_text
        )

        excerpt_number = 0

        for sentence in sentences:
            if not is_valid_excerpt(sentence):
                continue

            duplicate_key = (
                course_id,
                sentence.casefold(),
            )

            if duplicate_key in seen_excerpts:
                continue

            seen_excerpts.add(duplicate_key)
            excerpt_number += 1

            excerpts.append(
                {
                    "excerpt_id": (
                        f"{review_id}_E{excerpt_number:02d}"
                    ),
                    "review_id": review_id,
                    "course_id": course_id,
                    "professor": professor,
                    "review_excerpt": sentence,
                    "rating": normalize_whitespace(
                        row.get("rating", "")
                    ),
                    "date": normalize_whitespace(
                        row.get("date", "")
                    ),
                    "review_year": normalize_whitespace(
                        row.get("review_year", "")
                    ),
                    "is_recent": normalize_whitespace(
                        row.get("is_recent", "")
                    ),
                    "evidence_weight": normalize_whitespace(
                        row.get("evidence_weight", "")
                    ),
                    "source": normalize_whitespace(
                        row.get("source", "")
                    ),
                }
            )

    return excerpts


def write_excerpts(
    excerpts: List[Dict[str, Any]],
    output_path: Path,
) -> None:
    """Write extracted excerpts to CSV."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "excerpt_id",
        "review_id",
        "course_id",
        "professor",
        "review_excerpt",
        "rating",
        "date",
        "review_year",
        "is_recent",
        "evidence_weight",
        "source",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(excerpts)


def main() -> None:
    """Run excerpt extraction."""

    cleaned_rows = load_rows(
        INPUT_PATH
    )

    excerpts = extract_excerpts(
        cleaned_rows
    )

    write_excerpts(
        excerpts,
        OUTPUT_PATH,
    )

    print(
        f"[done] Wrote {len(excerpts)} excerpts "
        f"to {OUTPUT_PATH}"
    )

    course_counts = {}

    for excerpt in excerpts:
        course_id = excerpt["course_id"]

        course_counts[course_id] = (
            course_counts.get(course_id, 0) + 1
        )

    print("[excerpts per course]")

    for course_id, count in sorted(
        course_counts.items()
    ):
        print(f"{course_id}: {count}")


if __name__ == "__main__":
    main()