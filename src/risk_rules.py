"""
Simple baseline risk rules for TerpLoad.

It is a baseline that uses the four
first-version workload labels to estimate schedule risk.
"""


def estimate_schedule_risk(courses):
    risk_score = 0
    reasons = []

    if len(courses) >= 4:
        risk_score += 1
        reasons.append("The schedule includes four or more courses.")

    project_heavy_count = 0
    exam_heavy_count = 0
    homework_heavy_count = 0
    time_consuming_count = 0

    for course in courses:
        code = course.get("course_code", "Unknown course")

        if course.get("project_heavy"):
            risk_score += 2
            project_heavy_count += 1
            reasons.append(f"{code} may have heavy project workload.")

        if course.get("exam_heavy"):
            risk_score += 2
            exam_heavy_count += 1
            reasons.append(f"{code} may have heavy exam pressure.")

        if course.get("homework_heavy"):
            risk_score += 1
            homework_heavy_count += 1
            reasons.append(f"{code} may have heavy homework workload.")

        if course.get("time_consuming"):
            risk_score += 2
            time_consuming_count += 1
            reasons.append(f"{code} may require high weekly time commitment.")

    if project_heavy_count >= 2:
        risk_score += 2
        reasons.append("Multiple project-heavy courses may stack badly.")

    if exam_heavy_count >= 2:
        risk_score += 2
        reasons.append("Multiple exam-heavy courses may increase pressure.")

    if homework_heavy_count >= 2:
        risk_score += 1
        reasons.append("Multiple homework-heavy courses may increase weekly workload.")

    if time_consuming_count >= 2:
        risk_score += 2
        reasons.append("Multiple time-consuming courses may make the semester harder to manage.")

    if risk_score >= 8:
        risk_level = "High"
    elif risk_score >= 4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "reasons": reasons,
    }


if __name__ == "__main__":
    sample_schedule = [
        {
            "course_code": "CMSC330",
            "project_heavy": True,
            "exam_heavy": False,
            "homework_heavy": False,
            "time_consuming": True,
        },
        {
            "course_code": "CMSC351",
            "project_heavy": False,
            "exam_heavy": True,
            "homework_heavy": True,
            "time_consuming": True,
        },
        {
            "course_code": "STAT400",
            "project_heavy": False,
            "exam_heavy": True,
            "homework_heavy": False,
            "time_consuming": False,
        },
    ]

    result = estimate_schedule_risk(sample_schedule)
    print(result)