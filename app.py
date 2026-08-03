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

import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from risk_rules import estimate_schedule_risk  # noqa: E402
from simple_report_cli import (  # noqa: E402
    build_course_inputs,
    get_low_evidence_courses,
    load_course_signals,
)
from workload_labels import WORKLOAD_LABELS  # noqa: E402

st.set_page_config(page_title="TerpLoad", page_icon="📚", layout="centered")

LABELED_DATA_PATHS = [
    "data/weakly-labeled-week08.csv",
    "data/weakly-labeled-week10.csv",
]

RISK_COLORS = {"Low": "low", "Medium": "medium", "High": "high"}

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
    div[data-baseweb="select"] > div {
        background-color: #fdfbf5 !important;
        border-radius: 999px !important;
        border: 1px solid #d8b04a !important;
    }
    .card {
        background: #ffffff;
        color: #1a1a1a;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 1rem;
        border: 1px solid #2a2a2a;
    }
    .card-header {
        background: #a3132e;
        color: white;
        padding: 0.55rem 1rem;
        font-weight: 700;
        letter-spacing: 1px;
        font-size: 0.8rem;
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
    .risk-pill.high { background: #a3132e; }
    .risk-pill.medium { background: #b8860b; }
    .risk-pill.low { background: #2e7d32; }
    .confidence-text { font-weight: 700; font-size: 0.9rem; }
    .confidence-text.high { color: #2e7d32; }
    .confidence-text.medium { color: #b8860b; }
    .confidence-text.low { color: #a3132e; }
    .eyebrow { font-size: 0.7rem; color: #777; letter-spacing: 1px; }
    .advice-box {
        background: #e6f3fb;
        border-radius: 6px;
        padding: 0.7rem 1rem;
        margin: 0 0 0.9rem 0;
    }
    .warning-box {
        background: #fbe6ea;
        border-left: 4px solid #a3132e;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        margin-top: 0.9rem;
    }
    .reasoning-bar {
        background: #3a3a3a;
        color: #ddd;
        padding: 0.35rem 1.2rem;
        font-size: 0.7rem;
        letter-spacing: 1px;
    }
    .signal-row {
        padding: 0.6rem 1.2rem;
        border-top: 1px solid #eee;
    }
    .signal-course { font-weight: 700; }
    .tag {
        display: inline-block;
        background: #eee;
        border-radius: 999px;
        padding: 0.05rem 0.6rem;
        font-size: 0.7rem;
        font-weight: 700;
        margin-left: 0.5rem;
        color: #444;
    }
    .signal-detail { font-size: 0.85rem; color: #555; margin-top: 0.15rem; }
    .evidence-quote {
        border-left: 3px solid #a3132e;
        padding: 0.3rem 0.9rem;
        margin: 0.6rem 1.2rem;
        font-style: italic;
        color: #333;
    }
    .evidence-source { font-size: 0.72rem; color: #888; margin: -0.3rem 1.2rem 0.6rem 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_evidence_quotes():
    """Real quoted excerpts from labeled reviews, keyed by course code.

    Only uses evidence_snippet (an actual quote from the review text) -
    never label_rationale, which is our own note about *why* we labeled
    it that way, not something the student wrote.
    """
    frames = [pd.read_csv(path) for path in LABELED_DATA_PATHS]
    labeled = pd.concat(frames, ignore_index=True)

    quotes = {}
    for _, row in labeled.iterrows():
        snippet = str(row.get("evidence_snippet", "")).strip()
        if not snippet or snippet.lower() == "nan":
            continue
        quotes.setdefault(row["course"], []).append(snippet)
    return quotes


def compute_confidence(courses, courses_without_data):
    """Simple, real-data-based confidence label - not a trained score."""
    if courses_without_data:
        return "Low"
    if any(c.get("low_evidence") for c in courses):
        return "Low"
    if any(c.get("review_count", 0) < 30 for c in courses):
        return "Medium"
    return "High"


def best_move_text(result, courses_without_data):
    """Template advice built from the real risk result - no invented claims."""
    if courses_without_data:
        return (
            "No review data yet for "
            + ", ".join(courses_without_data)
            + " - check another source before deciding."
        )
    level = result["risk_level"]
    if level == "High":
        return "Risky combination based on review data. Avoid adding another heavy course, and start major assignments early."
    if level == "Medium":
        return "Doable, but plan ahead - start major work early and watch for overlapping deadlines."
    return "Looks manageable based on the review data we have."


course_signals = load_course_signals()
known_courses = sorted(course_signals.keys())
evidence_quotes = load_evidence_quotes()

st.markdown('<div class="terpload-title">TERPLOAD</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="terpload-subtitle">Understand your workload and risks for the semester</div>',
    unsafe_allow_html=True,
)

st.caption("Select your courses")
picker_col, button_col = st.columns([5, 1])
with picker_col:
    picked = st.multiselect(
        "Courses",
        options=known_courses,
        default=[],
        label_visibility="collapsed",
        help="Courses we have real review data for.",
    )
with button_col:
    run = st.button("↑", type="primary", use_container_width=True, disabled=not picked)

extra_text = st.text_input(
    "Other course codes (comma-separated, no review data yet)",
    placeholder="e.g. MATH410",
)
extra_courses = [c.strip().upper() for c in extra_text.split(",") if c.strip()]
course_codes = picked + [c for c in extra_courses if c not in picked]

if (run or extra_courses) and course_codes:
    courses, courses_without_data = build_course_inputs(course_codes, course_signals)
    result = estimate_schedule_risk(courses)
    low_evidence_courses = get_low_evidence_courses(courses)
    confidence = compute_confidence(courses, courses_without_data)
    risk_level = result["risk_level"]

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
              <span class="risk-pill {RISK_COLORS[risk_level]}">{risk_level.upper()}</span>
            </div>
            <div>
              <div class="eyebrow">CONFIDENCE</div>
              <span class="confidence-text {confidence.lower()}">{confidence.upper()}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reasons_html = (
        "<br>".join(html.escape(r) for r in result["reasons"])
        if result["reasons"]
        else "No major workload-risk signals found from the collected review data."
    )
    warning_html = ""
    if low_evidence_courses:
        lines = "<br>".join(
            f"{html.escape(code)}: based on only {count} review(s) - treat as a rough guess"
            for code, count in low_evidence_courses
        )
        warning_html = f'<div class="warning-box"><b>LIMITED EVIDENCE</b><br>{lines}</div>'

    st.markdown(
        f"""
        <div class="card">
          <div class="card-header"><span>BEST MOVE</span></div>
          <div class="card-body">
            <div class="advice-box">{html.escape(best_move_text(result, courses_without_data))}</div>
          </div>
          <div class="reasoning-bar">REASONING</div>
          <div class="card-body">{reasons_html}{warning_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    known_selected = [c for c in courses if c["course_code"] in course_signals]
    if known_selected:
        rows_html = ""
        for c in known_selected:
            active_labels = [label for label in WORKLOAD_LABELS if c.get(label)]
            tag_html = "".join(f'<span class="tag">{label.replace("_", "-").upper()}</span>' for label in active_labels)
            detail_bits = [
                f"{round(c.get(f'{label}_positive_rate', 0) * 100)}% of reviews mention {label.replace('_', ' ')}"
                for label in active_labels
            ]
            detail = " · ".join(detail_bits) if detail_bits else "No strong workload signals in the reviews we have"
            rows_html += f"""
            <div class="signal-row">
              <span class="signal-course">{html.escape(c['course_code'])}</span>{tag_html}
              <div class="signal-detail">{html.escape(detail)} ({c.get('review_count', 0)} reviews)</div>
            </div>
            """

        st.markdown(
            f"""
            <div class="card">
              <div class="card-header"><span>COURSE WORKLOAD SIGNALS</span></div>
              {rows_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        evidence_html = ""
        for c in known_selected:
            course_code = c["course_code"]
            for quote in evidence_quotes.get(course_code, [])[:2]:
                evidence_html += (
                    f'<div class="evidence-quote">"{html.escape(quote)}"</div>'
                    f'<div class="evidence-source">{html.escape(course_code)}</div>'
                )

        if evidence_html:
            st.markdown(
                f"""
                <div class="card">
                  <div class="card-header"><span>EVIDENCE</span></div>
                  {evidence_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

elif not course_codes:
    st.caption("Pick at least one course to get a report.")
