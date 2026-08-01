"""
TerpLoad - Streamlit demo

This is a display layer only. It reuses the exact same functions the CLI
(src/simple_report_cli.py) uses - no risk logic lives here, so the web
version and the CLI version can never disagree.
"""

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

RISK_STYLE = {
    "Low": st.success,
    "Medium": st.warning,
    "High": st.error,
}

st.title("📚 TerpLoad")
st.caption("Will your planned semester be too much? A workload-risk check built from real UMD course reviews.")

course_signals = load_course_signals()
known_courses = sorted(course_signals.keys())

st.subheader("Pick your planned courses")

col1, col2 = st.columns(2)
with col1:
    picked = st.multiselect(
        "Courses we have review data for",
        options=known_courses,
        default=[],
        help="Selecting from this list uses real, review-based workload signals.",
    )
with col2:
    extra_text = st.text_input(
        "Other course codes (comma-separated)",
        placeholder="e.g. MATH410",
        help="Any course not in the list on the left. We'll say honestly if we have no data for it.",
    )

extra_courses = [c.strip().upper() for c in extra_text.split(",") if c.strip()]
course_codes = picked + [c for c in extra_courses if c not in picked]

run = st.button("Check my schedule risk", type="primary", disabled=not course_codes)

if run and course_codes:
    courses, courses_without_data = build_course_inputs(course_codes, course_signals)
    result = estimate_schedule_risk(courses)
    low_evidence_courses = get_low_evidence_courses(courses)

    st.divider()
    st.subheader("Result")

    risk_level = result["risk_level"]
    RISK_STYLE[risk_level](f"**{risk_level} risk**  —  risk score {result['risk_score']}")

    st.markdown("**Why:**")
    if result["reasons"]:
        for reason in result["reasons"]:
            st.markdown(f"- {reason}")
    else:
        st.markdown("- No major workload-risk signals found from the collected review data.")

    if courses_without_data:
        st.info(f"No review data yet for: {', '.join(courses_without_data)}")

    if low_evidence_courses:
        warning_lines = "\n".join(
            f"- **{code}**: based on only {count} review(s) — treat as a rough guess, not a fact"
            for code, count in low_evidence_courses
        )
        st.warning("**Limited evidence:**\n" + warning_lines)

    known_selected = [c for c in courses if c["course_code"] in course_signals]
    if known_selected:
        st.markdown("**Course-by-course evidence**")
        table = pd.DataFrame(
            [
                {
                    "Course": c["course_code"],
                    "Reviews": c.get("review_count", 0),
                    **{label: ("Yes" if c.get(label) else "") for label in WORKLOAD_LABELS},
                }
                for c in known_selected
            ]
        )
        st.dataframe(table, hide_index=True, use_container_width=True)

    st.caption(
        "Workload signals come from a TF-IDF model trained on a small, weakly-labeled "
        "review sample. This is a prototype for user testing, not a validated accuracy claim."
    )
elif not course_codes:
    st.caption("Pick at least one course to get a report.")
