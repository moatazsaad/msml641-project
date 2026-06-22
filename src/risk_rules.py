"""
Simple baseline risk rules for TerpLoad.

This is not the final NLP model. It is a baseline that uses workload signals
to estimate schedule risk. Later, the NLP model can predict these signals
from course review text.
"""


def estimate_schedule_risk(courses):
    risk_score = 0
    reasons = []
    uncertainty_flags = []

    if len(courses) >= 4:
        risk_score += 1
        reasons.append("The schedule includes four or more courses.")

    project_heavy_count = 0
    exam_heavy_count = 0

    for course in courses:
        code = course.get("course_code", "Unknown course")

        if course.get("project_heavy"):
            risk_score += 2
            project_heavy_count += 1
            reasons.append(f"{code} may have heavy project workload.")

        if course.get("exam_heavy"):
            risk_score += 1
            exam_heavy_count += 1
            reasons.append(f"{code} may have difficult exams.")

        if course.get("lab_heavy"):
            risk_score += 1
            reasons.append(f"{code} may have lab workload.")

        if course.get("writing_heavy"):
            risk_score += 1
            reasons.append(f"{code} may have writing workload.")

        if course.get("estimated_hours_per_week", 0) >= 8:
            risk_score += 2
            reasons.append(f"{code} may require high weekly time commitment.")

        if course.get("professor_unclear"):
            uncertainty_flags.append(
                f"{code} has professor or course-structure uncertainty."
            )

    if project_heavy_count >= 2:
        risk_score += 2
        reasons.append("Multiple project-heavy courses may stack badly.")

    if exam_heavy_count >= 2:
        risk_score += 1
        reasons.append("Multiple exam-heavy courses may increase pressure.")

    if risk_score >= 8:
        risk_level = "High"
    elif risk_score >= 4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if len(uncertainty_flags) >= 2:
        confidence = "Low"
    elif len(uncertainty_flags) == 1:
        confidence = "Medium"
    else:
        confidence = "High"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "confidence": confidence,
        "reasons": reasons,
        "uncertainty_flags": uncertainty_flags,
    }


if __name__ == "__main__":
    sample_schedule = [
        {
            "course_code": "CMSC330",
            "project_heavy": True,
            "exam_heavy": True,
            "lab_heavy": False,
            "writing_heavy": False,
            "estimated_hours_per_week": 9,
            "professor_unclear": False,
        },
        {
            "course_code": "CMSC351",
            "project_heavy": False,
            "exam_heavy": True,
            "lab_heavy": False,
            "writing_heavy": False,
            "estimated_hours_per_week": 8,
            "professor_unclear": False,
        },
        {
            "course_code": "STAT400",
            "project_heavy": False,
            "exam_heavy": True,
            "lab_heavy": False,
            "writing_heavy": False,
            "estimated_hours_per_week": 6,
            "professor_unclear": True,
        },
    ]

    result = estimate_schedule_risk(sample_schedule)
    print(result)