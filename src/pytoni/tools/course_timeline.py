import requests

from pytoni.config import get_settings


def get_calendar() -> str:
    """
    Fetches the calendar of the course, containing all dates relevant to the course.
    Lecture days, homework and project deadlines.
    """
    response = requests.get(f"{get_settings().course_db_url}/calendar")
    response.raise_for_status()

    return response.text.strip()
