"""
fetches data from planetterp

"""
import requests
from grade_context import aggregate_grade_rows

BASE_URL = "https://planetterp.com/api/v1"

def normalize_course_code(course_code):
    return (
        course_code
        .replace(" ", "")
        .replace("-", "")
        .strip()
        .upper()
    )
def fetch_grades(course_code):
    course_code = normalize_course_code(course_code)

    response = requests.get(
        f"{BASE_URL}/grades",
        params={"course": course_code},
        timeout=15,
    )

    response.raise_for_status()

    return response.json()
  
def get_grade_context(course_code):
    grade_rows = fetch_grades(course_code)
    return aggregate_grade_rows(grade_rows)