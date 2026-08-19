"""
TerpLoad - Streamlit demo

This is a display layer only. It reuses the exact same functions the CLI
(src/simple_report_cli.py) uses - no risk logic lives here, so the web
version and the CLI version can never disagree.

Styling is custom CSS to match a team design mockup. Everything shown is
built from real data:
- risk level / reasons: risk_rules.py, unchanged
- workload tags: the same project_heavy/exam_heavy/etc. flags as the CLI
- evidence quotes: real evidence_snippet text from the labeled review CSVs
- "confidence" and "best move": new, simple rules defined here, based on
  real review counts - not invented numbers. There is no grade-weighting
  data available (e.g. "83% of your grade"), so that is not shown here.
"""
import re
import csv
import html
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from planetterp_client import get_grade_context, get_recent_professor_context
from risk_rules import estimate_schedule_risk  # noqa: E402
from course_profile_service import CourseProfileService, POSITIVE_LABEL_THRESHOLD  # noqa: E402
from distilbert_inference import SavedModelUnavailableError  # noqa: E402
from simple_report_cli import build_course_inputs, get_low_evidence_courses  # noqa: E402
from workload_labels import WORKLOAD_LABELS  # noqa: E402
import plotly.graph_objects as go
st.set_page_config(
    page_title="TerpLoad",
    page_icon="assets/terpload_logo.png",
    layout="centered",
)

RISK_COLORS = {"Low": "low", "Medium": "medium", "High": "high", "Uncertain": "uncertain"}

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #2b1f1a 0%, #1a1512 45%, #0f0d0c 100%);
    }
    .terpload-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.4rem;
        letter-spacing: 3px;
        color: #f5f0e8;
        margin-bottom: 0.2rem;
    }
    .terpload-subtitle {
        text-align: center;
        color: #cfc7ba;
        margin-bottom: 1.5rem;
    }
    /* Course selector shell */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background-color: #fdfbf5 !important;
        border-radius: 19px !important;
        border: 1px solid #d8b04a !important;
        min-height: 56px !important;
        padding: 5px 9px !important;
    }

    /* Selected course chips */
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: #171717 !important;
        border: 1px solid #171717 !important;
        border-radius: 7px !important;
        min-height: 30px !important;
        height: 30px !important;
        padding: 0 0.35rem !important;
        box-shadow: none !important;
    }

    div[data-testid="stMultiSelect"] [data-baseweb="tag"],
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] * {
        color: #ffffff !important;
    }

    div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.15px !important;
    }

    div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
        width: 14px !important;
        height: 14px !important;
    }

    div[data-testid="stMultiSelect"] input {
        color: #1a1a1a !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
    }

    /* Make the empty search placeholder visible against the white selector.
       Streamlit/BaseWeb can inherit WebKit text-fill separately from `color`,
       so set both explicitly. */
    div[data-testid="stMultiSelect"] input::placeholder,
    div[data-testid="stMultiSelect"] input::-webkit-input-placeholder {
        color: #7a7a7a !important;
        -webkit-text-fill-color: #7a7a7a !important;
        opacity: 1 !important;
        text-transform: none !important;
    }

    div[data-testid="stMultiSelect"] input {
        -webkit-text-fill-color: #1a1a1a !important;
        caret-color: #1a1a1a !important;
    }

    /* Display selected/new course codes in uppercase without mutating widget state. */
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        text-transform: uppercase !important;
    }

    /* Autocomplete/dropdown options also display as uppercase. */
    div[role="listbox"] [role="option"] {
        text-transform: uppercase !important;
    }

    /* Submit arrow: same TerpLoad red as the report headers */
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button[kind="primary"] {
        min-height: 54px !important;
        height: 54px !important;
        border-radius: 999px !important;
        padding: 0 !important;
        font-size: 1.25rem !important;
        min-width: 78px !important;
        width: 78px !important;
        max-width: 78px !important;
        margin: 0 auto !important;

        background: #FF0000 !important;
        border-color: #E60000 !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
        background: #CC0000 !important;
        border-color: #CC0000 !important;
        color: #ffffff !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:active,
    div[data-testid="stButton"] button[kind="primary"]:focus,
    div[data-testid="stFormSubmitButton"] button[kind="primary"]:active,
    div[data-testid="stFormSubmitButton"] button[kind="primary"]:focus {
        background: #CC0000 !important;
        border-color: #CC0000 !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }

    /* Keep the selector form visually invisible; it is only used to batch input. */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }
    .card {
        background: #ffffff;
        color: #1a1a1a;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 1rem;
        border: 1px solid #e5e1dd;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    }
    .card-header {
        background: #E60000;
        color: white;
        padding: 0.65rem 1.1rem;
        font-weight: 800;
        letter-spacing: 1px;
        font-size: 0.76rem;
        display: flex;
        justify-content: space-between;
    }
    .card-body { padding: 1rem 1.2rem; }
    .risk-pill {
        display: inline-block;
        color: white;
        padding: 0.15rem 0.9rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .risk-pill.high { background: #E60000; }
    .risk-pill.medium { background: #b8860b; }
    .risk-pill.low { background: #2e7d32; }
    .risk-pill.uncertain { background: #666666; }
    .confidence-text { font-weight: 700; font-size: 0.9rem; }
    .confidence-text.high { color: #2e7d32; }
    .confidence-text.medium { color: #b8860b; }
    .confidence-text.low { color: #E60000; }
    .eyebrow { font-size: 0.7rem; color: #777; letter-spacing: 1px; }

    .main-driver {
        border-top: 1px solid #eeeeee;
        background: #fafafa;
        padding: 0.75rem 1.2rem 0.85rem 1.2rem;
        font-size: 0.88rem;
        line-height: 1.4;
        color: #333333;
    }

    .main-driver-label {
        display: block;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.9px;
        color: #777777;
        margin-bottom: 0.18rem;
    }
    .advice-box {
        background: #f6f7f8;
        border: 1px solid #e7e8ea;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .warning-box {
        background: #fbe6ea;
        border-left: 4px solid #E60000;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        margin-top: 0.9rem;
    }
    .reasoning-bar {
        background: #343434;
        color: #f3f3f3;
        padding: 0.5rem 1.1rem;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 1px;
    }

    .reasoning-content {
        padding: 1rem 1.2rem 1.15rem 1.2rem;
    }

    .reasoning-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.65rem;
    }

    .reasoning-course-box {
        background: #fafafa;
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        padding: 0.8rem 0.85rem;
        min-height: 72px;
    }

    .reasoning-course-code {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.7px;
        color: #E60000;
        margin-bottom: 0.25rem;
    }

    .reasoning-course-text {
        font-size: 0.87rem;
        line-height: 1.35;
        color: #333;
    }

    .reasoning-conclusion {
        margin-top: 0.8rem;
        padding: 0.7rem 0.85rem;
        background: #fbf3f5;
        border-left: 3px solid #E60000;
        border-radius: 8px;
        font-size: 0.86rem;
        line-height: 1.4;
        color: #2b2b2b;
    }

    .reasoning-conclusion strong {
        color: #E60000;
    }
    .signal-row {
        padding: 0.78rem 1.15rem;
        border-top: 1px solid #eeeeee;
    }

    .signal-line {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        width: 100%;
        flex-wrap: nowrap;
    }

    .signal-course {
        font-weight: 700;
        min-width: 82px;
        white-space: nowrap;
    }

    .signal-items {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        flex-wrap: wrap;
        min-width: 0;
    }

    .signal-item {
        display: inline-flex;
        align-items: center;
        gap: 0.28rem;
        white-space: nowrap;
    }

    .signal-percent {
        color: #666;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .signal-review-count {
        margin-left: auto;
        padding-left: 0.8rem;
        color: #777;
        font-size: 0.78rem;
        white-space: nowrap;
    }

    @media (max-width: 700px) {
        .signal-line {
            flex-wrap: wrap;
        }

        .signal-review-count {
            width: 100%;
            margin-left: 82px;
            padding-left: 0.55rem;
        }
    }
    .tag {
        display: inline-block;
        background: #efefed;
        border: 1px solid #d9d9d6;
        border-radius: 999px;
        padding: 0.12rem 0.58rem;
        font-size: 0.66rem;
        font-weight: 700;
        margin-left: 0.4rem;
        color: #5f5f5f;
        vertical-align: middle;
    }
    .tag.muted {
        background: #f7f7f5;
        color: #888;
    }
    .signal-detail { font-size: 0.85rem; color: #555; margin-top: 0.15rem; }
    .evidence-quote {
        border-left: 3px solid #E60000;
        padding: 0.2rem 0.75rem;
        margin: 0.35rem 1.2rem 0.9rem 1.2rem;
        font-style: italic;
        font-size: 0.88rem;
        line-height: 1.45;
        color: #333;
    }
    .evidence-source { font-size: 0.72rem; color: #888; margin: -0.3rem 1.2rem 0.6rem 1.2rem; }
    .evidence-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin: 0.75rem 1.2rem 0.1rem 1.2rem;
    }
    .evidence-link {
        font-size: 0.72rem;
        font-weight: 700;
        color: #E60000 !important;
        text-decoration: none !important;
        white-space: nowrap;
    }
    .evidence-link:hover { text-decoration: underline !important; }

    /* Historical grade course selector — TerpLoad red */
    div[data-testid="stSegmentedControl"] button {
        border-radius: 999px !important;
        border-color: #E60000 !important;
        background: transparent !important;
        font-weight: 700 !important;
        min-height: 36px !important;
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
    }

    div[data-testid="stSegmentedControl"] button,
    div[data-testid="stSegmentedControl"] button * {
        color: #E60000 !important;
    }

    /* Selected grade-context course */
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
        background: #E60000 !important;
        border-color: #E60000 !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"] * {
        color: #ffffff !important;
    }

    /* Hover */
    div[data-testid="stSegmentedControl"] button:hover {
        border-color: #E60000 !important;
        background: #fff1f1 !important;
    }

    div[data-testid="stSegmentedControl"] button:hover,
    div[data-testid="stSegmentedControl"] button:hover * {
        color: #E60000 !important;
    }

    /* Selected course stays white-on-red while hovering */
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"]:hover {
        background: #CC0000 !important;
        border-color: #CC0000 !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-pressed="true"]:hover,
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"]:hover * {
        color: #ffffff !important;
    }

    .why-signals-card {
        background: #ffffff;
        border-radius: 16px;
        overflow: hidden;
    }
    .why-signals-header {
        background: #E60000;
        color: #ffffff;
        padding: 0.72rem 1.15rem;
        font-size: 0.82rem;
        font-weight: 850;
        letter-spacing: 0.03em;
    }
    .why-signals-content {
        padding-bottom: 0.85rem;
    }

    .course-evidence-block {
        padding: 0.8rem 1.2rem 0.95rem 1.2rem;
        border-bottom: 1px solid #ece6e0;
    }
    .course-evidence-block:last-child {
        border-bottom: none;
        padding-bottom: 1.35rem;
    }
    .course-evidence-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
        margin-bottom: 0.18rem;
    }
    .course-evidence-code {
        color: #24201d;
        font-size: 0.79rem;
        font-weight: 850;
        letter-spacing: 0.01em;
    }

    /* Evidence stays visible. Course-wide PlanetTerp link is a small text link. */
    .course-evidence-excerpt-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.9rem;
    }
    .course-evidence-excerpt-row .evidence-quote {
        flex: 1 1 auto;
        min-width: 0;
        margin: 0.32rem 0 0.42rem 0 !important;
    }
    .course-evidence-course-link {
        flex: 0 0 auto;
        margin-top: 0.42rem;
        color: #d90000 !important;
        font-size: 0.68rem;
        font-weight: 800;
        text-decoration: none !important;
        white-space: nowrap;
    }
    .course-evidence-course-link:hover {
        text-decoration: underline !important;
    }

    /* Professor context: grouped/attached rows, open by default */
    .course-professor-details {
        margin-top: 0.5rem;
        border: 1px solid #ddd5ce;
        border-radius: 7px;
        overflow: hidden;
        background: #f1eeeb;
    }

    .course-professor-summary {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        box-sizing: border-box;
        list-style: none;
        cursor: pointer;
        color: #24201d;
        background: #f1eeeb;
        padding: 0.52rem 0.68rem;
        font-size: 0.70rem;
        font-weight: 850;
        user-select: none;
        outline: none;
        border: none;
    }

    .course-professor-summary::-webkit-details-marker {
        display: none;
    }

    .course-professor-summary::after {
        content: "⌃";
        margin-left: auto;
        color: #8f8780;
        font-size: 0.72rem;
        line-height: 1;
    }

    .course-professor-details:not([open]) .course-professor-summary::after {
        content: "⌄";
    }

    .course-professor-summary:hover {
        color: #E60000;
        background: #f5f1ee;
    }

    .course-professor-list {
        margin: 0;
        padding: 0;
        background: #ffffff;
        border-top: 1px solid #ddd5ce;
    }

    .course-professor-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
        padding: 0.56rem 0.68rem;
        margin: 0;
        background: #ffffff;
        border: none;
        border-top: 1px solid #e4ddd7;
        border-radius: 0;
        color: inherit !important;
        text-decoration: none !important;
        transition:
            background 0.12s ease,
            color 0.12s ease,
            border-color 0.12s ease;
    }

    .course-professor-row:first-child {
        border-top: none;
    }

    .course-professor-row:hover {
        background: #fff1f1;
        color: #E60000 !important;
        text-decoration: none !important;
    }

    .course-professor-name {
        color: #24201d;
        font-size: 0.76rem;
        font-weight: 400;
        transition: color 0.12s ease;
    }

    .course-professor-rating {
        color: #24201d;
        font-size: 0.75rem;
        font-weight: 800;
        white-space: nowrap;
        transition: color 0.12s ease;
    }

    .course-professor-row:hover .course-professor-name,
    .course-professor-row:hover .course-professor-rating {
        color: #E60000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


COURSE_SERVICE_CACHE_VERSION = 22
GRADE_CONTEXT_CACHE_VERSION = 3
PROFESSOR_CONTEXT_CACHE_VERSION = 3

@st.cache_resource
def get_course_service(cache_version):
    """Keep the profile cache and loaded DistilBERT model across reruns."""
    return CourseProfileService()

@st.cache_data(ttl=3600, show_spinner="Loading historical grade context...")
def load_grade_context(course_code, cache_version):
    """Fetch historical grade context without refetching on each rerun."""
    try:
        return get_grade_context(course_code)
    except Exception:
        return None


@st.cache_data(ttl=21600, show_spinner="Loading professor context...")
def load_professor_context(
    course_code,
    start_year=2024,
    end_year=2026,
    cache_version=PROFESSOR_CONTEXT_CACHE_VERSION,
):
    """Fetch professor context without slowing every Streamlit rerun."""
    try:
        return get_recent_professor_context(
            course_code,
            start_year=start_year,
            end_year=end_year,
        )
    except Exception:
        return []




def compute_confidence(courses, courses_without_data):
    """Simple, real-data-based confidence label - not a trained score."""
    if courses_without_data:
        return "Low"
    if any(c.get("low_evidence") for c in courses):
        return "Low"
    if any(c.get("review_count", 0) < 30 for c in courses):
        return "Medium"
    return "High"


def display_risk_level(model_risk_level, courses, courses_without_data):
    """Avoid a definitive risk headline when review coverage is too sparse."""
    if courses_without_data:
        return "Uncertain"

    review_counts = [c.get("review_count", 0) for c in courses]

    if any(count == 0 for count in review_counts):
        return "Uncertain"

    if review_counts and all(count < 10 for count in review_counts):
        return "Uncertain"

    return model_risk_level


def main_driver_text(courses, courses_without_data):
    """Return one concise explanation for what is driving the schedule result."""
    review_counts = [c.get("review_count", 0) for c in courses]

    if (
        courses_without_data
        or any(count == 0 for count in review_counts)
        or (review_counts and all(count < 10 for count in review_counts))
    ):
        return "Review coverage is too sparse for a confident schedule conclusion."

    pressure_labels = [
        ("project_heavy", "project"),
        ("exam_heavy", "exam"),
        ("homework_heavy", "homework"),
        ("time_consuming", "time-consuming"),
    ]

    overlaps = []
    for label, display_name in pressure_labels:
        matching_courses = [
            course["course_code"]
            for course in courses
            if course.get(label)
        ]
        if len(matching_courses) >= 2:
            overlaps.append((display_name, matching_courses))

    if overlaps:
        display_name, matching_courses = max(
            overlaps,
            key=lambda item: len(item[1]),
        )

        if len(matching_courses) == 2:
            course_text = f"{matching_courses[0]} and {matching_courses[1]}"
        else:
            course_text = (
                ", ".join(matching_courses[:-1])
                + f", and {matching_courses[-1]}"
            )

        return f"Overlapping {display_name} pressure across {course_text}."

    flagged = [
        course
        for course in courses
        if any(course.get(label) for label, _ in pressure_labels)
    ]

    if flagged:
        dominant = max(
            flagged,
            key=lambda course: sum(
                bool(course.get(label))
                for label, _ in pressure_labels
            ),
        )
        return (
            f"{dominant['course_code']} carries the strongest workload pressure "
            "in this schedule."
        )

    return "No major workload overlap stands out."


def best_move_text(result, courses_without_data, courses):
    """Give one short, actionable recommendation instead of restating the risk."""
    review_counts = [c.get("review_count", 0) for c in courses]

    if courses_without_data or any(count == 0 for count in review_counts):
        return (
            "For courses with no reviews, check instructor reviews and ask the professor "
            "for a recent syllabus before making a schedule change."
        )

    if review_counts and all(count < 10 for count in review_counts):
        return (
            "Keep this result tentative and check the limited-review courses before changing your schedule."
        )

    level = result["risk_level"]

    labels = [
        ("project_heavy", "project"),
        ("exam_heavy", "exam"),
        ("homework_heavy", "homework"),
        ("time_consuming", "time-consuming"),
    ]

    overlaps = []

    for key, display_name in labels:
        matching_courses = [
            course["course_code"]
            for course in courses
            if course.get(key)
        ]

        if len(matching_courses) >= 2:
            overlaps.append((display_name, matching_courses))

    if overlaps:
        display_name, matching_courses = max(
            overlaps,
            key=lambda item: len(item[1]),
        )

        if level == "High":
            if display_name == "exam":
                return (
                    "If you can, swap one exam-heavy course for a lighter alternative. "
                    "If not, avoid adding another exam-heavy course and start exam prep early."
                )
            if display_name == "project":
                return (
                    "If you can, reduce one project-heavy course. "
                    "If not, start major projects early and avoid adding another project-heavy class."
                )
            if display_name == "homework":
                return (
                    "If you can, reduce one homework-heavy course. "
                    "If not, protect weekly work time and avoid adding another homework-heavy class."
                )
            return (
                "If you can, reduce one time-consuming course. "
                "If not, keep the rest of your schedule and outside commitments lighter."
            )

        if level == "Medium":
            if display_name == "exam":
                return (
                    "This schedule is workable, but avoid adding another exam-heavy course "
                    "and plan exam prep ahead of time."
                )
            if display_name == "project":
                return (
                    "This schedule is workable, but avoid adding another project-heavy course "
                    "and start major projects early."
                )
            if display_name == "homework":
                return (
                    "This schedule is workable, but avoid adding another homework-heavy course "
                    "and leave consistent weekly work time."
                )
            return (
                "This schedule is workable, but avoid adding another time-consuming course "
                "and keep some weekly buffer."
            )

    if level == "High":
        return "Consider replacing one of the heavier courses before adding anything else."
    if level == "Medium":
        return "Keep some weekly buffer and avoid adding another high-workload course."
    return "No schedule change stands out. Keep some weekly buffer for unexpected workload spikes."


COURSE_OPTIONS_CACHE_VERSION = 3

# Snapshot of the 109 course codes represented in the final project dataset.
# The app still tries to discover courses from data/ first; this is only a
# safe fallback so the selector never becomes empty because of a path/cache issue.
PROJECT_COURSE_FALLBACK = ['BSCI160', 'BSCI161', 'BSCI170', 'BSCI171', 'BSCI201', 'BSCI202', 'BSCI207', 'BSCI222', 'BSCI223', 'BSCI330', 'BSCI331', 'BSCI353', 'BSCI410', 'CHEM131', 'CHEM132', 'CHEM135', 'CHEM136', 'CHEM231', 'CHEM232', 'CHEM241', 'CHEM242', 'CHEM271', 'CHEM272', 'CMSC131', 'CMSC132', 'CMSC216', 'CMSC250', 'CMSC320', 'CMSC330', 'CMSC335', 'CMSC351', 'CMSC411', 'CMSC412', 'CMSC414', 'CMSC417', 'CMSC420', 'CMSC421', 'CMSC422', 'CMSC424', 'CMSC426', 'CMSC430', 'CMSC433', 'CMSC434', 'CMSC436', 'CMSC451', 'CMSC456', 'CMSC460', 'CMSC466', 'CMSC470', 'CMSC471', 'CMSC472', 'CMSC474', 'CMSC475', 'DATA100', 'DATA110', 'DATA120', 'DATA350', 'INST326', 'INST327', 'INST414', 'INST447', 'MATH140', 'MATH141', 'MATH240', 'MATH241', 'MATH246', 'MATH310', 'MATH401', 'MATH402', 'MATH403', 'MATH404', 'MATH405', 'MATH406', 'MATH410', 'MATH411', 'MATH416', 'MATH420', 'MATH424', 'MATH430', 'MATH431', 'MATH475', 'MSML601', 'MSML602', 'MSML603', 'MSML604', 'MSML605', 'MSML610', 'MSML640', 'PHYS121', 'PHYS122', 'PHYS131', 'PHYS132', 'PHYS141', 'PHYS142', 'PHYS260', 'PHYS261', 'PHYS270', 'PHYS271', 'PHYS371', 'PHYS401', 'PHYS402', 'PHYS410', 'PHYS411', 'STAT100', 'STAT400', 'STAT401', 'STAT410', 'STAT420', 'STAT430']

@st.cache_data
def load_course_options(cache_version):
    """Load every course code represented in TerpLoad's project data."""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    course_codes = set()

    # Scan every CSV in data/ recursively. Different project files use either
    # `course` or `course_id`, so support both instead of assuming one filename.
    if data_dir.exists():
        for csv_path in data_dir.rglob("*.csv"):
            try:
                with csv_path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    fieldnames = set(reader.fieldnames or [])
                    course_field = (
                        "course" if "course" in fieldnames
                        else "course_id" if "course_id" in fieldnames
                        else None
                    )
                    if not course_field:
                        continue

                    for row in reader:
                        course_code = str(row.get(course_field, "")).strip().upper()
                        if course_code:
                            course_codes.add(course_code)
            except Exception:
                continue

        # Also collect dictionary keys from JSON files that look like
        # course->profile/signal maps.
        for json_path in data_dir.rglob("*.json"):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    continue

                for key in payload.keys():
                    course_code = str(key).strip().upper()
                    if re.fullmatch(r"[A-Z]{3,5}\d{3}", course_code):
                        course_codes.add(course_code)
            except Exception:
                continue

    # Never leave the UI with an empty multiselect. These are the course codes
    # present in the final project snapshot used for Week 11 evaluation.
    if not course_codes:
        course_codes.update(PROJECT_COURSE_FALLBACK)

    return sorted(course_codes)


course_service = get_course_service(COURSE_SERVICE_CACHE_VERSION)

base_course_options = load_course_options(COURSE_OPTIONS_CACHE_VERSION)

# Read the current picker state without mutating it.
raw_picker_state = st.session_state.get("course_picker", [])

normalized_picker_state = list(
    dict.fromkeys(
        str(course).strip().upper()
        for course in raw_picker_state
        if str(course).strip()
    )
)

# New custom courses are kept PENDING while the user is actively editing.
# This is important: changing the multiselect's options while a custom value
# is still selected can make Streamlit drop/reset chips unexpectedly.
pending_course_options = set(
    st.session_state.get("pending_user_course_options", [])
)

base_option_set = set(base_course_options)

for course_code in normalized_picker_state:
    if (
        re.fullmatch(r"[A-Z]{3,5}\d{3}", course_code)
        and course_code not in base_option_set
    ):
        pending_course_options.add(course_code)

st.session_state["pending_user_course_options"] = sorted(
    pending_course_options
)

# Only promote learned custom courses into autocomplete AFTER the picker is
# empty. That way Backspace/X only removes the intended chip and never causes
# the options list to change underneath an active multiselect.
remembered_course_options = set(
    st.session_state.get("user_added_course_options", [])
)

if not raw_picker_state and pending_course_options:
    remembered_course_options.update(pending_course_options)
    st.session_state["user_added_course_options"] = sorted(
        remembered_course_options
    )
    st.session_state["pending_user_course_options"] = []
else:
    st.session_state["user_added_course_options"] = sorted(
        remembered_course_options
    )

course_options = sorted(
    base_option_set | remembered_course_options
)


def submit_schedule():
    """Persist the selected schedule before Streamlit performs its normal rerun."""
    selected = st.session_state.get("course_picker", [])

    course_codes = list(
        dict.fromkeys(
            str(course).strip().upper()
            for course in selected
            if str(course).strip()
        )
    )

    if not 1 <= len(course_codes) <= 6:
        st.session_state["schedule_submit_error"] = (
            "Enter between 1 and 6 courses for a schedule analysis."
        )
        return

    st.session_state["submitted_course_codes"] = course_codes
    st.session_state.pop("grade_context_course", None)
    st.session_state.pop("schedule_submit_error", None)


# If the user edits a schedule that already has a report, invalidate only
# the REPORT. Never rewrite or clear the multiselect selection itself.
submitted_schedule = st.session_state.get("submitted_course_codes")

if submitted_schedule and normalized_picker_state != submitted_schedule:
    st.session_state.pop("submitted_course_codes", None)
    st.session_state.pop("grade_context_course", None)
    st.session_state.pop("schedule_submit_error", None)


# Before a schedule is submitted, add vertical space so the hero sits
# around the middle of the viewport. After submit, remove the spacer so the
# title + search form move to the top and the report appears directly below.
has_submitted_schedule = bool(
    st.session_state.get("submitted_course_codes")
)

st.markdown(
    """
    <style>
    div[data-testid="stMainBlockContainer"] {
        max-width: 1120px !important;
        padding-top: 0.75rem !important;
    }

    .landing-spacer {
        height: calc(50vh - 165px);
        min-height: 180px;
        max-height: 360px;
    }

    .terpload-title {
        margin-top: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not has_submitted_schedule:
    st.markdown(
        '<div class="landing-spacer"></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="terpload-title">TERPLOAD</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="terpload-subtitle">Understand your workload and risks for the semester</div>',
    unsafe_allow_html=True,
)

# Center the SEARCH BAR itself on the page.
# Use equal-width side columns so the red submit button does not shift the
# visual center of the selector. The title/subtitle are already page-centered,
# so they now sit exactly over the midpoint of the search box.
outer_left, outer_center, outer_right = st.columns(
    [0.2, 9.6, 0.2],
    gap="small",
)

with outer_center:
    left_balance, picker_col, button_col = st.columns(
        [1.15, 9.25, 1.15],
        gap="medium",
        vertical_alignment="center",
    )

    with picker_col:
        st.markdown(
            '<div style="color:#bdb7b2;font-size:0.82rem;margin:0 0 0.45rem 0.15rem;">'
            'Select your courses'
            '</div>',
            unsafe_allow_html=True,
        )

        picked = st.multiselect(
            "Courses",
            options=course_options,
            placeholder="Search a course code",
            label_visibility="collapsed",
            help=(
                "Select 1-6 courses. You can also type a course code "
                "that is not already listed."
            ),
            max_selections=6,
            accept_new_options=True,
            key="course_picker",
        )

    with button_col:
        # Small top spacer aligns the circular button vertically with the search
        # box rather than with the "Select your courses" label above it.
        st.markdown('<div style="height:1.45rem;"></div>', unsafe_allow_html=True)
        st.button(
            "↑",
            type="primary",
            use_container_width=True,
            disabled=not picked,
            on_click=submit_schedule,
            key="analyze_schedule_button",
        )

entered_course_codes = list(
    dict.fromkeys(
        str(course).strip().upper()
        for course in picked
        if str(course).strip()
    )
)

submit_error = st.session_state.get("schedule_submit_error")
if submit_error:
    st.error(submit_error)

course_codes = st.session_state.get("submitted_course_codes", [])

if course_codes:
    try:
        with st.spinner("Analyzing course reviews..."):
            course_signals = {
                course_code: course_service.get_profile(course_code)
                for course_code in course_codes
            }
    except SavedModelUnavailableError as error:
        st.error(str(error))
        st.stop()
    except Exception as error:
        st.error(f"Could not retrieve and analyze course reviews: {error}")
        st.stop()

    courses, courses_without_data = build_course_inputs(course_codes, course_signals)
    result = estimate_schedule_risk(courses)
    low_evidence_courses = get_low_evidence_courses(courses)
    confidence = compute_confidence(courses, courses_without_data)
    risk_level = result["risk_level"]
    shown_risk_level = display_risk_level(
        risk_level,
        courses,
        courses_without_data,
    )
    main_driver = main_driver_text(
        courses,
        courses_without_data,
    )

    st.markdown(
        f"""
        <div class="card">
          <div class="card-header">
            <span>SCHEDULE ANALYSIS REPORT</span>
            <span>{html.escape(" · ".join(course_codes))}</span>
          </div>
          <div class="card-body" style="display:flex; justify-content:space-between;">
            <div>
              <div class="eyebrow">OVERALL RISK</div>
              <span class="risk-pill {RISK_COLORS[shown_risk_level]}">{shown_risk_level.upper()}</span>
            </div>
            <div>
              <div class="eyebrow">CONFIDENCE</div>
              <span class="confidence-text {confidence.lower()}">{confidence.upper()}</span>
            </div>
          </div>
          <div class="main-driver">
            <span class="main-driver-label">MAIN DRIVER</span>
            {html.escape(main_driver)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">
          <div class="card-header"><span>BEST MOVE</span></div>
          <div class="card-body">
            <div class="advice-box">{html.escape(best_move_text(result, courses_without_data, courses))}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    known_selected = [
        c for c in courses
        if c["course_code"] in course_signals
    ]

    if known_selected:
        # Workload signals
        rows_html = ""

        display_names = {
            "project_heavy": "PROJECT-HEAVY",
            "exam_heavy": "EXAM-HEAVY",
            "homework_heavy": "HOMEWORK-HEAVY",
            "time_consuming": "TIME-CONSUMING",
        }


        for c in known_selected:
            course_code = c["course_code"]
            active_labels = [
                label for label in WORKLOAD_LABELS
                if c.get(label)
            ]

            review_count = c.get("review_count", 0)

            if review_count == 0:
                signal_items_html = '<span class="tag muted">NO COURSE REVIEWS</span>'
                review_text = "No course-specific reviews"
                instructor_context_html = (
                    f'<a class="evidence-link" '
                    f'href="https://planetterp.com/course/{html.escape(course_code)}" '
                    'target="_blank" rel="noopener noreferrer">'
                    'See instructor reviews ↗</a>'
                    '<span style="color:#8a8a8a;font-size:0.72rem;margin-left:0.55rem;">'
                    '· Ask professor for syllabus'
                    '</span>'
                )
            elif active_labels:
                # COURSE WORKLOAD SIGNALS always shows the actual course-level
                # labels produced by full-review model aggregation.
                signal_items_html = "".join(
                    (
                        '<span class="signal-item">'
                        f'<span class="tag">{html.escape(display_names[label])}</span>'
                        f'<span class="signal-percent">'
                        f'{round(c.get(f"{label}_positive_rate", 0) * 100)}%'
                        '</span>'
                        '</span>'
                    )
                    for label in active_labels
                )
                review_text = f"{review_count} reviews"
                if review_count < 10:
                    review_text += " · Limited data"
                instructor_context_html = ""
            elif c.get("low_evidence"):
                signal_items_html = '<span class="tag muted">LIMITED DATA</span>'
                review_text = f"{review_count} reviews"
                instructor_context_html = ""
            else:
                signal_items_html = '<span class="tag muted">NO DOMINANT WORKLOAD SIGNAL</span>'
                review_text = f"{review_count} reviews"
                instructor_context_html = ""

            rows_html += (
                '<div class="signal-row">'
                '<div class="signal-line">'
                f'<span class="signal-course">{html.escape(course_code)}</span>'
                '<div class="signal-items">'
                f'{signal_items_html}{instructor_context_html}'
                '</div>'
                f'<span class="signal-review-count">{html.escape(review_text)}</span>'
                '</div>'
                '</div>'
            )

        workload_card_html = (
            '<div class="card">'
            '<div class="card-header">'
            '<span>COURSE WORKLOAD SIGNALS</span>'
            '</div>'
            f'{rows_html}'
            '<div class="signal-detail" '
            'style="padding:0.3rem 1.15rem 0.8rem;color:#8a8a8a;font-size:0.72rem;">'
            'Percentages can overlap because one review may fit more than one category.'
            '</div>'
            '</div>'
        )

        st.markdown(
            workload_card_html,
            unsafe_allow_html=True,
        )

        # WHY THESE SIGNALS?
        # Evidence excerpts are always visible.
        # Professor context is open by default per course and can be collapsed
        # independently under each course.
        evidence_html = ""

        evidence_names = {
            "project_heavy": "PROJECT EVIDENCE",
            "exam_heavy": "EXAM EVIDENCE",
            "homework_heavy": "HOMEWORK EVIDENCE",
            "time_consuming": "TIME EVIDENCE",
        }

        for c in known_selected:
            course_code = c["course_code"]
            items = c.get("evidence_snippets", [])

            clean_items = [
                item for item in items
                if isinstance(item, dict)
                and item.get("excerpt")
                and item.get("matched_labels")
            ]

            if not clean_items:
                continue

            representative_only = all(
                str(item.get("evidence_scope", "")).startswith("representative")
                for item in clean_items
            )

            source_url = clean_items[0].get(
                "source_url",
                f"https://planetterp.com/course/{course_code}/reviews",
            )
            safe_url = html.escape(source_url, quote=True)

            professors = load_professor_context(
                course_code,
                start_year=2024,
                end_year=2026,
                cache_version=PROFESSOR_CONTEXT_CACHE_VERSION,
            )

            # Representative/below-threshold labels remain only where needed.
            tag_html = ""
            representative_note_html = ""

            if representative_only:
                course_labels = []
                for item in clean_items:
                    for label in item.get("matched_labels") or []:
                        if label not in course_labels:
                            course_labels.append(label)

                has_fallback_excerpt = any(
                    item.get("evidence_scope") == "representative_fallback"
                    for item in clean_items
                )

                below_threshold_labels = []

                if not has_fallback_excerpt:
                    below_threshold_labels = [
                        label
                        for label in course_labels
                        if (
                            0.0
                            < float(c.get(f"{label}_positive_rate", 0.0))
                            < POSITIVE_LABEL_THRESHOLD
                        )
                    ]

                if below_threshold_labels:
                    tag_html = "".join(
                        (
                            '<span class="tag muted">'
                            f'{html.escape(evidence_names.get(label, "WORKLOAD EVIDENCE"))} '
                            '· BELOW 30%'
                            '</span>'
                        )
                        for label in below_threshold_labels
                    )
                    representative_note_html = (
                        '<div class="signal-detail" '
                        'style="margin:-0.12rem 0 0.28rem 0;'
                        'color:#8a8a8a;font-size:0.72rem;">'
                        'Evidence found, but this workload type did not reach the '
                        '30% course threshold. No risk impact.'
                        '</div>'
                    )
                else:
                    tag_html = '<span class="tag muted">REPRESENTATIVE REVIEW</span>'
                    representative_note_html = (
                        '<div class="signal-detail" '
                        'style="margin:-0.12rem 0 0.28rem 0;'
                        'color:#8a8a8a;font-size:0.72rem;">'
                        'Representative excerpt only · no workload category reached '
                        'the 30% course threshold. No risk impact.'
                        '</div>'
                    )

            quote_items = (
                clean_items[:1]
                if representative_only
                else clean_items
            )

            quotes_html = ""

            for index, item in enumerate(quote_items):
                excerpt = html.escape(item.get("excerpt", ""))

                review_link = (
                    f'<a class="course-evidence-course-link" href="{safe_url}" '
                    'target="_blank" rel="noopener noreferrer">Course reviews ↗</a>'
                    if index == 0
                    else ""
                )

                quotes_html += (
                    '<div class="course-evidence-excerpt-row">'
                    '<div class="evidence-quote">'
                    f'“{excerpt}”'
                    '</div>'
                    f'{review_link}'
                    '</div>'
                )

            professor_rows_html = ""

            for professor in professors:
                professor_name = html.escape(professor["name"])
                professor_url = html.escape(
                    professor["planetterp_url"],
                    quote=True,
                )
                professor_rating = professor["average_rating"]

                professor_rows_html += (
                    f'<a class="course-professor-row" href="{professor_url}" '
                    'target="_blank" rel="noopener noreferrer">'
                    f'<span class="course-professor-name">{professor_name}</span>'
                    f'<span class="course-professor-rating">{professor_rating:.2f} / 5</span>'
                    '</a>'
                )

            professor_context_html = ""

            if professor_rows_html:
                professor_context_html = (
                    '<details class="course-professor-details" open="open">'
                    '<summary class="course-professor-summary">'
                    'Professor context'
                    '</summary>'
                    '<div class="course-professor-list">'
                    f'{professor_rows_html}'
                    '</div>'
                    '</details>'
                )

            evidence_html += (
                '<div class="course-evidence-block">'
                '<div class="course-evidence-head">'
                '<span>'
                f'<span class="course-evidence-code">{html.escape(course_code)}</span>'
                f'{tag_html}'
                '</span>'
                '</div>'
                f'{quotes_html}'
                f'{representative_note_html}'
                f'{professor_context_html}'
                '</div>'
            )

        if evidence_html:
            st.markdown(
                (
                    '<div class="why-signals-card">'
                    '<div class="why-signals-header">'
                    '<span>WHY THESE SIGNALS?</span>'
                    '</div>'
                    '<div class="why-signals-content">'
                    f'{evidence_html}'
                    '</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        # Historical grade context — keep every searched course selectable.
        grade_contexts = {}

        for c in known_selected:
            course_code = c["course_code"]
            grade_contexts[course_code] = load_grade_context(
                course_code,
                GRADE_CONTEXT_CACHE_VERSION,
            )

        if known_selected:
            st.markdown("### Historical Grade Context")

            grade_course_options = [
                c["course_code"]
                for c in known_selected
            ]

            selected_grade_course = st.segmented_control(
                "View course",
                options=grade_course_options,
                default=grade_course_options[0],
                key="grade_context_course",
                label_visibility="collapsed",
            )

            selected_grade_context = grade_contexts.get(
                selected_grade_course
            )

            if selected_grade_context:
                grade_labels = ["A", "B", "C", "D", "F", "W"]
                grade_values = [
                    selected_grade_context["a_range_rate"] * 100,
                    selected_grade_context["b_range_rate"] * 100,
                    selected_grade_context["c_range_rate"] * 100,
                    selected_grade_context["d_range_rate"] * 100,
                    selected_grade_context["f_rate"] * 100,
                    selected_grade_context["withdrawal_rate"] * 100,
                ]

                chart_top = min(100, max(grade_values) * 1.25 + 5)

                fig = go.Figure(
                    go.Bar(
                        x=grade_labels,
                        y=grade_values,
                        text=[f"{value:.0f}%" for value in grade_values],
                        textposition="outside",
                        marker_color="#FF4D4D",
                        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
                    )
                )

                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    yaxis=dict(range=[0, chart_top], showgrid=True),
                    showlegend=False,
                    height=300,
                    margin=dict(l=35, r=15, t=20, b=35),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

                source_course = selected_grade_context.get(
                    "grade_source_course_code",
                    selected_grade_course,
                )
                used_crosslist = selected_grade_context.get(
                    "used_crosslist_fallback",
                    False,
                )

                source_note = (
                    f" · using {source_course} records"
                    if used_crosslist
                    else ""
                )

                st.caption(
                    f"{selected_grade_context['total_grade_records']:,} historical outcomes"
                    f"{source_note}. Grades are context only."
                )
            else:
                st.info(
                    f"No historical grade data available for {selected_grade_course}."
                )

elif not entered_course_codes:
    st.markdown(
        '<div style="text-align:center;color:#aaa;font-size:0.82rem;margin-top:0.55rem;">'
        'Pick 1-6 courses to get a report.'
        '</div>',
        unsafe_allow_html=True,
    )
