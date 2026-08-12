import json
from pathlib import Path

from risk_rules import estimate_schedule_risk

# Legacy TF-IDF data loader retained for the command-line prototype. The
# Streamlit application now uses CourseProfileService and saved DistilBERT
# inference for both locally cached and newly fetched courses.
COURSE_SIGNALS_PATH = Path("data/course_workload_signals.json")


def load_course_signals(path=COURSE_SIGNALS_PATH):
    """Load real, model-predicted workload signals for known courses."""

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_courses(user_input):
    return [
        course.strip().upper()
        for course in user_input.split(",")
        if course.strip()
    ]


def build_course_inputs(course_codes, course_signals):
    courses = []
    courses_without_data = []

    for course_code in course_codes:
        if course_code in course_signals:
            courses.append(course_signals[course_code])
        else:
            # Unknown courses stay in the report but have no workload signals yet.
            courses.append({"course_code": course_code})
            courses_without_data.append(course_code)

    return courses, courses_without_data


def get_low_evidence_courses(courses):
    """Return (course_code, review_count) for courses with too few reviews
    to trust their workload signals, instead of presenting thin data as fact."""

    return [
        (course["course_code"], course.get("review_count", 0))
        for course in courses
        if course.get("low_evidence")
    ]


def print_report(course_codes, result, courses_without_data, low_evidence_courses):
    print("\nTerpLoad Prototype Report")
    print("-------------------------")
    print("Selected courses:", ", ".join(course_codes))
    print("Risk level:", result["risk_level"])
    print("Risk score:", result["risk_score"])

    print("\nReasons:")
    if result["reasons"]:
        for reason in result["reasons"]:
            print(f"- {reason}")
    else:
        print("- No major workload-risk signals found from the collected review data")

    if courses_without_data:
        print("\nNo review data yet for:", ", ".join(courses_without_data))

    if low_evidence_courses:
        print("\nLimited evidence (treat these signals as a rough guess, not a fact):")
        for course_code, review_count in low_evidence_courses:
            print(f"- {course_code}: based on only {review_count} review(s)")

    print("\nNote:")
    print("Workload signals come from a TF-IDF model trained on a small,")
    print("weakly-labeled review sample. This is a prototype for user")
    print("testing, not the final trained model.")


def main():
    print("TerpLoad Simple Report CLI")
    print("Enter 3-5 planned courses separated by commas")
    print("Example: CMSC330, CMSC351, STAT400\n")

    course_signals = load_course_signals()

    user_input = input("Courses: ")
    course_codes = parse_courses(user_input)

    if not course_codes:
        print("No courses entered")
        return

    courses, courses_without_data = build_course_inputs(
        course_codes, course_signals
    )
    result = estimate_schedule_risk(courses)
    low_evidence_courses = get_low_evidence_courses(courses)

    print_report(course_codes, result, courses_without_data, low_evidence_courses)


if __name__ == "__main__":
    main()
