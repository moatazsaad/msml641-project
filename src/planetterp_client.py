"""
fetches data from planetterp

"""
import requests


BASE_URL = "https://planetterp.com/api/v1"

def normalize_course_code(course_code):
    return (
        course_code
        .replace(" ", "")
        .replace("-", "")
        .strip()
        .upper()
    )
