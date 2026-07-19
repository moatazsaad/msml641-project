from risk_rules import estimate_schedule_risk

# Prototype sample labels for testing the report flow
SAMPLE_COURSE_SIGNALS = {
    "CMSC330": {
        "course_code": "CMSC330",
        "project_heavy": True,
        "exam_heavy": False,
        "homework_heavy": True,
        "time_consuming": True,
    },
    "CMSC351": {
        "course_code": "CMSC351",
        "project_heavy": False,
        "exam_heavy": True,
        "homework_heavy": True,
        "time_consuming": True,
    },
    "CMSC216": {
        "course_code": "CMSC216",
        "project_heavy": True,
        "exam_heavy": True,
        "homework_heavy": False,
        "time_consuming": True,
    },
    "STAT400": {
        "course_code": "STAT400",
        "project_heavy": False,
        "exam_heavy": True,
        "homework_heavy": True,
        "time_consuming": False,
    },
    "MATH410": {
        "course_code": "MATH410",
        "project_heavy": False,
        "exam_heavy": True,
        "homework_heavy": True,
        "time_consuming": True,
    },
}


def parse_courses(user_input):
    return [
        course.strip().upper()
        for course in user_input.split(",")
        if course.strip()
    ]


def build_course_inputs(course_codes):
    courses = []

    for course_code in course_codes:
        if course_code in SAMPLE_COURSE_SIGNALS:
            courses.append(SAMPLE_COURSE_SIGNALS[course_code])
        else:
            # Unknown courses stay in the report but have no workload signals yet.
            courses.append({"course_code": course_code})

    return courses


def print_report(course_codes, result):
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
        print("- No major workload-risk signals found from the current sample data")

    print("\nNote:")
    print("This is a prototype for user testing, not the final trained model")


def main():
    print("TerpLoad Simple Report CLI")
    print("Enter 3-5 planned courses separated by commas")
    print("Example: CMSC330, CMSC351, STAT400\n")

    user_input = input("Courses: ")
    course_codes = parse_courses(user_input)

    if not course_codes:
        print("No courses entered")
        return

    courses = build_course_inputs(course_codes)
    result = estimate_schedule_risk(courses)

    print_report(course_codes, result)


if __name__ == "__main__":
    main()